# Immich-python-slideshow

## Setup
1. Create API Key in Immich
2. Update the docker-compose.yml
    * subnet: 0.0.0.0/0
    * ip_range: 0.0.0.0/0
    * gateway: 0.0.0.0

## Use
1. Share an album with a URL that doesn't expire. This contains the access key for the share (share access key).
2. Get the guid for that share (your-share-guid-from-api):
   1. `curl -L -X GET https://my-immich.example.com/api/shared-link/ -H 'Accept: application/json' -H 'x-api-key: yourapikeyhere'`

Set your request url from your frame to the below. The first 2 values from from the above steps, the username is the username you'll set in the environment variables.

`https://url/path?shareId=<your-share-guid-from-api>&accessKey=<share-access-key>&user=<user-set-in-python-script>`


### Run the docker container

Set required environment variables:
```
# be sure to include the trailing slash for this one
export IMMICH_URL=https://my-immich.example.com/
export KEYS=some-username=12345
```

If using more than one user, add to your keys environment variable
```
export KEYS=some-username=12345,some-other-username=67890[,...=###,...=###]
```

If your proxy interacts with immich API directly, but you want to redirect users to a different url:

For example, you might run immich and immich-python-slideshow on the same host and want to avoid extra auth added by nginx in front of immich.

```
# be sure to include the trailing slash for this one
export IMMICH_API_URL=https://my-immich-host.lan:2283/
```


Start the container
```
docker compose up
```
