import requests, re, time
from bs4 import BeautifulSoup
from UserAgentReplica import UserAgent


def get_token():
    s = requests.session()
    s.headers.update(
        {
            "User-Agent": UserAgent().chrome(),
            "Accept": "application/json",
            "Origin": "https://freeimage.host",
            "Referer": "https://freeimage.host/",
        }
    )
    p = s.get("https://freeimage.host/").text
    soup = BeautifulSoup(p, "html.parser")
    script_tag = soup.find("script", string=re.compile(r"PF\.obj\.config\.auth_token"))

    if script_tag:
        token_match = re.search(
            r'PF\.obj\.config\.auth_token\s*=\s*"([^"]+)"', script_tag.string
        )

        if token_match:
            auth_token = token_match.group(1)
            return auth_token, s
        else:
            return "", ""
    else:
        return "", ""


def freeimage(file_n, file_binary, mime_type, n=0):
    auth_token, session = get_token()
    if auth_token == "":
        if n == 5:
            return None
        freeimage(file_n, file_binary, mime_type, n=n + 1)
    payload = {
        "type": "file",
        "action": "upload",
        "timestamp": str(int(time.time() * 1000)),
        "auth_token": auth_token,
    }
    try:
        files = {"source": (file_n, file_binary, mime_type)}
        upload_response = session.post(
            "https://freeimage.host/json", data=payload, files=files
        )
        return upload_response.json()["image"]["url"]
    except Exception:
        return None
