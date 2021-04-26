import os
from typing import List

import requests
import yaml

if os.path.exists("gh_token.py"):
    from gh_token import GH_TOKEN
else:
    GH_TOKEN = os.environ["GH_TOKEN"]


headers = {"Authorization": f"token {GH_TOKEN}"}


def query_gh_gpl_api(query: str) -> dict:
    """Query the GitHub GraphQL API.

    Args:
        query (str): Multi-line query string. Use triple-quotes. Minimal example:
            '''
            {
              viewer {
                login
              }
            }
            '''

    Raises:
        Exception: If the query returned an error message.

    Returns:
        dict: The data returned by the API.
    """
    response = requests.post(
        "https://api.github.com/graphql", json={"query": query}, headers=headers
    ).json()

    if "errors" in response:
        err = response["errors"][0]["message"]
        raise Exception(f"Request failed with error '{err}'.")
    else:
        return response["data"]


def construct_gql_query(settings: List[str], affil: str = "OWNER") -> str:
    """Construct GraphQL query from settings list.

    Args:
        settings (list[str]): Names of repo settings according to the GraphQL API.
        affil (str, optional): Comma-separated string of author affiliations to their
            repos. One or several of OWNER, COLLABORATOR, ORGANIZATION_MEMBER.
            Defaults to "OWNER".

    Returns:
        str: GraphQL query.
    """
    return """{
        viewer {
            repositories(first: 100, affiliations: [{affil}]) {
                nodes {
                    name
                    nameWithOwner
                    isArchived
                    {settings}
                }
            }
        }
    }""".replace(
        "{settings}", "\n".join(settings)
    ).replace(
        "{affil}", affil
    )


def main() -> int:
    with open(".repo-config.yaml") as file:
        config = yaml.safe_load(file.read())

    query = construct_gql_query(config["settings"].keys())

    repos = query_gh_gpl_api(query)["viewer"]["repositories"]["nodes"]

    count = 0

    for repo in repos:
        # skip archived repos
        if repo["isArchived"]:
            continue
        # also skip repos whose settings already conform to the config
        if all(dic["value"] == repo[key] for key, dic in config["settings"].items()):
            continue

        print(f"processing {repo['nameWithOwner']}... ")

        # send patch request to GitHub REST API to update repo settings
        requests.patch(
            f"https://api.github.com/repos/{repo['nameWithOwner']}",
            # see https://docs.github.com/en/rest/reference/repos
            # for the names of repo settings
            json={d["restName"]: d["value"] for d in config["settings"].values()},
            headers=headers,
        )

        for key, dic in config["settings"].items():
            if dic["value"] != repo[key]:
                print(f"  - changed {key} to {dic['value']}\t")

        print("")
        count += 1

    if count == 0:
        print("Nothing to do, all repos already conformed to config.")
    else:
        print(f"Done! Modified settings on {count:,} repos.")

    return 0


if __name__ == "__main__":
    exit(main())
