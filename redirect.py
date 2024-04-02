import os, requests, random, json, environs
import traceback
from urllib.parse import urlparse
from urllib.parse import parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from environs import Env

env = Env()
env.read_env()
key_pairs = env.dict('KEYS', subcast=str)

IMMICH_URL = os.environ["IMMICH_URL"]

IMMICH_API_URL = os.environ.get("IMMICH_API_URL")
if IMMICH_API_URL == 'unset':
    IMMICH_API_URL = IMMICH_URL

def get_images(photo, shareId, user):
    url = f"{IMMICH_API_URL}api/shared-link/" + shareId
    payload = {}
    if user in key_pairs.keys():
        API_KEY = key_pairs[user]
        headers = {
            'Accept': 'application/json',
            'x-api-key': API_KEY,
            'Connection': 'close'
        }
    response = requests.get(url, headers=headers, data=payload)
    y = json.loads(response.text)
    for x in y["assets"]:
        allowlist = ("jpg", "png")
        if x["originalPath"].lower().endswith(allowlist):
            try:
                photo[user].append(x["id"])
            except KeyError:
                photo[user] = [(x["id"])]
        else:
            print("Not an allowed filetype " + x["originalPath"], flush=True)
            print("Not an allowed filetype " + x["id"] + " " + str(allowlist), flush=True)
    response.close()
    return photo


def get_query_field(url, field):
    try:
        return parse_qs(urlparse(url).query)[field][0]
    except KeyError:
        return []


def status(photo, id, user):
    print(id, flush=True)
    print(len(photo[user]), flush=True)


class Redirect(BaseHTTPRequestHandler):

    def execute_immich_redirect(self, user, access_key):
        photo_id = random.choice(photo[user])
        status(photo, photo_id, user)
        url_for_redirection = f"{IMMICH_URL}api/asset/file/" + photo_id + "?isThumb=false&isWeb=true&key=" + access_key
        print(url_for_redirection)
        photo[user].remove(photo_id)
        self.send_response(302)
        self.send_header('Location', url_for_redirection)
        self.end_headers()

    def do_GET(self):

        url = f"{IMMICH_URL}" + self.path
        share_id = get_query_field(url, 'shareId')
        access_key = get_query_field(url, 'accessKey')
        user = get_query_field(url, 'user')
        reset = get_query_field(url, 'reset')

        if not access_key:
            self.send_response(400)

        try:
            if reset:
                print("Resetting...Getting images.", flush=True)
                get_images(photo, share_id, user)
                # print(len(photo[user]),flush=True)
            
            if not photo.get(user):
                get_images(photo, share_id, user)

            if user not in photo:
                get_images(photo, share_id, user)

            self.execute_immich_redirect(user, access_key)
        except Exception as e:
            print(e, flush=True)
            print(traceback.format_exc(), flush=True)
            self.send_error(500)


photo = {}
print("ready", flush=True)
HTTPServer(("", int(8000)), Redirect).serve_forever()
