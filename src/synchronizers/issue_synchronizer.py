import pprint
import time
import logging
from typing import Optional
from src.services.issue_service import IssueService

log = logging.getLogger("gh2yt.synchronizer")


class IssueSynchronizer:
    """
    Responsible for synchronizing issues between GitHub and YouTrack.

    This class periodically fetches issues from a GitHub repository and
    synchronizes them with a target YouTrack project using the provided
    orchestrator service.
    """
    def __init__(self, gh_client, service_orchestrator):
        self.gh = gh_client
        self.orchestrator = service_orchestrator

    def sync(self, repo: str, state: Optional[str] = "all", interval: int = 60, once: bool = False, dry_run: bool = False, limit: Optional[int] = None):
        """
        Synchronizes issues from GitHub to YouTrack.

        Fetches issues from the specified repository and either updates
        existing YouTrack issues or creates new ones.

        Args:
            repo (str): GitHub repository in the format "owner/repo".
            state (Optional[str]): Issue state to fetch ("all", "open", "closed").
            interval (int): Time interval between syncs (in seconds).
            once (bool): If True, performs a single synchronization and exits.
            dry_run (bool): If True, logs what would happen without making changes.
            limit (Optional[int]): Maximum number of issues to fetch.

        Returns:
            None
        """
        while True:
            try:
                issues = self.gh.fetch_issues(repo, state=state)
                if limit:
                    issues = issues[:limit]

                log.info("Fetched %d issues from GitHub (state=%s)", len(issues), state)
                for issue in issues:
                    if dry_run:
                        payload = self.orchestrator.map_issue_create(issue)
                        log.info("[dry-run] GH #%s → %s", issue.get("number"), payload.get("summary"))
                        continue

                    self._sync_issue(issue)

                if once:
                    log.info("One-time sync completed.")
                    return

                log.info(f"Sleeping {interval} seconds before next sync...")
                time.sleep(interval)

            except KeyboardInterrupt:
                log.info("Synchronization interrupted by user.")
                break
            except Exception as e:
                log.exception(f"Error during sync: {e}")
                time.sleep(interval)

    def _sync_issue(self, issue: dict):
        """
        Synchronizes a single issue.

        Determines whether the issue already exists in YouTrack and
        updates it if necessary, or creates a new one.

        Args:
           issue (dict): GitHub issue data.

        Returns:
            None
        """
        summary = issue.get("title", "")
        yt_id = self.orchestrator.find_existing_issue_id(summary)

        if yt_id:
            current = self.orchestrator.get_issue(yt_id)
            self.orchestrator.update_issue(current, issue, yt_id)
        else:
            self.orchestrator.create_issue(issue)
