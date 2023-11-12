import os
from pathlib import Path

import pytest

from helpers import get_gql_query, load_config, query_gh_gpl_api


def test_query_gh_gpl_api() -> None:
    query = """{
        viewer {
            login
        }
    }"""
    response = query_gh_gpl_api(query)
    assert response["viewer"]["login"] == "janosh"

    query = """{
        viewer {
            repositories(first: 3, affiliations: [OWNER]) {
                nodes {
                    name
                }
            }
        }
    }"""
    response = query_gh_gpl_api(query)
    assert len(response["viewer"]["repositories"]["nodes"]) == 3


def test_get_gql_query() -> None:
    settings = [
        "name",
        "nameWithOwner",
        "isArchived",
        "isFork",
        "allowSquashMerge",
        "deleteBranchOnMerge",
    ]
    settings_str = "\n".join(settings)
    affiliations = "foobar"

    query = get_gql_query(settings_str, affiliations)
    assert query.count(settings_str) == 2

    assert query.count(affiliations) == 1


@pytest.mark.parametrize("skip_forks", ["true", "false"])
def test_load_config(tmp_path: Path, skip_forks: str) -> None:
    os.chdir(tmp_path)

    # raises if default file name for config is not found
    with pytest.raises(FileNotFoundError):
        load_config()

    config_file = tmp_path / ".repo-config.yml"
    config_file.write_text(
        f"""
    skipForks: {skip_forks}
    orgs: [super-secret-org]
    settings:
        deleteBranchOnMerge:
            restName: delete_branch_on_merge
            value: true
        mergeCommitAllowed:
            restName: allow_merge_commit
            value: false
        autoMergeAllowed:
            restName: allow_auto_merge
            value: true
        hasWikiEnabled:
            restName: has_wiki
            value: false
    """,
    )
    settings, orgs, loaded_skip_forks = load_config(str(config_file))

    assert str(loaded_skip_forks).lower() == skip_forks
    assert orgs == ["super-secret-org"]
    assert settings["deleteBranchOnMerge"]["value"] is True

    # raises if custom file name for config is not found even though default is present
    with pytest.raises(FileNotFoundError):
        load_config("non-existent-file.yml")
