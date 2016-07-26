from eve import Eve
from inventory import sites_callback, sites_patch_callback
from . import utils

app = Eve(settings="/data/code/inventory/inventory/settings.py")

#tell Eve which functions to use as callbacks
app.on_post_POST_sites += sites_callback
app.on_post_PATCH_sites += sites_patch_callback


