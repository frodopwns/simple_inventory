## Poros Inventory

This local_settings.py file contains sensitive or dynamic information that will be different
for different teams/environments:

    #local_settings.py
    environment = 'prod'
    #mysql admin creds
    mysql_user = 'user'
    mysql_pw = 'pw'
    ssh_user = 'user'
    # in case an enviornment needs a different url
    api_server = 'https://localhost/inventory'
    allowed_users = []


##Eve

to post a site to eve:

    import requests
    import json
    from inventory.local_settings import ldap_user, ldap_pw
    
    payload = { 'name': 'TestSite', 'path': 'TestPath' }
    headers = {"content-type": "application/json"}
    r = requests.post(api_server + "/sites", headers = headers,
        data = json.dumps(payload), verify = False)

    
to patch (or update) a document (site or pool...maybe user):

    import requests
    import json
    from inventory.local_settings import ldap_user, ldap_pw
    
    url = api_server + "/sites/526efd595867b3381e781163"
    etag = requests.get(url).json()['_etag']
    payload = {'name': 'newname'}
    headers = {'Content-Type': 'application/json', 'If-Match': etag}
    r = requests.patch(url, headers = headers, data = json.dumps(payload), verify = False)
    print "yayy" if r.ok else "booo"


Daemon
------

Usage:	/etc/init.d/celeryd {start|stop|restart|status}

Configuration file:
 	/etc/default/celeryd

get init script from:
https://github.com/celery/celery/tree/3.0/extra/generic-init.d/

Daemonizing worker prod config
put in /etc/default/celeryd

    # Name of nodes to start
    # here we have a single node
    CELERYD_NODES="worker1"
    # or we could have three nodes:
    #CELERYD_NODES="w1 w2 w3"
    #this may be different for you: type 'which celery' from terminal to check
    CELERY_BIN="/usr/local/bin/celery"
    # App instance to use
    # # comment out this line if you don't use an app
    # CELERY_APP="proj"
    # # or fully qualified:
    #CELERY_APP="tasks"
    CELERY_APP="inventory.tasks:celery"
    # Where to chdir at start.
    CELERYD_CHDIR="/data/code/inventory"

    # Extra arguments to celeryd
    #CELERYD_OPTS="-A inventory.tasks --time-limit=12000 --loglevel=WARNING"
    CELERYD_OPTS="-A inventory.tasks --time-limit=12000 --loglevel=WARNING --concurrency=2 -Q:worker1 celery"

    # %n will be replaced with the nodename.
    CELERYD_LOG_FILE="/var/log/celery/%n.log"
    CELERYD_PID_FILE="/var/run/celery/%n.pid"

    # Workers should run as an unprivileged user.
    CELERYD_USER="dplagnt"
    CELERYD_GROUP="dplagnt"
    #CELERYD_GROUP="www-data"


Make sure these two directories exist and that the user the celery daemon is running as can write to them.

    /var/log/celery
    /var/run/celery

Setting up Celery Flower (not currently implemented):

    sudo pip install flower
    celery flower --port=5555 --broker=mongodb://localhost:27017/inventory


Interact with celeryd:

    sudo service celeryd start
    sudo service celeryd stop
    sudo service celeryd restart

Restart CeleryBeat:

    sudo service celerybeat [start|stop]


#Statuses

    Allowed: ["pending", "installed", "launching", "launched", "available", "destroy"]

    - pending: Site has been posted but not finished installing
    - installed: Site installed and ready for use
    - launching: site patched for launch but not finished
    - launched: site launched with prod url
    - available: site installed but not assigned to any user
    - destroy: site queued for deletion
