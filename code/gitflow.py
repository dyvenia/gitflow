from typing import List
import json
import requests
import pandas as pd
from datetime import datetime

BASE_URL = "https://api.github.com/"


class GitHubRepos:
    """
    Get information about repositories from organisation.
    """

    def get_repos_number(self, url: str = "users/dyvenia") -> int:
        """
        Get number of public repositories from Dyvenia.

        Args:
            url (str, optional): API url. Defaults to "users/dyvenia".

        Returns:
            int: number of repositories
        """
        test = requests.get(BASE_URL + url)
        result = test.json()
        return result["public_repos"]

    def get_repo_names(self, url: str = "users/dyvenia/repos") -> List[str]:
        """
        Get public repositories names from Dyvenia.

        Args:
            url (str, optional): API url. Defaults to "users/dyvenia/repos".

        Returns:
            List[str]: List of repository names
        """
        repos = requests.get(BASE_URL + url)
        result = repos.json()
        repos = self.get_repos_number()
        repo_names = [result[num]["name"] for num in range(repos)]
        return repo_names


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

        return req.json()

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


class GitHubPR:
    """
    Get information about Pull requests.
    """

    def __init__(self, repo, pr_number):
        self.repo = repo
        self.pr_number = pr_number

    def request_to_json(self, url: str = None):
        repos = requests.get(url)
        return repos.json()

    def get_files_from_pr(self) -> List[dict]:
        """
        Get files changed from specific PR.

        Returns:
            List[dict]: List of dicts
        """
        url = f"repos/dyvenia/{self.repo}/pulls/{self.pr_number}/files"
        result = self.request_to_json(BASE_URL + url)
        list_dict_pr = []
        for i in range(len(result)):
            res_json = result[i]
            dict_pr = {
                "filename": res_json["filename"].split("/")[-1],
                "path_to_file": res_json["filename"],
                "pr_number": self.pr_number,
                "repo": self.repo,
                "status": res_json["status"],
                "additions": res_json["additions"],
                "deletions": res_json["deletions"],
                "changes": res_json["changes"],
            }
            list_dict_pr.append(dict_pr)
        return list_dict_pr

    def get_commit_from_pr(self) -> List[dict]:
        """
        Get info about commits from specific PR.

        Returns:
            List[dict]: List of dicts
        """
        url = f"repos/dyvenia/{self.repo}/pulls/{self.pr_number}/commits"
        result = self.request_to_json(BASE_URL + url)

        list_dict_pr = []
        for i in range(len(result)):
            res_json = result[i]
            commit = res_json["commit"]
            dict_pr = {
                "author": commit["author"]["name"],
                "pr_number": self.pr_number,
                "date_commit": commit["author"]["date"],
                "message": commit["message"],
                "comment_count": commit["comment_count"],
            }
            list_dict_pr.append(dict_pr)
        return list_dict_pr
