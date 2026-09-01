#!/bin/bash

POD=$(kubectl get pods -l app=media-api -o jsonpath='{.items[0].metadata.name}')

kubectl exec "$POD" -- python -c "
import urllib.request
import json

data = json.dumps({
    'title': '$1',
    'file_path': '/movies/$2.mkv',
    'media_type': 'movie'
}).encode()

req = urllib.request.Request(
    'http://localhost:8080/media',
    data=data,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

print(urllib.request.urlopen(req).read().decode())
"
