#!/usr/bin/env python3
import os
import requests
import json
import random
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from environs import Env

# Load environment variables
env = Env()
env.read_env()
key_pairs = env.dict('KEYS', subcast=str)
IMMICH_URL = os.environ["IMMICH_URL"]
IMMICH_API_URL = os.environ.get("IMMICH_API_URL")
if IMMICH_API_URL == 'unset' or not IMMICH_API_URL:
    IMMICH_API_URL = IMMICH_URL

FALLBACK_IMAGE = "https://images.pexels.com/photos/417074/pexels-photo-417074.jpeg"
DEBUG = os.environ.get("DEBUG", "0") == "1"

# Helper to parse query params
def get_query_field(url, field):
    try:
        return parse_qs(urlparse(url).query)[field][0]
    except KeyError:
        return None

# Get images for a user/share key from Immich API
def get_images_for_user(share_key, user):
    images = []
    if user in key_pairs:
        api_key = key_pairs[user]
        headers = {
            'Accept': 'application/json',
            'x-api-key': api_key,
            'Connection': 'close'
        }
        if DEBUG:
            print(f"[DEBUG] Using API key for user: {user}", flush=True)
            print(f"[DEBUG] Headers: {headers}", flush=True)
            print(f"[DEBUG] Requesting shared link info: {IMMICH_API_URL}api/shared-links/me?key={share_key}", flush=True)
        # Step 1: Get shared link info
        url = f"{IMMICH_API_URL}api/shared-links/me?key={share_key}"
        try:
            response = requests.get(url, headers=headers)
            if DEBUG:
                print(f"[DEBUG] Shared link response status: {response.status_code}", flush=True)
                print(f"[DEBUG] Shared link response: {response.text}", flush=True)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if DEBUG:
                        print(f"[DEBUG] Shared link response is a list, using first element if available.", flush=True)
                    if data:
                        data = data[0]
                    else:
                        data = {}
                # If assets are directly attached to the shared link, use them
                for asset in data.get("assets", []):
                    path = asset.get("originalPath", "")
                    if path.lower().endswith(("jpg", "png")):
                        images.append(asset["id"])
                # If the shared link is for an album, fetch album assets
                album = data.get("album")
                if album and "id" in album:
                    album_id = album["id"]
                    if DEBUG:
                        print(f"[DEBUG] Album found in shared link: {album}", flush=True)
                        print(f"[DEBUG] Requesting album info: {IMMICH_API_URL}api/albums/{album_id}", flush=True)
                    album_url = f"{IMMICH_API_URL}api/albums/{album_id}"
                    album_resp = requests.get(album_url, headers=headers)
                    if DEBUG:
                        print(f"[DEBUG] Album response status: {album_resp.status_code}", flush=True)
                        print(f"[DEBUG] Album response: {album_resp.text}", flush=True)
                    if album_resp.status_code == 200:
                        album_data = album_resp.json()
                        for asset in album_data.get("assets", []):
                            path = asset.get("originalPath", "")
                            if path.lower().endswith(("jpg", "png")):
                                images.append(asset["id"])
                    else:
                        print(f"Immich API album error: {album_resp.status_code}", flush=True)
            else:
                print(f"Immich API error: {response.status_code}", flush=True)
        except Exception as e:
            print(f"Exception fetching images: {e}", flush=True)
    if not images:
        images = [FALLBACK_IMAGE]
    return images

class ImmichRedirectHandler(BaseHTTPRequestHandler):
    user_images = {}

    def do_GET(self):
        url = f"{IMMICH_URL}" + self.path
        share_key = get_query_field(url, 'shareId')
        print(url)
        user = get_query_field(url, 'user')
        reset = get_query_field(url, 'reset')

        if not share_key or not user:
            print(share_key, user, flush=True)
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing shareKey or user")
            return

        if reset or user not in self.user_images:
            self.user_images[user] = get_images_for_user(share_key, user)

        images = self.user_images.get(user, [FALLBACK_IMAGE])
        # Choose a random image from the list
        if not images:
            images = [FALLBACK_IMAGE]
        image_id = random.choice(images)
        images.remove(image_id)
        # If all images have been displayed, reload the list and retry
        if not images:
            self.user_images[user] = get_images_for_user(share_key, user)
            images = self.user_images.get(user, [FALLBACK_IMAGE])
            image_id = random.choice(images)
            images.remove(image_id)
        self.user_images[user] = images if images else [FALLBACK_IMAGE]

        # If the image_id is a fallback URL, redirect directly
        if image_id.startswith("http"):
            redirect_url = image_id
        else:
            redirect_url = f"{IMMICH_URL}api/assets/{image_id}/thumbnail?size=preview&key={share_key}"

        self.send_response(302)
        self.send_header('Location', redirect_url)
        self.end_headers()

if __name__ == "__main__":
    print("Immich redirect proxy ready", flush=True)
    HTTPServer(("", 8000), ImmichRedirectHandler).serve_forever()
