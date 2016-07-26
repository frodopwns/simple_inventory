import hashlib
import random
import string
import requests 
import json
from Crypto.Cipher import AES 
from Crypto import Random 
import smtplib
from email.mime.text import MIMEText
import re
from . import conf


def randomword(length=14):
    """Returns a random alphabetical sequence

    """
    return ''.join(random.choice(string.lowercase) for i in range(length))


def mysql_password():
    """
    Hash string twice with SHA1 and return uppercase hex digest,
    prepended with an asterix.

    This function is identical to the MySQL PASSWORD() function.
    """
    start = randomword()
    pass1 = hashlib.sha1(start).digest()
    pass2 = hashlib.sha1(pass1).hexdigest()
    return "*" + pass2.upper()


def encrypt_db_pw(key, pw):
    iv = Random.new().read(AES.block_size) 
    cipher = AES.new(key, AES.MODE_CFB, iv) 
    msg = iv + cipher.encrypt(pw) 
    encrypted = msg.encode("hex")
    return encrypted


def decrypt_db_pw(key, encrypted):
    iv = Random.new().read(AES.block_size) 
    cipher = AES.new(key, AES.MODE_CFB, iv) 
    decrypted = cipher.decrypt(encrypted.decode("hex"))[len(iv):] 
    return decrypted


def send_email(content, subject="Inventory Email", me='frodopwns@gmail.com', you=['matt.tucker@colorado.edu']):
    """
    Sends email to site_owner when the site is ready.

    :param content: content of the email to be sent
    :param me: the user sending the email
    :param you: the target email address the email will be sent to

    """    

    # Create a text/plain message
    # make 2nd argument to MIMEText as 'html' to make html email
    msg = MIMEText(content, 'html')

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = ", ".join(you)
    
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(me, you, msg.as_string())
    s.quit()


def send_site_patch(url, data, etag):
    """
    Updates the mongo document via PATCH

    :param url: the url to the document in eve
    :param data: the dictionary containing the updates
    :param etag: the latest etag for the document being updated

    """
    #print "send_site_patch('{0}', '{1}', '{2}')".format(url, data, etag)
    headers = {'Content-Type': 'application/json', 'If-Match': etag}
    r = requests.patch(url, headers = headers, data = json.dumps(data), verify=False)
    #print r.ok
    print "site patch successfull" if r.ok else "site patch failed"


def get_resource(res, q = ""):
    """wrapper for get request to inventory
    
    :param res:  a string representing the resource being requested
    :param _id:  resource id if you want a specific item  
    """
    url = "{0}/{1}{2}".format(conf.api_server, res, q)
    r = requests.get(url, verify=False)
    if r.ok:
        return r.json()
    else:
        return False


def post_resource(res='sites', payload={}):
    """
    wrapper for post request to inventory

    :param res:  a string representing the resource being requested
    :param payload: the dictionary containing the item to be posted
    """
    headers = {'Content-Type': 'application/json'}
    url = "{0}/{1}/".format(conf.api_server, res)
    r = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
    if r.ok:
        return r.json()
    else:
        return False


def patch_resource(res='sites', payload={}):
    """
    wrapper for patch request to inventory

    :param res:  a string representing the resource being requested
    :param payload: the dictionary containing the item to be posted
    """
    #cant patch without etag in payload
    assert '_etag' in payload
    #need _id in payload as well
    assert '_id' in payload
    site_id = payload['_id']
    del payload['_id']
    #headers needs up-to-date etag
    headers = {'Content-Type': 'application/json', 'If-Match': payload['_etag']}
    del payload['_etag']
    url = "{0}/{1}/{2}".format(conf.api_server, res, site_id)
    r = requests.patch(url, headers=headers, data=json.dumps(payload), verify=False)
    if r.ok:
        return r.json()
    else:
        return False


def delete_resource(site):
    url = "{0}/sites/{1}".format(conf.api_server, site['_id'])
    headers = {"content-type": "application/json", "If-Match": site["_etag"]}
    r = requests.delete(url, headers = headers, verify=False)
    if r.ok:
        return r.json()
    else:
        return False


def get_site_by_name(path):
    r = get_resource("sites", q='?where={%22name%22:%22' + path + '%22}')
    if r and len(r['_items']) > 0:
        return r['_items'][0]
    return False


def fixslash(s):
    """
    Massages site data for alias creation.  Replaces subsite forward slash with underscore.
    Sets original value in key 'path_raw'.
    :param s: site dictionary
    :return: returns fixed site dictionary
    """
    s['path_raw'] = s['path']
    if "/" in s['path']:
        s['path'] = s['path'].replace("/", "_")
        s['name'] = s['name'].replace("/", "_")
    return s


def get_sites_available():
    sites = get_resource('sites', q='?where={"status":"available"}')
    if '_items' in sites:
        sites = sites['_items']
    else:
        sites = []
    return sites


def get_site_users(site_id):
    """
    Returns a list of users with a role on the site passed in

    :param site_id: Id of site to find users for
    :return: List of users
    """
    res = []
    users = get_resource('users')['_items']
    for user in users:
        for site in user['sites']:
            if site['id'] == site_id:
                res.append(user)
    return res


def make_machine_readable(s):
    name = s.lower().replace(" ", "_")
    return re.sub(r'\W+', '', name)
