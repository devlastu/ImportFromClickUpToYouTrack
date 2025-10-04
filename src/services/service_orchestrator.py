import logging
from src.clients.youtrack_client import YouTrackClient
from src.services.user_service import UserService
from src.services.issue_service import IssueService
from src.services.project_service import ProjectService

log = logging.getLogger("gh2yt.orchestrator")


class ServiceOrchestrator:
    """
    Orchestrates interaction between different services:
    - AssignmentService: ensures users exist in YouTrack
    - ProjectService: ensures users are part of a project team
    - IssueService: handles creation and updates of issues
    """

    def __init__(self, yt_client: YouTrackClient, project_short: str, project_id: str):
        self.project_service = ProjectService(yt_client)
        self.user_service = UserService(yt_client)
        self.issue_service = IssueService(yt_client, project_id, project_short)
        self.project_short = project_short
        self.project_id = project_id


    def find_existing_issue_id(self, summary: str):
        """Searches for an issue by summary text"""
        return self.issue_service.find_existing_issue_id(summary)

    def get_issue(self, yt_id: str):
        """Fetches an existing issue by its YouTrack ID"""
        return self.issue_service.get_issue(yt_id)

    def update_issue(self, current: dict, new_issue: dict, yt_id: str):
        """
        Ensures assignee is valid before updating an issue.
        Passes the prepared issue to IssueService.
        """
        new_issue = self._prepare_assignee(new_issue)
        return self.issue_service.update_issue(current, new_issue, yt_id)

    def create_issue(self, issue: dict):
        """
        Ensures assignee is valid before creating an issue.
        Passes the prepared issue to IssueService.
        """
        issue = self._prepare_assignee(issue)
        return self.issue_service.create_issue(issue)


    def _prepare_assignee(self, issue: dict) -> dict:
        """
        Validates and prepares the assignee for the given issue:
        1. Checks if the assignee is provided
        2. Ensures the user exists in YouTrack (creates if missing)
        3. Ensures the user is part of the project team (adds if missing)
        4. If user cannot be validated, clears the assignee field
        """
        if not issue.get("assignee"):
            return issue

        assignee_login = issue["assignee"].get("login")
        assignee_name = issue["assignee"].get("name")

        if not assignee_login:
            return issue

        user = self.user_service.ensure_user_exists(assignee_login, assignee_name)
        if not user:
            log.warning(f"Assignee '{assignee_login}' could not be created/found -> removing assignee")
            issue["assignee"] = None
            return issue

        ring_id = user.get("ringId")
        if not self.project_service.is_user_in_project(self.project_short, ring_id):
            if not self.project_service.add_user_to_project_team(self.project_short,ring_id):
                log.warning(f"User '{assignee_login}' could not be added to project '{self.project_short}' -> removing assignee")
                issue["assignee"] = None

        return issue
