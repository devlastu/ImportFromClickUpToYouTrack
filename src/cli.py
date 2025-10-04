import argparse
import logging
import os
import sys

from src.clients.github_client import GitHubClient
from src.clients.youtrack_client import YouTrackClient
from src.services.service_orchestrator import ServiceOrchestrator
from src.synchronizers.issue_synchronizer import IssueSynchronizer


import src.config as config
from src.logging_config import configure_logging

configure_logging()
log = logging.getLogger("gh2yt")


def main():
    """
    Main entry point for the CLI application.

    This function parses command-line arguments, configures
    GitHub and YouTrack clients, sets up the service orchestrator
    and synchronizer, and runs either a one-time import or
    continuous synchronization of GitHub issues into YouTrack.

    CLI Arguments:
       --repo: GitHub repository in format owner/repo (required)
       --project: YouTrack project ID or shortName (required)
       --state: GitHub issue state filter ('open', 'closed', 'all')
       --dry-run: Simulate import without creating/updating issues
       --limit: Limit number of issues (0 = all issues)
       --sync: Enable continuous synchronization mode
       --interval: Interval in seconds between syncs (default=60)
    """

    parser = argparse.ArgumentParser(
        description="Import GitHub issues to YouTrack and optionally synchronize them."
    )

    parser.add_argument("--repo", required=True, help="GitHub repo in format owner/repo")
    parser.add_argument("--project", required=True, help="YouTrack project ID or shortName")
    parser.add_argument(
        "--state",
        default="all",
        choices=["open", "closed", "all"],
        help="Filter GitHub issues by state"
    )
    parser.add_argument("--dry-run", action="store_true", help="Simulate import without creating issues")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of issues (0 = all)")
    parser.add_argument("--sync", action="store_true", help="Enable continuous synchronization")
    parser.add_argument("--interval", type=int, default=60, help="Sync interval in seconds")

    args = parser.parse_args()

    log.info("CLI arguments: %s", args)


    github_token = config.GITHUB_TOKEN or os.getenv("GITHUB_TOKEN")
    youtrack_token = config.YOUTRACK_TOKEN or os.getenv("YOUTRACK_TOKEN")

    if not youtrack_token:
        log.error("YouTrack token is required. Set it in config or environment variable.")
        sys.exit(1)

    log.info("GitHub token: %s", github_token[:5] + "..." if github_token else "None")
    log.info("YouTrack URL: %s", config.YOUTRACK_URL)
    log.info("YouTrack Project ID: %s", config.YOUTRACK_PROJECT_ID)


    gh = GitHubClient(token=github_token)
    yt = YouTrackClient(base_url=config.YOUTRACK_URL, token=youtrack_token)


    orchestrator = ServiceOrchestrator(
        yt_client=yt,
        project_short=args.project,
        project_id=config.YOUTRACK_PROJECT_ID
    )


    syncer = IssueSynchronizer(gh_client=gh, service_orchestrator=orchestrator)

    if args.sync:
        log.info("Starting synchronization mode (continuous)...")
        syncer.sync(
            repo=args.repo,
            state=args.state,
            interval=args.interval,
            once=False,
            dry_run=args.dry_run,
            limit=args.limit if args.limit > 0 else None,
        )
    else:
        log.info("Starting one-time import (sync once)...")
        syncer.sync(
            repo=args.repo,
            state=args.state,
            once=True,
            dry_run=args.dry_run,
            limit=args.limit if args.limit > 0 else None,
        )


if __name__ == "__main__":
    # Example invocation for testing/debugging
    sys.argv = [
        "cli.py",
        "--repo", "devlastu/ImportFromClickUpToYouTrack",
        "--project", "GS",
        "--sync",
        "--interval", "10",
        # "--limit", "1"
    ]
    main()
