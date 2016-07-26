from fabric.api import *
from fabric.contrib.files import append, exists
import requests
import pprint
import time
import json
import os
import sys
import re
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from inventory import conf

from inventory.utils import send_site_patch
from inventory.utils import get_resource
from inventory.utils import get_site_by_name
from inventory.utils import patch_resource
from inventory.utils import post_resource

env.user = conf.ssh_user
#allow ~/.ssh/config to be utilized
env.use_ssh_config = True

env.roledefs = {
    'local': ['wweblocal'],
    'dev': ['wwebdev2'],
    'prod': ['wweb3', 'wweb4'],
}
#list of servers for commands that only need 1 server
#from a given conf.environment
singles = {
    'dev': 'wwebdev2',
    'prod': 'wweb3',
    'local': 'wweblocal',
}

workhorses = {
    'dev': 'wwhdev1.int',
    'prod': 'wwh1.int',
    'local': 'wwhlocal',
}


@roles(conf.environment)
def add_site_dslm(sid):
    """This function connects to the target server and uses drush dslm to create a new site.

    :param sid: First 10 characters of a sha1 hash created from the mongo id

    """
    target = singles[conf.environment]
    print "running add_site_dslm: {0} @ {1}".format(sid, target)
    run("mkdir -p /wwwng/sitefiles/{0}/files".format(sid))
    opts = "--dslm-base=/data/code/dslm_base --strict=0"
    with cd("/data/releases"):
        run("mkdir {0}".format(sid))
        with cd(sid):
            run("drush dslm-new {0} {1} --current".format(sid, opts))
            with cd(sid):
                run("drush dslm-add-profile cu_fit-current {0}".format(opts))
                with cd("sites/default"):
                    run("rm -rf files;ln -s /wwwng/sitefiles/{0}/files".format(sid))
                    if not exists("/wwwng/sitefiles/{0}/tmp".format(sid)):
                        run("mkdir /wwwng/sitefiles/{0}/tmp".format(sid))
            run("ln -s ./{0} current".format(sid))
    with cd("/data/web"):
        run("ln -s /data/releases/{0}/current {0}".format(sid))


@roles(conf.environment)
def add_site_packages(sid, packages):
    """This function connects to the target server and uses drush dslm to create packages symlinks in .
    sites/all

    :param packages: dict element with keys custom and contrib
    :param sid: First 10 characters of a sha1 hash created from the mongo id

    """
    target = singles[conf.environment]
    print "running add_site_packages: {0} @ {1}".format(sid, target)

    opts = "--dslm-base=/data/code/dslm_base --strict=0"
    with cd("/data/releases/{}/current/sites/all".format(sid)):
        if "custom" in packages:
            run("drush dslm-add-custom {0} {1}".format(" ".join(packages["custom"]), opts))
        if "contrib" in packages:
            run("drush dslm-add-contrib {0} {1}".format(" ".join(packages["contrib"]), opts))


def site_install(sid, site, profile):
    """"connects to server and runs drush site-install

    :param sid: first 10 digits of sha1 hash created from mongo document id
    :param site: the name of the site
    :param target: the server the site is being installed on
    :param profile: the install profile being used
    """
    target = singles[conf.environment]
    print "running site_install: {0} ({1}) @ {2}".format(sid, site, target)
    with hide('everything'):
        with settings(host_string=target):
            with cd("/data/web/{0}".format(sid)):
                run("drush site-install -y {0} --site-name=\"{1}\"".format(profile, site))


def add_site_db(sid, site, pw):
    """This function connects to the target server and uses drush dslm to create a new site.

    :param site: The name of the site
    :param sid: hash of the side id created by eve/mongo
    :param pw: The hashed database password
    :param pool: poola or poolb

    """
    print "creating site db with user: {0} @ {1}".format(sid, site)
    with settings(host_string=singles[conf.environment]):
        run('mysql -e \'create database `{}`;\''.format(sid))
        

