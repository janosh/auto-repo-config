import os
from argparse import ArgumentParser
from collections.abc import Sequence
from importlib.metadata import version

import requests

from helpers import get_gql_query, load_config, query_gh_gpl_api


if os.path.exists("gh_token.py"):
    from gh_token import GH_TOKEN
else:
    GH_TOKEN = os.environ["GH_TOKEN"]


headers = {"Authorization": f"token {GH_TOKEN}"}


def main(argv: Sequence[str] = None) -> int:
    """The auto-repo-config CLI interface.

    Returns:
        int: 0 if auto-repo-config exits successfully else error code.
    """
    parser = ArgumentParser(
        "auto-repo-config",
        description="Periodically run a GitHub Action to change settings on your own "
        "and/or org repos if they differ from those specified in .repo-config.yaml.",
    )

    parser.add_argument(
        "-c",
        "--config",
        help="Specify a custom path to your config file.",
        default=None,
    )

    arc_version = version("auto-repo-config")
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s v{arc_version}"
    )

    args = parser.parse_args(argv)

    settings, org_logins, skipForks = load_config(args.config)

    query = get_gql_query("\n".join(settings))

    result = query_gh_gpl_api(query)

    repos = result["viewer"]["repositories"]["nodes"]
    orgs = result["viewer"]["organizations"]["nodes"]

    accessible_org_logins = [d["login"] for d in orgs]

    for org_login in org_logins:
        if org_login not in accessible_org_logins:
            print(
                f"Warning: The 'orgs' key in .repo-config.yaml includes '{org_login}' "
                "but you do not seem to have access to that org. Accessible "
                f"orgs are {accessible_org_logins}."
            )

    # We first query for all org repos and then do the filtering based on orgs
    # specified in repo-config.yaml so that we only need one request to the GQL API.
    for org in orgs:
        if org["login"] in org_logins:
            org_repos = org["repositories"]["nodes"]
            repos.extend(org_repos)

    count = 0

    for repo in repos:
        # skip archived repos
        if repo["isArchived"]:
            continue
        # skip repos whose settings already conform to the config
        if all(dic["value"] == repo[key] for key, dic in settings.items()):
            continue
        # skip forked repos if config says so
        if skipForks and repo["isFork"]:
            continue

        print(f"processing {repo['nameWithOwner']}... ")

        # send patch request to GitHub REST API to update repo settings
        requests.patch(
            f"https://api.github.com/repos/{repo['nameWithOwner']}",
            # see https://docs.github.com/en/rest/reference/repos
            # for the names of repo settings
            json={d["restName"]: d["value"] for d in settings.values()},
            headers=headers,
        )

        for key, dic in settings.items():
            if dic["value"] != repo[key]:
                print(f"  - changed {key} to {dic['value']}\t")

        print()
        count += 1

    if count == 0:
        print("\nNothing to do, all repos already conformed to config.")
    else:
        print(f"\nDone! Modified settings on {count:,} repos.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
