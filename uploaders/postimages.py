import requests
import time
import random
from bs4 import BeautifulSoup
from UserAgentReplica import UserAgent


def postimages(file_n, file_binary, mime_type):
    session = requests.Session()
    base_url = "https://postimages.org/"
    session.get(base_url)
    upload_session = str(int(time.time() * 1000)) + str(random.random())[1:]
    headers = {
        "priority": "u=1, i",
        "sec-gpc": "1",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://postimages.org",
        "Referer": "https://postimages.org/",
        "User-Agent": UserAgent().chrome(),
    }
    payload = {
        "gallery": "",
        "optsize": "0",
        "expire": "0",
        "numfiles": "1",
        "upload_session": upload_session,
    }

    try:

        files = {"file": (file_n, file_binary, mime_type)}
        response = session.post(
            "https://postimages.org/json",
            data=payload,
            files=files,
            headers=headers,
        )
        resp = response.json()
        if "url" in resp:
            try:
                url = resp["url"]
                webpage = session.get(url)
                soup = BeautifulSoup(webpage.content, "html.parser")
                url = soup.find("input", {"type": "text", "id": "direct"})
                return url["value"]
            except:
                return None
        return None

    except FileNotFoundError:
        return None
    except Exception as e:
        return None
