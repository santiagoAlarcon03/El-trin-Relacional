#!/usr/bin/env python3
import requests
import json

response = requests.post(
    "http://localhost:8000/search/text-to-image",
    json={"query": "gafas de sol", "limit": 1}
)

print(json.dumps(response.json(), indent=2, ensure_ascii=False))
