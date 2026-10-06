import requests

# ---------- CONFIGURATION ----------
SIMULATION = "TNG50-2"
SNAPSHOT = 99
API_KEY = "8a23973c71dfa5b08a074e900b1411ea"   # <-- Replace with your key from https://www.tng-project.org/users/account/
# -----------------------------------

BASE_URL = "https://www.tng-project.org/api/"
HEADERS = {"api-key": API_KEY}

def sizeof_fmt(num):
    """Convert bytes to human-readable string."""
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if num < 1024.0:
            return f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} PiB"

def get_file_size(url):
    """Return the size in bytes for a given file URL, or None if cannot determine."""
    # First try HEAD (fast)
    resp = requests.head(url, headers=HEADERS, allow_redirects=True)
    if resp.status_code == 200:
        size = resp.headers.get('content-length')
        if size is not None:
            return int(size)
    # If HEAD doesn't give size, try GET with Range: bytes=0-0
    resp = requests.get(url, headers={**HEADERS, "Range": "bytes=0-0"}, allow_redirects=True)
    if resp.status_code in (200, 206):
        # Content-Range header often contains total size: e.g., "bytes 0-0/123456789"
        content_range = resp.headers.get('content-range', '')
        if '/' in content_range:
            total = content_range.split('/')[-1]
            if total.isdigit():
                return int(total)
        # Fallback to content-length
        size = resp.headers.get('content-length')
        if size is not None:
            return int(size)
    return None

def main():
    # 1. Get the list of file URLs
    listing_url = f"{BASE_URL}{SIMULATION}/files/snapshot-{SNAPSHOT}/"
    resp = requests.get(listing_url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()

    # The response is a dict with a "files" key containing a list of URLs
    file_urls = data.get('files', [])
    if not file_urls:
        print("No files found.")
        return

    print(f"Files for {SIMULATION}, snapshot {SNAPSHOT}:")
    print("-" * 50)

    total = 0
    for url in file_urls:
        filename = url.split('/')[-1]   # e.g., snapshot-99.0.hdf5
        size = get_file_size(url)
        if size is None:
            print(f"{filename:30}  <size unknown>")
        else:
            print(f"{filename:30} {sizeof_fmt(size):>12}")
            total += size

    print("-" * 50)
    print(f"{'TOTAL':30} {sizeof_fmt(total):>12}")

if __name__ == "__main__":
    main()