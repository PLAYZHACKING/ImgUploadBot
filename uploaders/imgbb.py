import time, requests, re, bs4
from UserAgentReplica import UserAgent


def imgbb(file_n, file_binary, mime_type):
    url = "https://imgbb.com"
    headers = {
        "User-Agent": UserAgent().chrome(),
        "origin": "https://imgbb.com",
    }
    resp1 = requests.get(url, headers=headers)
    soup = bs4.BeautifulSoup(resp1.text, "html.parser")
    ibbjs = soup.find_all("script", id=None, src=None)
    for i in ibbjs:
        if "auth_token" in str(i):
            match = re.search(r'PF.obj.config.auth_token="([^"]+)"', str(i))
            if match:
                token = match.group(1)
                url2 = url + "/json"
                headers["referer"] = "https://imgbb.com/"
                files = {"source": (file_n, file_binary, mime_type)}
                payload = {
                    "type": "file",
                    "action": "upload",
                    "auth_token": token,
                    "timestamp": str(time.time()).replace(".", "")[:13],
                }
                resp2 = requests.post(url2, headers=headers, data=payload, files=files)
                jsoned = resp2.json()
                if jsoned["status_code"] == 200:
                    return jsoned["image"]["url"]
                else:
                    return None
    return None
