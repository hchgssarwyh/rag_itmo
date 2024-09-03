import requests

url = "http://localhost:8000/api/v1/collections"
payload = {
        "id": 0,
        "name": "test",
        "metadata": {
            "description": "Default description",
            "created_by": "system"
        }
    }

response = requests.post(url, json=payload)

print(response.status_code)
print(response.text)
url = "http://localhost:8000/api/v1/collections/0/add"  # используйте тот же URL
response = requests.get(url)

print(response.status_code)
print(response.text)
