#!/usr/bin/env python3

import os, requests, random, json
from urllib.parse import urlparse
from urllib.parse import parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler

IMMICH_URL = os.environ["IMMICH_URL"]

USERNAME_1 = os.environ['USERNAME_1']
API_KEY_1 = os.environ['API_KEY_1']

USERNAME_2 = os.environ['USERNAME_2']
API_KEY_2 = os.environ['API_KEY_2']


def get_images(photo, shareId, user):
    url = f"{IMMICH_URL}api/shared-link/" + shareId
    payload = {}
    if user == USERNAME_1:
        headers = {
            'Accept': 'application/json',
            'x-api-key': '<apikey>',
            'Connection': 'close'
        }
    elif user == USERNAME_2:
        headers = {
            'Accept': 'application/json',
            'x-api-key': '<apikey>',
            'Connection': 'close'
        }
    # else:
    # print("failed",flush=True)
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


def check_photos(photo, shareId, user):
    try:
        if len(photo[user]) < 2:
            print("Getting images for " + user, flush=True)
            get_images(photo, shareId, user)
        return photo
    except KeyError:
        print("Key Error. Getting images for " + user, flush=True)
        get_images(photo, shareId, user)
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
    def do_GET(self):

        url = f"{IMMICH_URL}" + self.path
        share_id = get_query_field(url, 'shareId')
        access_key = get_query_field(url, 'accessKey')
        user = get_query_field(url, 'user')
        reset = get_query_field(url, 'reset')

        if reset:
            print("Resetting...Getting images.", flush=True)
            get_images(photo, share_id, user)
            # print(len(photo[user]),flush=True)

        try:
            if not access_key:
                self.send_response(400)
            else:
                if photo[user]:
                    id = random.choice(photo[user])
                    status(photo, id, user)
                    print(f"{IMMICH_URL}api/asset/file/" + id + "?isThumb=false&isWeb=true&key=" + access_key)
                    photo[user].remove(id)
                    self.send_response(302)
                    self.send_header('Location',
                                     f"{IMMICH_URL}api/asset/file/" + id + "?isThumb=false&isWeb=true&key=" + access_key)
                    self.end_headers()
                else:
                    check_photos(photo, share_id, user)
        except KeyError:
            # print("Getting images.",flush=True)
            get_images(photo, share_id, user)
            print("KeyError", flush=True)
            id = random.choice(photo[user])
            photo[user].remove(id)
            self.send_response(302)
            self.send_header('Location',
                             f"{IMMICH_URL}api/asset/file/" + id + "?isThumb=false&isWeb=true&key=" + access_key)
            self.end_headers()
            return


photo = {}
print("ready", flush=True)
HTTPServer(("", int(8000)), Redirect).serve_forever()
