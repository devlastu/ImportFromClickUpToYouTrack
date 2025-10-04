import requests, time, logging
from requests.adapters import HTTPAdapter, Retry
from typing import List, Dict, Optional

log = logging.getLogger("gh2yt")

def make_session():
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429,500,502,503,504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s

class GitHubClient:
    def __init__(self, token: Optional[str] = None, session: Optional[requests.Session] = None):
        self.session = session or make_session()
        self.token = token

    def fetch_issues(self, repo: str, state: str = "all") -> List[Dict]:
        """Fetches issues from a GitHub repository."""
        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"

        url = f"https://api.github.com/repos/{repo}/issues?state={state}&per_page=100"
        issues = []
        while url:
            resp = self.session.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            page_items = resp.json()
            issues.extend([it for it in page_items if "pull_request" not in it])
            url = None
            link = resp.headers.get("Link", "")
            if 'rel="next"' in link:
                for p in link.split(","):
                    if 'rel="next"' in p:
                        url = p.split(";")[0].strip("<> ")
            time.sleep(0.1)
        return issues
