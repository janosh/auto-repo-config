# Auto Repo Settings

[![Tests](https://github.com/janosh/auto-repo-config/workflows/main/badge.svg)](https://github.com/janosh/auto-repo-config/actions)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/janosh/auto-repo-config/main.svg)](https://results.pre-commit.ci/latest/github/janosh/auto-repo-config/main)
[![License](https://img.shields.io/github/license/janosh/auto-repo-config?label=License)](/license)

> Forked from [`asottile/set-delete-branch-on-merge`](https://github.com/asottile/set-delete-branch-on-merge).

GitHub does not provide a way to change the default settings for new repositories.

This tool runs a periodic GitHub Action to change settings on your repositories if they differ from those specified in [`.repo-config.yaml`](.repo-config.yaml).

To use this:

- Fork this repository
- Create a [personal access token](https://github.com/settings/tokens/new) (PAT) with scopes `repo` and/or `admin:org` depending on if you want to manage your own and/or organizational repos. If you're not sure, just set both.
- Create a repository secret named `GH_TOKEN` and paste in your PAT. If you cloned the repo and want to run the action locally (e.g. for testing), also paste that token into a file `token.py`:

    ```sh
    echo 'GH_TOKEN = "<your_token>"' > gh_token.py
    ```

- Enable GitHub Actions.
- Modify the setting [`.repo-config.yaml`](.repo-config.yaml) to your liking. Consult [these docs](https://docs.github.com/graphql/reference/objects#repository) for the GraphQL names of repo settings and [these docs](https://docs.github.com/rest/reference/repos#update-a-repository) for the REST names of repo settings.
- Enjoy!
