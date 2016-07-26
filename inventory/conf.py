"""
Configuration file for Inventory system

All configurables should go here so values can be propagated to teh various functions from a central location
"""

ldap_server = 'ldap://directory.somehwere.someplace:389'
#db auth secret
SECRET_KEY = 's3f9k8s7rabblerasbblerabblef2hjd723m4'

#drupal profile to install
profile = 'standard'
cu_fit_version = '1.6'

#### Server Lists ####

#this data set is used for the drush aliases template
platforms = {
    'poola-custom': {
        'prod': ['wweb1', 'wweb2'],
        'test': ['wwebtest1', 'wwebtest2'],
        'stage': ['wstage1'],
        'dev': ['wwebdev1'],
    },
    'poolb-express': {
        'prod': ['wweb3', 'wweb4'],
    }
}

weburls = {
    'wweb1': 'http://www.somehwere.someplace/',
    'wwebtest1': 'http://www-test.somehwere.someplace/',
    'wstage1': 'http://www-stage.somehwere.someplace/',
    'wwebdev1': 'http://www-dev.somehwere.someplace/',
}

#fabric uses this and the environment variable
#to determine which F5 servers to update
f5servers = {
    'prod': ['uctool@its4-f5.somehwere.someplace', 'uctool@its5-f5.somehwere.someplace'],
    'dev': ['uctool@its6-f5.somehwere.someplace', 'uctool@its7-f5.somehwere.someplace'],
    'local': [],
}

#the easiest way to get the f5 conf filename per environment
f5config = {
    'prod': 'WWWNGProdDataGroup.dat',
    'dev': 'WWWNGDevDataGroup.dat',
}
#entries in teh f5 that are not sites per se
f5exceptions = [
    '/engineering/videos',
    '/law/media',
    '/catalog',
    '/p1',
]

#webservers (used for email template)
webservers = {
    'prod': 'https://www.somehwere.someplace/',
    'dev': 'https://www-dev.somehwere.someplace/',
    'local': 'https://expresslocal/',
}

#reverse_proxy_addresses
reverse_proxies = {
    'prod': ['172.20.11.11', '172.20.11.11', ],
    'stage': ['128.138.111.11', ],
    'dev': ['172.20.11.11', ],
     'local': [],
}

#varnish_control_terminal
varnish_control = {
    'prod': 'wvarn3.int.somehwere.someplace:6082 wvarn4.int.somehwere.someplace:6082',
    'stage': 'wstage1.somehwere.someplace:6082',
    'dev': 'wvarndev2.int.somehwere.someplace:6082',
    'local': '',
}

#memcache_servers
memcache_servers = {
    'prod': ['wmem1.int.somehwere.someplace:11212', 'wmem2.int.somehwere.someplace:11212', ],
    'stage': ['wstage1.somehwere.someplace:11211', ],
    'dev': ['wmemdev1.int.somehwere.someplace:11211', ],
    'local': ['localhost:11211'],
}

#prebiult sites for cloning
base_sites = [
    'cu_fit'
]

clone_sites = True

#importing local_settings.py here
#any value above can be overridden in the local_settings file
try:
    from local_settings import *
except ImportError:
    raise Exception("You need a local_settings.py file!")

#url to eve instance, no trailing slash
if environment == 'local':
    api_server = 'https://localhost:5000'
elif environment == 'dev':
    api_server = 'https://wwhdev1.int.somehwere.someplace/inventory'
elif environment == 'prod':
    api_server = 'https://wwh1.int.somehwere.someplace/inventory'

