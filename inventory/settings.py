#SERVER_NAME = 'localhost:5000'

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DBNAME = 'inventory'

RESOURCE_METHODS = ['GET', 'POST', 'DELETE']

ITEM_METHODS = ['GET', 'PATCH', 'DELETE']

PAGINATION_LIMIT = 2000
PAGINATION_DEFAULT = 1000

MONGO_QUERY_BLACKLIST = ['$where']

## SITES
sites_schema = {
    'username': {
      'type': 'string',
      'minlength': 1,
      'maxlength': 40,
    },
    'mail': {
      'type': 'string',
      'minlength': 1,
      'maxlength': 40,
    },
    'name': {
      'type': 'string',
      'minlength': 1,
    },
    'path': {
      'type': 'string',
      'unique': True,
    },
    'db_key': {
      'type': 'string',
      'minlength': 1,
      'maxlength': 128,
    },
    'sid': {
      'type': 'string',
      'minlength': 9,
      'maxlength': 14,
    },
    'status': {
        'type': 'string',
        'allowed': ["pending", "installed", "launching", "launched", "available", "destroy"],
    },
    'packages': {
        'type': 'dict',
        'schema': {
            'custom': {'type': 'list'},
            'contrib': {'type': 'list'}
        }
    },
}
sites = {
    'item_title': 'site',
    'additional_lookup': {
        'url': 'regex("[\w]+")',
        'field': 'sid'
    },
    'resource_methods': ['GET', 'POST'],
    'public_methods': ['GET'],
    'public_item_methods': ['GET'],
    'schema': sites_schema,
}


user_schema = {
    'email': {
        'type': 'string',
        'minlength': 5,
        'maxlength': 254,
        'required': True,
        'unique': True,
    },
    'username': {
        'type': 'string',
        'required': True,
        'unique': True,
    },
    'sites': {
        'type': 'list',
        'site': {
            'type': 'dict',
            'schema': {
                'id': {'type': 'string'},
                'roles': {'type': 'list'},
            },
        }
    },

}


users = {
    'item_title': 'user',

    'additional_lookup': {
        'url': 'regex("[\w]+")',
        'field': 'username'
    },

    'cache_control': '',
    'cache_expires': 0,
    'query_objectid_as_string': True,
    'resource_methods': ['GET', 'POST'],
    'public_methods': ['GET'],
    'public_item_methods': ['GET'],
    'schema': user_schema
}

DOMAIN = {
    'sites': sites,
    'users': users, 
}
