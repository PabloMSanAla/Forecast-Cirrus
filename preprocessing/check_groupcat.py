import requests

api_key = "8a23973c71dfa5b08a074e900b1411ea"
headers = {'api-key': api_key}

# Check what group catalog files are available for snapshot 99
print("Checking group catalog files for snapshot 99...\n")

# Try different endpoints
endpoints = [
    "https://www.tng-project.org/api/TNG100-1/files/groupcat-99/",
    "https://www.tng-project.org/api/TNG100-1/snapshots/99/",
]

for url in endpoints:
    print(f"Testing: {url}")
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"Keys: {list(data.keys())}")
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    print(f"  {key}: {len(value)} items")
                    print(f"    First item: {value[0]}")
                elif isinstance(value, (str, int, float)):
                    print(f"  {key}: {value}")
    print("-" * 60)
