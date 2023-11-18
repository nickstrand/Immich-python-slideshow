# Immich-python-slideshow

## Setup
1. Create API Key in Immich
1. Update the redirect-multiuser.py with your API key
- Replace the \<user\> and \<API KEY\>
- Replace \<https://url/here> with your url

1. Update the docker-compose.yml
- subnet: 0.0.0.0/0
- ip_range: 0.0.0.0/0
- gateway: 0.0.0.0

## Use
1. Share an album with a URL that doesn't expire
2. Browse to the share url with f12 (network debugging)
3. Open an indivudial image and look for the file load
4. `/api/asset/thumbnail/3c57228c-8262-4e14-998b-c10755413e6d?format=WEBP&key=<this-shares-access-key>`

Set your request url from your frame to 
`https://url/path?shareId=<your-share-id-from-api>&accessKey=<this-shares-access-key>&user=<user-set-in-python-script>`
