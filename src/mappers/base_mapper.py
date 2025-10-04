import requests
from dateutil import parser as dateparser
import logging
from urllib.parse import quote

log = logging.getLogger("gh2yt.mapper")

class BaseMapper:
    @staticmethod
    def format_description(issue) -> str:
        """Formating description for issue"""
        summary = issue.get("title", "No title")
        number = issue.get("number")
        github_url = issue.get("html_url")
        body = issue.get("body") or ""
        created_at = issue.get("created_at")
        try:
            created = dateparser.parse(created_at).isoformat() if created_at else ""
        except Exception as e:
            log.warning(f"Failed to parse creation date '{created_at}': {e}")
            created = created_at

        return (
            f"**Imported from GitHub**\n"
            f"Issue: {github_url}\n"
            f"Number: {number}\n"
            f"Created: {created}\n\n"
            f"---\n\n{body}"
        )

    @classmethod
    def get_existing_issue_id(cls, yt_client, project_short: str, number: int) -> str | None:
        """Search for existing issue in YouTrack by issue number"""
        try:
            query = f'project: {project_short} number: {number}'
            issues = yt_client.search_issues(query=query, fields="id, idReadable, summury", top=1)
            if issues:
                return issues[0].get("id")
            return None
        except Exception as e:
            log.error(f"Greška pri pretrazi issues: {e}")
            return None



