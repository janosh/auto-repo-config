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


def pretty_print(dic: dict) -> None:
    """Pretty print a dictionary in YAML format.
    Useful for development and debugging.
    """
    print(yaml.dump(dic))


def get_gql_query(settings: str, affil: str = "OWNER") -> str:
    """Construct GraphQL query from settings list.

    Args:
        settings (str): Names of repo settings according to the GraphQL API,
            separated by new lines. Use '\n'.join(settings_list).
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
        "{affil}", affil
    )


def load_config(config_path: str = None) -> tuple[dict[str, Any], list[str], bool]:
    """Load .repo-config.(yml|yaml).

    Returns:
        tuple[dict[str, Any], list[str], bool]:
            - Dictionary of GitHub settings to apply to all your repos
            - list of additional logins of your GitHub organizations to query for repos
            - boolean whether or not apply settings to repos you forked as well
    """
    config = {}

    if config_path and not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Path to config file was set as '{config_path}' but no such file exists."
        )
    elif config_path:
        with open(config_path) as file:
            config = yaml.safe_load(file.read())

    for path in (".repo-config.yml", ".repo-config.yaml"):
        if os.path.exists(path):
            with open(path) as file:
                config = yaml.safe_load(file.read())

    if config == {}:
        raise ValueError(
            "No config file could be found. See https://git.io/JWa5o for an example "
            "config file. All fields except 'settings' are optional."
        )

    settings = config["settings"]
    orgs = config["orgs"] or []
    skipForks = config["skipForks"] or True

    return settings, orgs, skipForks
