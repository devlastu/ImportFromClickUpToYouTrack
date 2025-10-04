import logging
import pprint
from typing import Optional
from src.clients.youtrack_client import YouTrackClient

log = logging.getLogger("gh2yt.services.project")


class ProjectService:
    """
    Service for managing YouTrack projects.

    This class provides utility methods for interacting with YouTrack projects,
    including retrieving project ring IDs, checking user membership, and adding users
    to project teams.

    Attributes:
        yt (YouTrackClient): Client for interacting with the YouTrack API.
    """

    def __init__(self, yt_client: YouTrackClient):
        self.yt = yt_client

    def get_project_ring_id(self, short_name: str) -> Optional[str]:
        """
        Retrieves the ring ID of a project given its short name.

        Args:
            short_name (str): Short name of the project in YouTrack.

        Returns:
            Optional[str]: Ring ID of the project if found; otherwise, None.
        """
        try:
            params = {"fields": "id,ringId,shortName,name", "query": short_name}
            log.debug(f"[YT][Project] Fetching project by shortName='{short_name}' with params={params}")
            projects = self.yt.hub_get("/api/admin/projects", params=params)

            log.debug(f"[YT][Project] Response projects={projects}")
            if projects:
                return projects[0].get("ringId")
            log.warning(f"[YT][Project] Project with shortName '{short_name}' not found.")
        except Exception as e:
            log.error(f"[YT][Project] Error fetching project '{short_name}': {e}", exc_info=True)
        return None

    def is_user_in_project(self, project_short: str, user_ring_id: str) -> bool:
        """
        Checks whether a user is a member of a given project.

        Args:
            project_short (str): Short name of the project in YouTrack.
            user_ring_id (str): Ring ID of the user.

        Returns:
            bool: True if the user is a member of the project, False otherwise.
        """
        try:
            ring_id = self.get_project_ring_id(project_short)
            if not ring_id:
                log.error(f"Cannot get ringId for project '{project_short}'")
                return False

            path = f"/hub/api/rest/projects/{ring_id}/team/users"
            members = self.yt.hub_get(path, params={"fields": "id,login"})

            log.debug(f"[YT][Project] Members in project '{project_short}': {members}")

            for member in members.get("users", []):
                if member.get("id") == user_ring_id:
                    log.debug(f"[YT][Project] User ringId={user_ring_id} is already in project '{project_short}'")
                    return True
        except Exception as e:
            log.error(f"Error checking if user is in project '{project_short}': {e}", exc_info=True)
        return False

    def add_user_to_project_team(self, project_short: str, user_ring_id: str) -> bool:
        """
        Adds a user to a YouTrack project's team.

        Args:
            project_short (str): Short name of the project in YouTrack.
            user_ring_id (str): Ring ID of the user to add.

        Returns:
            bool: True if the user was successfully added; False otherwise.
        """
        try:
            ring_id = self.get_project_ring_id(project_short)
            if not ring_id:
                log.error(f"[YT][Project] Could not get ringId for project '{project_short}'")
                return False

            path = f"/hub/api/rest/projects/{ring_id}/team/users"
            payload = {"id": user_ring_id}
            params = {"fields": "name,id"}
            log.debug(f"[YT][Project] Adding user ringId={user_ring_id} to project '{project_short}' -> path={path}, payload={payload}")

            response = self.yt.hub_post(path, json=payload, params=params)
            log.info(f"[YT][Project] User ringId={user_ring_id} added to project '{project_short}'. Response={response}")
            return True
        except Exception as e:
            log.error(f"[YT][Project] Error adding user ringId={user_ring_id} to project '{project_short}': {e}", exc_info=True)
            return False


