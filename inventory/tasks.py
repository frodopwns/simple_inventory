"""
    inventory.tasks
    ~~~~~~~~~

    Celery tasks for Inventory system.

"""

from time import time
from celery import Celery
from celery import group
from celery import chord
from celery.signals import worker_process_init

import Crypto
from jinja2 import Environment, PackageLoader
#add directory that contains project folder
from fabric.api import execute
import fabfile
from .utils import *

from . import conf


from . import celeryconfig

#tell jinja where our templates live
env = Environment(loader=PackageLoader('inventory', 'templates'))
#create the celery object
celery = Celery('tasks')
celery.config_from_object(celeryconfig)

@celery.task
def patching(url, data, etag):
    send_site_patch(url, data, etag)

@celery.task
def new_site(site_id):
    """Takes the url to the site in the api and gets its data before sending it off to fabric.

    :param url: link to where the site object lives in the eve api

    """
    #the status check may be unnecessary
    if site_id:
        #we have to request the site object because the
        #callback data does not include _etag
        data = get_resource("sites", "/" + site_id)
        url = "{0}/{1}".format(conf.api_server, data["_links"]["self"]["href"])
        name = data['name']
        sid = data['sid']
        path = data['sid']
        #username = data['username']
        mail = data['mail']
        etag = data['_etag']
        pw = mysql_password()

        template = env.get_template('settings.php')
        settings_php = template.render(
            profile='cu_fit',
            site=name,
            sid=sid,
            pw=pw,
            path=path,
            status=data['status'],
        )

        with open("/tmp/{0}.settings.php".format(sid), "w") as ofile:
            ofile.write(settings_php)

        fabfile.add_site_db(sid, name, pw)
        #using execute forces @roles('ENV') to be used when running the function
        execute(fabfile.add_site_dslm, sid=sid)
        execute(fabfile.push_settings, sid=sid)

        fabfile.site_install(sid, name, conf.profile)

        #if fit plus you might have packages to symlink
        if "packages" in data:
            execute(fabfile.add_site_packages, sid=sid, packages=data["packages"])

        #make sure passwords aren't in plain text when passed around by the api
        pw = encrypt_db_pw(conf.SECRET_KEY, pw)
        payload = {'db_key': pw, 'sid': sid, 'path': path}
        #if the site was posted as 'available' don't change it to 'installed'
        if data['status'] == 'pending':
            payload['status'] = 'installed'
        #update the site object in the api with the db pw...etag is required
        send_site_patch(url, payload, etag)
        #clean up site file permissions...
        #execute(fabfile.set_site_perms, sid=sid)
        #email the user...template in templates/email.html
        #send_site_intro(site_id, sid, you = mail)
        #update the aliases here
        #export_aliases.delay()


@celery.task
def launch_site(data):
    """On site POST if the status is 'launching' this task will be called to launch the site at the new path

    """

    if data and data['status'] == 'launching':
        #cast to string in case the id is an object
        site_id = str(data['_id'])
        #request full site info to get the site's ID hash
        data = get_resource("sites", "/" + site_id)
        template = env.get_template('settings.php')
        settings_php = template.render(
            profile='cu_fit',
            sid=data['sid'],
            path=data['path'],
            status=data['status'],
        )

        with open("/tmp/{0}.settings.php".format(data['sid']), "w") as ofile:
            ofile.write(settings_php)

        execute(fabfile.launch_site, sid=data['sid'])


def send_site_intro(site_id, sid, you):
    """
    Sends an email to th enew site owner.  Uses the email.html template in templates/

    :param sid: hash of the mongo document id
    :param you: email address of recipient (site owner)

    """
    template = env.get_template('email.html')
    #render email with variables
    content = template.render(
        sid=sid,
        fullid=site_id,
        webserver=conf.webservers[conf.environment],
    )
    send_email(content, me="no-reply@example.com", you=you)


@celery.task
def export_aliases():
    """
    This function prepares and renders the site data needed to create drush aliases
    :return None:
    """

    #get all sites
    sites = get_resource("sites", q='?max_results=2000')

    template = env.get_template('aliases.drushrc.php')
    #conf.platforms dict is coming from conf.py
    aliases = template.render(
        sites=sites['_items'],
        servers=conf.platforms['poolb-express'],
    )
    #write express aliases to file as well
    with open("/data/code/inventory/fabfile/aliases.drushrc.php", "w") as ofile:
        ofile.write(aliases)

    execute(fabfile.push_aliases)


@celery.task
def invite_site_users(users):
    """
    invite list of users
    """
    #group(run_cron.s(item) for item in sites).delay()
    pass


@celery.task
def prepare_custom_crons():
    envs = conf.platforms['poola-custom']
    for k in envs:
        host = envs[k][0]
        sites = fabfile.get_data_release_sites(host)
        #group(call_custom_cron.s(host, item) for item in sites).delay()
        chord(call_custom_cron.s(host, item) for item in sites)(check_cron_results.s(k))
        #print k, ' ', host, ' ', len(sites)


@celery.task
def call_custom_cron(host, site):
    failed = fabfile.run_custom_cron(host, site)
    out = ""
    if failed:
        href = "{0}{1}".format(conf.weburls[host], site)
        out = "<a href='{0}'>{1}</a>@{2} - {3}".format(href, site, host, failed)
    return out


@celery.task
def check_cron_results(values, env):
    errs = filter(None, values)
    if errs:
        message = ",<br><br>".join(errs)
        subject = "CRON - {0} errs on {1}".format(len(errs), env)
        send_email(message, subject)


@celery.task
def delete_express_site(site):
    fabfile.delete_db(site)
    execute(fabfile.remove_site_dirs, site=site)
    delete_resource(site)
    #update f5 and aliases


@celery.task
def prepare_express_settings():
    #get all sites
    express_sites = get_resource("sites", q='?max_results=2000')
    group(update_settings.s(item) for item in express_sites['_items']).delay()


@celery.task
def update_settings(site):
    if 'sid' in site:
        print "Updating settings on -> " + site['name'] + ' - ' + site['sid']
        template = env.get_template('settings.local.php')
        local_settings = template.render(
            site=site['name'],
            sid=site['sid'],
            status=site['status'],
            pw=decrypt_db_pw(conf.SECRET_KEY, site['db_key']),
            environment=conf.environment if conf.environment != 'prod' else '',
        )

        with open("/data/code/inventory/fabfile/{0}.settings.local.php".format(site['sid']), "w") as ofile:
            ofile.write(local_settings)

        template = env.get_template('settings.php')
        settings_php = template.render(
            profile='cu_fit',
            sid=site['sid'],
            path=site['path'],
            status=site['status'],
        )
        with open("/data/code/inventory/fabfile/{0}.settings.php".format(site['sid']), "w") as ofile:
            ofile.write(settings_php)

        execute(fabfile.push_settings, sid=site['sid'])
        return site['name'] + ' - ' + site['sid']


@celery.task
def call_add_site_user(sid, username, mail):
    fabfile.add_site_user(sid, username, mail)


#fixes a concurrency issue with Fabric
@worker_process_init.connect
def configure_workers(sender=None, conf=None, **kwargs):
    Crypto.Random.atfork()

