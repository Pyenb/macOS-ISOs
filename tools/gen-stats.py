import requests
from requests.auth import HTTPBasicAuth
import os
import json

qb_urls = [
    {"url": os.getenv("QB_URL_1"), "auth_type": "normal"},
    {"url": os.getenv("QB_URL_2"), "auth_type": "http"},
]

def get_uploaded(qb_url, auth_type):
    session = requests.Session()
    active = False
    total_uploaded = 0

    try:
        response = session.get(qb_url["url"])
        if response.status_code != 200:
            raise Exception("Server not reachable")
        
        if auth_type == "http":
            auth = HTTPBasicAuth(os.getenv("HTTP_USERNAME"), os.getenv("HTTP_PASSWORD"))
            response = session.get(f"{qb_url['url']}/api/v2/torrents/info", auth=auth)
        else:
            response = session.post(f"{qb_url['url']}/api/v2/auth/login", data={"username": os.getenv("QB_USERNAME"), "password": os.getenv("QB_PASSWORD")})
            if response.text != "Ok.":
                raise Exception("Login failed")
            response = session.get(f"{qb_url['url']}/api/v2/torrents/info")

        active = True
        total_uploaded = sum(torrent["uploaded"] for torrent in response.json() if any(keyword.lower() in torrent["name"].lower() for keyword in ["macOS", "OS X"]))
    except Exception as e:
        active = False
        print(f"Error accessing {qb_url['url']}: {e} | Code: {response.status_code}")

    return active, total_uploaded

def bytes_to_human_readable(num_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.2f} TB"

def update_readme(stats):
    readme_path = "README.md"
    with open(readme_path, "r") as file:
        readme_content = file.read()

    start_marker = "<!--- STATS_START --->"
    end_marker = "<!--- STATS_END --->"
    stats_table = f"""
| Server | Active | Total Upload |
|--------|--------|--------------|
| Server1 | {stats['server1']['active']} | {stats['server1']['total_upload']} |
| Server2 | {stats['server2']['active']} | {stats['server2']['total_upload']} |
| **Combined** | - | {stats['combined_total_upload']} |
"""

    new_readme_content = readme_content.split(start_marker)[0] + start_marker + stats_table + end_marker + readme_content.split(end_marker)[1]
    
    with open(readme_path, "w") as file:
        file.write(new_readme_content)

server1_active, server1_total_upload = get_uploaded(qb_urls[0], qb_urls[0]["auth_type"])
server2_active, server2_total_upload = get_uploaded(qb_urls[1], qb_urls[1]["auth_type"])

combined_total_upload = server1_total_upload + server2_total_upload

stats = {
    "server1": {
        "active": "Yes" if server1_active else "No",
        "total_upload": bytes_to_human_readable(server1_total_upload)
    },
    "server2": {
        "active": "Yes" if server2_active else "No",
        "total_upload": bytes_to_human_readable(server2_total_upload)
    },
    "combined_total_upload": bytes_to_human_readable(combined_total_upload)
}

print(json.dumps(stats, indent=2))

update_readme(stats)
