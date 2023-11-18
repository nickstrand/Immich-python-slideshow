#!/usr/bin/env python3

import sys, requests, random, json
from urllib.parse import urlparse
from urllib.parse import parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler

def get_Images(photo,shareId,user):
  url = "<https://url/here>api/shared-link/"+shareId
  payload={}
  if user == "<user>":
    headers = {
      'Accept': 'application/json',
      'x-api-key': '<apikey>',
      'Connection': 'close'
    }
  elif user == "<user>" or "<user>":
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
      print("Not an allowed filetype "+x["originalPath"],flush=True)
      print("Not an allowed filetype "+x["id"]+" "+str(allowlist),flush=True)
  response.close()
  return photo

def check_photos(photo,shareId,user):
  try:
    if len(photo[user]) < 2:
      print("Getting images for "+user,flush=True)
      get_Images(photo,shareId,user)
    return photo
  except KeyError:
    print("Key Error. Getting images for "+user,flush=True)
    get_Images(photo,shareId,user)
    return photo

def get_query_field(url, field):
  try:
      return parse_qs(urlparse(url).query)[field][0]
  except KeyError:
      return []
  
def status(photo,id,user):
  print(id,flush=True)
  print(len(photo[user]),flush=True)

class Redirect(BaseHTTPRequestHandler):
  def do_GET(self):

    url = "<https://url/here>"+self.path
    shareId = get_query_field(url,'shareId')
    accessKey = get_query_field(url,'accessKey')
    user = get_query_field(url,'user')
    reset = get_query_field(url,'reset')

    if reset:
      print("Resetting...Getting images.",flush=True)
      get_Images(photo,shareId,user)
      # print(len(photo[user]),flush=True)

    try:
      if not accessKey:
        self.send_response(400)
      else:
        if photo[user]:
          id = random.choice(photo[user])
          status(photo,id,user)
          print("<https://url/here>api/asset/file/"+id+"?isThumb=false&isWeb=true&key="+accessKey)
          photo[user].remove(id)
          self.send_response(302)
          self.send_header('Location', "<https://url/here>api/asset/file/"+id+"?isThumb=false&isWeb=true&key="+accessKey)
          self.end_headers()
        else:
          check_photos(photo,shareId,user)
    except KeyError:
      # print("Getting images.",flush=True)
      get_Images(photo,shareId,user)
      print("KeyError",flush=True)
      id = random.choice(photo[user])
      photo[user].remove(id)
      self.send_response(302)
      self.send_header('Location', "<https://url/here>api/asset/file/"+id+"?isThumb=false&isWeb=true&key="+accessKey)
      self.end_headers()
      return

photo = {}
print("ready",flush=True)
HTTPServer(("", int(8000)), Redirect).serve_forever()
