import sys
import http.client
import json
import urllib.parse
from pathlib import Path

# Get the `name` parameter from the command-line arguments
if len(sys.argv) < 2:
    raise ValueError("Please provide the 'name' parameter as a command-line argument.")
dynamic_name = sys.argv[1]  # The first argument is the dynamic `name`

# Construct the URL dynamically
base_url = "172.16.1.236:8081"
api_path = f"/service/rest/v1/search/assets?direction=desc&repository=Space-Reserve&format=maven2&group=Space-Reserve&name={urllib.parse.quote(dynamic_name)}&version=1.0.0"

def fetch_data_from_api(host, path):
    """Fetch data from the API."""
    conn = http.client.HTTPConnection(host)
    conn.request("GET", path)
    response = conn.getresponse()
    if response.status != 200:
        raise RuntimeError(f"Failed to fetch assets: {response.status} {response.reason}")
    data = response.read()
    conn.close()
    return json.loads(data)

def download_file(host, path, filename):
    """Download a file and save it locally."""
    conn = http.client.HTTPConnection(host)
    conn.request("GET", path)
    response = conn.getresponse()
    if response.status != 200:
        raise RuntimeError(f"Failed to download the file: {response.status} {response.reason}")
    with open(filename, "wb") as file:
        file.write(response.read())
    conn.close()

def download_latest_zip():
    try:
        print(f"Fetching data from URL: http://{base_url}{api_path}")

        # Fetching data from the URL
        data = fetch_data_from_api(base_url, api_path)

        # Filter for ZIP files
        zip_assets = [item for item in data.get("items", []) if item.get("downloadUrl", "").endswith(".zip")]
        if not zip_assets:
            raise RuntimeError("No ZIP files found in the response.")

        # Sort ZIP files by the lastModified field in descending order (latest first)
        latest_zip_asset = sorted(
            zip_assets,
            key=lambda x: x.get("lastModified", ""),
            reverse=True
        )[0]

        download_url = latest_zip_asset["downloadUrl"]  # URL to download the latest ZIP
        filename = Path(download_url).name  # Extract filename from the URL

        print(f"Downloading the latest ZIP file: {filename} from {download_url}")

        # Parse the download URL to extract the host and path
        parsed_url = urllib.parse.urlparse(download_url)
        download_file(parsed_url.hostname, parsed_url.path, filename)

        print(f"File downloaded successfully: {filename}")

    except Exception as error:
        print(f"Error: {error}")

# Call the function to download the latest ZIP file
if __name__ == "__main__":
    download_latest_zip()
