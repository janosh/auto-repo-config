import os
from typing import Any

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


def get_gql_query(settings: str, affiliations: str = "OWNER") -> str:
    """Construct GraphQL query from settings list.

    Args:
        settings (str): Names of repo settings according to the GraphQL API,
            separated by new lines. Use '\n'.join(settings_list).
        affiliations (str, optional): Comma-separated string of author affiliations to
            their repos. One or several of OWNER, COLLABORATOR, ORGANIZATION_MEMBER.
            Defaults to "OWNER".

    Returns:
        str: GraphQL query.
    """
    return """{
      viewer {
        repositories(first: 100, affiliations: [{affiliations}]) {
          nodes {
            name
            nameWithOwner
            isArchived
            isFork
            {settings}
          }
        }
        organizations(first: 100) {
          nodes {
            login
            repositories(first: 100) {
              nodes {
                name
                nameWithOwner
                isArchived
                isFork
                {settings}
              }
            }
          }
        }
      }
    }""".replace(
        "{settings}", settings
    ).replace(
        "{affiliations}", affiliations
    )


def load_config(config_path: str = None) -> tuple[dict[str, Any], list[str], bool]:
    """Load .repo-config.(yml|yaml).

    Args:
        config_path (str, optional): Path to config file. Defaults to None.

    Raises:
        FileNotFoundError: If config_path does not exist or .repo-config.(yml|yaml) does
            not exist in the current working directory.

    Returns:
        tuple[dict[str, Any], list[str], bool]:
            - Dictionary of GitHub settings to apply to all your repos
            - list of additional logins of your GitHub organizations to query for repos
            - boolean whether or not apply settings to repos you forked as well
    """
    config = {}

    if config_path and not os.path.exists(config_path):
        raise FileNotFoundError(f"{config_path=} does not exist.")
    else:
        for path in (".repo-config.yml", ".repo-config.yaml"):
            if os.path.exists(path):
                config_path = path
        if not config_path:
            raise FileNotFoundError(
                "Could not find .repo-config.(yml|yaml) in the current directory. "
                "Either create them or pass config path explicitly."
            )

    with open(config_path) as file:
        config = yaml.safe_load(file.read())

    settings = config["settings"]
    orgs = config["orgs"] or []
    skipForks = config.get("skipForks", True)

    return settings, orgs, skipForks
