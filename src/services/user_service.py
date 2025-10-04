import logging
from typing import Optional
from src.clients.youtrack_client import YouTrackClient

log = logging.getLogger("gh2yt.services.assignment")


class UserService:
    """
    Service for managing YouTrack users.

    This class provides helper methods for verifying user existence,
    retrieving user details, and ensuring that users exist in YouTrack.

    Attributes:
        yt (YouTrackClient): Client for interacting with the YouTrack API.
    """
    def __init__(self, yt_client: YouTrackClient):
        self.yt = yt_client

    def is_valid_user(self, login: str) -> bool:
        """
        Checks if a user with the given login exists in YouTrack.

        Args:
            login (str): Login name of the user.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        try:
            users = self.yt.get_users()
            return any(user.get("login") == login for user in users)
        except Exception as e:
            log.error(f"Error checking user '{login}': {e}")
            return False

    def get_user_ring_id(self, login: str) -> Optional[str]:
        """
        Retrieves the ring ID of a user given their login.

        Args:
            login (str): Login name of the user.

        Returns:
            Optional[str]: Ring ID if the user exists, None otherwise.
        """
        try:
            users = self.yt.get_users()
            for user in users:
                if user.get("login") == login:
                    return user.get("ringId")
        except Exception as e:
            log.error(f"Errir retrieving ringId for user '{login}': {e}")
        return None

    def ensure_user_exists(self, login: str, name: Optional[str] = None) -> Optional[dict]:
        """
        Ensures that a user exists in YouTrack, creating the user if necessary.

        Args:
            login (str): Login name of the user.
            name (Optional[str]): Full name of the user (optional).

        Returns:
            Optional[dict]: User object if created or found, None if an error occurred.
        """
        try:
            user = self.yt.get_or_create_user(login = login, name = name)
            return user

        except Exception as e:
            log.error(f"Error creating or retrieving user '{login} '{login}': {e}")
            return None
