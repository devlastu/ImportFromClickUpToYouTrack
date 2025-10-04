import logging
import pprint
from typing import Dict, Optional
from src.mappers.issue_mapper import IssueMapper
from src.mappers.field_strategies import DescriptionStrategy, StateStrategy, AssigneeStrategy, SummaryStrategy

from src.clients.youtrack_client import YouTrackClient

log = logging.getLogger("gh2yt.services.issue")


class IssueService:
    """
    Service for handling YouTrack issues.

    This class provides CRUD operations for YouTrack issues,
    including creating, updating, and retrieving issues.
    It uses IssueMapper to map GitHub issue data to YouTrack's format.

    Attributes:
        yt (YouTrackClient): Client for interacting with the YouTrack API.
        project_id (str): The YouTrack project ID.
        project_short (str): Short identifier of the project in YouTrack.
        mapper (IssueMapper): Mapper for transforming GitHub issue fields into YouTrack format.
    """
    def __init__(self, yt_client: YouTrackClient, project_id: str, project_short: str):
        self.yt = yt_client
        self.project_id = project_id
        self.project_short = project_short

        self.mapper = IssueMapper([
            SummaryStrategy(),
            DescriptionStrategy(),
            StateStrategy(),
            AssigneeStrategy()
        ])

    def create_issue(self, issue: dict) -> Optional[dict]:
        """
        Creates a new issue from dict(JSON) in YouTrack.
        """
        payload = self.mapper.map_create(issue, self.project_id)
        try:
            return self.yt.create_issue(payload)
        except Exception as e:
            log.error(f"Error creating issue: {e}")
            return None

    def update_issue(self, current_issue: dict, new_issue: dict, yt_id: str) -> Optional[dict]:
        """
        Updates an existing YouTrack issue if there are changes.

        Args:
            current_issue (dict): Current issue data retrieved from YouTrack.
            new_issue (dict): New issue data retrieved from GitHub.
            yt_id (str): YouTrack issue ID.

        Returns:
            Optional[dict]: Updated issue data from YouTrack, or None if no changes were detected.
        """
        payload = self.mapper.map_update(current_issue, new_issue)

        if not payload:
            log.info(f"No changes detected for issue with ID-{yt_id} | Number {new_issue['number']}")
            return None
        else:
            log.info(f"Updated issue with ID-{yt_id} | Number {new_issue['number']}")
        try:
            return self.yt.update_issue(yt_id, payload)
        except Exception as e:
            log.error(f"Error triying to update issue with ID-{yt_id} | Number {new_issue['number']}: {e}")
            return None

    def get_issue(self, yt_id: str) -> Optional[dict]:
        """
        Retrieves an issue from YouTrack by its ID.
        """
        try:
            return self.yt.get_issue(yt_id, fields="id,summary,description,customFields(name,value(name,login))")
        except Exception as e:
            log.error(f"Error getting issue ID-{yt_id}: {e}")
            return None

    def find_existing_issue_id(self, number: int) -> Optional[str]:
        """
        Finds the ID of an existing issue based on its summary.

        Args:
            summary (str): Summary text of the issue.

        Returns:
            Optional[str]: ID of the existing issue if found, otherwise None.
        """
        try:
            return self.mapper.get_existing_issue_id(self.yt, self.project_short, number=number)
        except Exception as e:
            log.error(f"Error finding issue '{number}': {e}")
            return None

