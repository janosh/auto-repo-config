# Auto Repo Settings

[![Tests](https://github.com/janosh/auto-repo-config/workflows/Auto%20Repo%20Config/badge.svg)](https://github.com/janosh/auto-repo-config/actions)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/janosh/auto-repo-config/main.svg)](https://results.pre-commit.ci/latest/github/janosh/auto-repo-config/main)

> Forked from [`asottile/set-delete-branch-on-merge`](https://github.com/asottile/set-delete-branch-on-merge).

GitHub does not provide a way to change the default settings for new repositories.

This tool runs a periodic GitHub Action to change settings on your repos if they differ from those specified in [`.repo-config.yaml`](.repo-config.yaml).

## Usage

1. Fork this repository
2. Create a [personal access token](https://github.com/settings/tokens/new) (PAT) with scopes `repo` and/or `admin:org` depending on if you want to manage your own and/or organizational repos. If you're not sure, just set both.
3. Create a repository secret under 'Settings' > 'Secrets' > 'New repository secret' named `GH_TOKEN` and paste in your PAT. If you cloned the repo and want to run the action locally (e.g. for testing), also paste that token into a file `gh_token.py`:

    ```sh
    echo 'GH_TOKEN = "<your_token>"' > gh_token.py
    ```

4. Modify the settings in [`.repo-config.yaml`](.repo-config.yaml) to your liking. Consult [these docs](https://docs.github.com/graphql/reference/objects#repository) for the GraphQL names of repo settings and [these docs](https://docs.github.com/rest/reference/repos#update-a-repository) for the REST names of repo settings. Both names are necessary at the moment since the GraphQL API is more efficient at fetching only the relevant current settings of your repos but does not yet offer [a mutation](https://docs.github.com/graphql/reference/mutations) to update these settings. This requires a call to the REST API.
5. Wait for the action to trigger automatically every Sunday at 10:00 UTC or trigger it manually by going to the [Actions tab](https://github.com/janosh/auto-repo-config/actions/workflows/schedule.yml) and clicking the "Run workflow" button.
6. Enjoy!

## Files of Interest

- [`.repo-config.yaml`](.repo-config.yaml)
- [`.github/workflows/schedule.yml`](.github/workflows/schedule.yml)
- [`auto_repo_config.py`](auto_repo_config.py)

## GraphiQL Explorer

To get acquainted with the GitHub GraphQL API, check out this [live interface](https://docs.github.com/graphql/overview/explorer) with autocomplete and docs. For example, try running

```gql
{
  viewer {
    repositories(first: 100) {
      nodes {
        name
      }
    }
  }
}
```

to see a list of your repos.
