import requests


class YouTrackClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        # Hub API base (used for users, groups, permissions)
        self.hub_url = self.base_url.replace("/youtrack", "/hub")
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    # --- Issues ---
    def get_issue(self, issue_id: str, fields: str = None) -> dict:
        """
        Fetch a single issue by ID.
        """
        params = {"fields": fields} if fields else {}
        url = f"{self.base_url}/api/issues/{issue_id}"
        resp = requests.get(url, headers=self.headers, params=params)
        resp.raise_for_status()
        return resp.json()

    def create_issue(self, payload: dict) -> dict:
        """
        Create a new issue in YouTrack.
        """
        url = f"{self.base_url}/api/issues"
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    def update_issue(self, issue_id: str, payload: dict) -> dict:
        """
        Update an existing issue by ID.
        """
        url = f"{self.base_url}/api/issues/{issue_id}"
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    def search_issues(self, query: str, fields: str = None, top: int = 1) -> list:
        """
        Search issues by YouTrack query language.
        """
        params = {"query": query, "fields": fields, "$top": top}
        url = f"{self.base_url}/api/issues"
        resp = requests.get(url, headers=self.headers, params=params)
        resp.raise_for_status()
        return resp.json()

    # --- Users ---
    def get_users(self) -> list[dict]:
        """
        Get all users with basic info.
        """
        url = f"{self.base_url}/api/users?fields=id,ringId,login,name"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_or_create_user(self, login: str, name: str = None) -> dict:
        """
        Get a user by login or create one in Hub if it does not exist.
        """
        users = [u for u in self.get_users() if u.get("login") == login]
        if users:
            return users[0]

        if not name:
            name = login

        url = f"{self.hub_url}/api/rest/users?fields=id,ringId,login,name"
        payload = {"login": login, "name": name}
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    def assign_user_to_issue(self, issue_id: str, user_id: str) -> dict:
        """
        Assign a user to an issue.
        NOTE: YouTrack requires `id` or `ringId`, not login.
        """
        url = f"{self.base_url}/api/issues/{issue_id}/assignee"
        payload = {"id": user_id}
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    # --- Groups ---
    def get_groups(self) -> list[dict]:
        """
        Fetch all user groups (so you can pick group_id to assign users to).
        """
        url = f"{self.hub_url}/api/rest/usergroups?fields=id,name"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def add_user_to_group(self, user_id: str, group_id: str) -> dict:
        """
        Add a user to a given group (e.g. Developers, Project Team).
        This is necessary to make them 'Assignable' in YouTrack.
        """
        url = f"{self.hub_url}/api/rest/users/{user_id}/groups"
        resp = requests.post(url, headers=self.headers, json={"id": group_id})
        resp.raise_for_status()
        return resp.json()

    # --- Projects ---
    def get_project_ring_id(self, short_name: str) -> str:
        """
        Get a project's ringId (used for Hub API calls).
        """
        url = f"{self.base_url}/api/admin/projects"
        params = {"fields": "id,ringId,shortName,name", "query": short_name}
        resp = requests.get(url, headers=self.headers, params=params)
        resp.raise_for_status()
        projects = resp.json()
        if not projects:
            raise ValueError(f"Project {short_name} not found")
        return projects[0]["ringId"]

    def add_user_to_project(self, project_ring_id: str, user_ring_id: str) -> dict:
        """
        Add user to a project's team (not enough for assignment –
        usually you must also add them to a group with proper permissions).
        """
        url = f"{self.hub_url}/api/rest/projects/{project_ring_id}/team/users"
        resp = requests.post(
            url,
            headers=self.headers,
            json={"id": user_ring_id},
            params={"fields": "id,name"}
        )
        resp.raise_for_status()
        return resp.json()

    # --- Hub helpers ---
    def hub_post(self, path: str, json: dict = None, params: dict = None) -> dict:
        """
        Generic POST to Hub API.
        """
        url = f"{self.hub_url}{path}"
        resp = requests.post(url, headers=self.headers, json=json, params=params)
        resp.raise_for_status()
        return resp.json()

    def hub_get(self, path: str, params: dict = None) -> dict:
        """
        Generic GET to Hub API.
        """
        url = f"{self.hub_url}{path}"
        resp = requests.get(url, headers=self.headers, params=params)
        resp.raise_for_status()
        return resp.json()