def add_site_user(sid, mail, role='site_owner'):
    """This function takes a site id, server, username, email address, and a lsit of roles. It connects to the target server and users drush user-create to add the user to the site. We don't need to set a password because LDAP handles authentication within the Drupal site.

    :param sid: hash of the site id created by mongo
    :param target: remote server address
    :param username: drupal username for new user
    :param mail: email address for new user
    :param roles: roles to be applied to new user

    """
    target = singles[conf.environment]
    print "add site user called"
    env.warn_only = True
    with settings(host_string=target):
        with cd("/data/web/{0}".format(sid)):
            run("drush cu-users-send-invite {0} '{1}'".format(mail, role))


@roles(conf.environment)
def set_site_perms(sid):
    """Corrects files directory issues with new sites

    """
    with hide('everything'):
        print "set_site_perms called"
        with cd("/data/web/{0}".format(sid)):
            run("chgrp -R lapurd sites/default")
            run("chmod -R 775 sites/default")


def get_site_by_sid(sid):
    """Takes the 10 char hash create from the mongo db and returns teh site object related to that hash

    :param sid: 10 char sha1 hash created from the mongo site id
    """
    print "looking up {} ...\n".format(sid)
    q = '?where={"sid": "%s"}' % sid
    data = get_resource("sites", q)
    if data:
        pprint.pprint(data)
        return data['_items'][0]


@roles(conf.environment)
def launch_site(sid):
    """Connects to web servers and creates symlinks with new site name then updates settings.php
    """
    #request full site data to get the etag
    site = get_site_by_sid(sid)
    if site:
        with cd("/data/web"):
            if "/" in site['path']:
                lead_path = "/".join(site['path'].split("/")[:-1])
                if not exists(site['path']):
                    run("mkdir -p {}".format(lead_path))

            #create a new symlink using site's updated path
            if not exists(site['path']):
                run("ln -s /data/releases/{0}/current {1}".format(sid, site['path']))
            #enter new site directory
            with cd("{0}".format(site['path'])):
                #enter sites/default
                with cd("sites/default"):
                    #update settings.php to allow redirect to prod path from sid
                    put("/tmp/{0}.settings.php".format(sid), "settings.php")

        #update site info to show the site has launched
        payload = {'status': 'launched'}
        url = "{0}{1}".format(conf.api_server, site['_links']['self']['href'])
        send_site_patch(url, payload, site['_etag'])


@hosts(workhorses[conf.environment])
def push_aliases():
    """
    SCP the rendered drush aliases to the workhorse server
    :return:
    """
    put("/data/code/inventory/fabfile/aliases.drushrc.php", "/home/dplagnt/.drush")


@hosts(singles[conf.environment])
def run_drush_cron(site):
    with settings(warn_only=True):
        if 'sid' in site:
            print "Running cron: {0}@{1} - {2}".format(site['sid'], singles[conf.environment], site['name'])
            with cd("/data/web/{0}".format(site['sid'])):
                task = run("drush cron")
            if task.failed:
                print "FAILED CRON: {0}@{1} - {2}".format(site['sid'], singles[conf.environment], site['name'])


def get_data_release_sites(host):
    with settings(host_string=host):
        with cd("/data/releases/"):
            sites = run("ls").split()
    return sites


def run_custom_cron(host, site):
    with settings(host_string=host, warn_only=True):
        path = "/data/releases/{0}/current".format(site)
        if exists(path):
            with cd(path):
                task = run("drush cron")
                if task.failed:
                    return task


@roles(conf.environment)
def push_settings(sid):
    """
    SCP the rendered drupal site settings files to web heads
    :return:
    """
    send_from = '/tmp/{0}'.format(sid)
    send_to = "/data/web/{0}/sites/default/".format(sid)
    run("chmod -R u+w {}".format(send_to))
    put("{0}.settings.php".format(send_from), "{0}settings.php".format(send_to))


@roles("dev")
def update_settings():
    with settings(warn_only=True):
        with cd("/data/releases"):
            sites = run("ls")
            p = re.compile('p1[a-zA-Z0-9_]+')
            sites = p.findall(sites)
            for s in sites:
                print s
                run("chmod -R 775 /data/releases/{0}".format(s))
                run("rm -rf /data/releases/{0}".format(s))