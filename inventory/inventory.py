import json
from hashlib import sha1
from .utils import send_site_patch
from . import tasks
from .conf import api_server


def sites_callback(request, payload):
    """This function is called whenever a new site is created in teh eve api.

    :param request: original flask.request object, only includes the data you POST
    :param payload: POST response as JSON, includes _id and etag

    """
    print 'A post to "sites" was just performed!'

    #get response and make sure its a list
    resp_data = json.loads(payload.data)
    if not isinstance(resp_data, list):
        resp_data = [resp_data]

    #get request and convert to list
    req_data = request.json
    if not isinstance(req_data, list):
         req_data = [request.json]

    #update each new site with an sid then kick off new_site task
    for site in resp_data:
        site_id = site['_id']
        #if multiple sites were posted match the site in request data with
        #current site in resp_data so we have a status
        status = filter(lambda x: str(x['_id']) == site_id, req_data)[0]['status']
        if status in ['pending', 'available']:
            # create shorter site id
            sid = 'p1' + sha1(site_id).hexdigest()[0:10]
            url = api_server + "/sites/" + str(site_id)
            # update site entity with sid
            tasks.patching.apply_async(
                (url, {'sid':sid, 'status':status}, site['_etag']),
                link=tasks.new_site.si(site_id)
            )


def sites_patch_callback(request, payload):
    """Handles the patch event for sites.
    If the patched site is valid and status is 'launching' the symlinks will be created to
    allow for a production path for the patched site.

    :param request: original flask.request object, only includes the data you PATCH
    :param payload: POST response as JSON, includes _id and _etag

    """
    #status only exists here if it was included in the PATCHED payload
    if 'status' in request.json:
        payload_data = json.loads(payload.data)
        _id = payload_data["_id"]
        status = request.json["status"]
        data = {'_id': _id, "status": status}
        if status == "launching":
            tasks.launch_site.delay(data)
        elif status == 'installed':
            #tasks.call_add_site_user.delay(request.json["sid"], request.json["mail"], 'site_owner')
            url = api_server + "/sites/" + str(_id)
            #send_site_patch(url, {'status':'installed'}, payload_data['_etag'])
            #tasks.send_site_intro(_id, request.json["sid"], you = request.json["mail"])
            print payload.data, "\n", request.json
        elif status == 'destroy':
            # todo:handle site deletion
            pass
