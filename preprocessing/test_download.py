import requests

api_key = "8a23973c71dfa5b08a074e900b1411ea"
headers = {'api-key': api_key}

# Get the file URL from the list
files_url = "https://www.tng-project.org/api/TNG100-1/files/snapshot-99/"
response = requests.get(files_url, headers=headers)
files_data = response.json()
file_url = files_data['files'][0]  # Get first file

print(f"File URL from API: {file_url}")

# Try downloading
print("\n1. Testing direct GET with api-key header:")
r = requests.get(file_url, headers=headers, stream=True)
print(f"   Status: {r.status_code}")
print(f"   Content-Type: {r.headers.get('content-type')}")
print(f"   Content-Length: {r.headers.get('content-length')}")

# Try with redirect following
print("\n2. Testing with allow_redirects:")
r2 = requests.get(file_url, headers=headers, stream=True, allow_redirects=True)
print(f"   Status: {r2.status_code}")
print(f"   Content-Type: {r2.headers.get('content-type')}")
print(f"   Content-Length: {r2.headers.get('content-length')}")
print(f"   URL after redirect: {r2.url}")

# Try with wget-style parameters
print("\n3. Testing with format parameter:")
r3 = requests.get(file_url, headers=headers, params={'format': 'download'}, stream=True)
print(f"   Status: {r3.status_code}")
print(f"   Content-Type: {r3.headers.get('content-type')}")
print(f"   Content-Length: {r3.headers.get('content-length')}")

# Check if response is binary or HTML
if r2.status_code == 200:
    content_start = r2.content[:100]
    if b'<!DOCTYPE' in content_start or b'<html' in content_start:
        print("\n⚠ Response is HTML (error)")
    elif b'HDF' in content_start or content_start.startswith(b'\x89HDF'):
        print("\n✓ Response appears to be HDF5 file!")
    else:
        print(f"\n? Unknown format, first bytes: {content_start[:20]}")
