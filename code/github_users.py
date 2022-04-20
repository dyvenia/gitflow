import json
import requests
from typing import List
import pandas as pd

from utils import request_to_json, get_repo_names


class GitHubUsers:
    """
    Get information about contributors and contributions.
    """

    def get_repo_contributors(self, repo: str = None) -> json:
        """
        Get specific repository contributors.

        Args:
            repo (str, optional): Repository name. Defaults to None.

        Returns:
            json: json with all information about contributors.
        """
        url = f"https://api.github.com/repos/dyvenia/{repo}/contributors"
        req = requests.get(url)
        if req.status_code != 200:
            return {}

        return request_to_json(url)

    def get_all_contributions(self, repos: List[str] = None) -> pd.DataFrame:
        """
        Get all contributions for list of repos for all contributors.

        Args:
            repos (List[str], optional): List of repository names. Defaults to None.

        Returns:
            pd.DataFrame: DF
        """
        dfs = []
        for repo in repos:
            contributors = self.get_repo_contributors(repo=repo)
            contrib_dict = {}
            contributor_list = []

            for contrib in contributors:
                if "[bot]" not in contrib["login"]:
                    contrib_dict = {
                        "repo": repo,
                        "login": contrib["login"],
                        "contributions": contrib["contributions"],
                    }
                    contributor_list.append(contrib_dict)
            df_dict = pd.DataFrame(contributor_list)
            dfs.append(df_dict)
        return self.union_dfs_task(dfs)

    def union_dfs_task(self, dfs):
        return pd.concat(dfs, ignore_index=True)
