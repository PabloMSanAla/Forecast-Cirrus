import requests
import json

api_key = "8a23973c71dfa5b08a074e900b1411ea"
headers = {'api-key': api_key}

# Test file list endpoint
url = "https://www.tng-project.org/api/TNG100-1/files/snapshot-99/"
print(f"Testing URL: {url}")

response = requests.get(url, headers=headers)
print(f"Status code: {response.status_code}")
print(f"Response type: {type(response.json())}")

data = response.json()
print(f"\nResponse structure:")
if isinstance(data, dict):
    print(f"Dictionary with keys: {list(data.keys())}")
    for key, value in data.items():
        print(f"  {key}: {type(value)} - {str(value)[:100]}")
elif isinstance(data, list):
    print(f"List with {len(data)} items")
    if len(data) > 0:
        print(f"First item type: {type(data[0])}")
        print(f"First item: {data[0]}")
else:
    print(f"Unknown type: {type(data)}")
    print(data)

# Also test direct file URL
print("\n" + "="*60)
file_url = "https://www.tng-project.org/api/TNG100-1/files/snapshot-99/snap_099.0.hdf5"
print(f"Testing direct file URL: {file_url}")
response2 = requests.get(file_url, headers=headers)
print(f"Status code: {response2.status_code}")
print(f"Content-Type: {response2.headers.get('content-type', 'unknown')}")
print(f"Content-Length: {response2.headers.get('content-length', 'unknown')}")
if 'html' in response2.headers.get('content-type', '').lower():
    print("Response is HTML (error page)")
else:
    print("Response appears to be binary data (good!)")
