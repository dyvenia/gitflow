from typing import List
import json
import requests
import pandas as pd
from datetime import datetime

from utils import request_to_json

BASE_URL = "https://api.github.com/"


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

    def get_files_from_pr(self, repo: str = None, pr_number: int = None) -> List[dict]:
        """
        Get files changed from specific PR.

        Args:
            repo (str, optional): Repository name. Defaults to None.
            pr_number (int, optional):Pull request number. Defaults to None.

        Returns:
            List[dict]: List of dicts
        """
        repo = repo or self.repo
        pr_number = pr_number or self.pr_number
        url = f"repos/dyvenia/{repo}/pulls/{pr_number}/files"
        result = request_to_json(BASE_URL + url)
        list_dict_pr = []
        for i in range(len(result)):
            res_json = result[i]
            dict_pr = {
                "filename": res_json["filename"].split("/")[-1],
                "path_to_file": res_json["filename"],
                "pr_number": pr_number,
                "repo": repo,
                "status": res_json["status"],
                "additions": res_json["additions"],
                "deletions": res_json["deletions"],
                "changes": res_json["changes"],
            }
            list_dict_pr.append(dict_pr)
        return list_dict_pr

    def files_to_df(self, files: List[dict] = None) -> pd.DataFrame:
        """
        Get all changed files for pull request and convert to DF.
        """
        return pd.DataFrame(files)

    def get_commit_from_pr(self, repo: str = None, pr_number: int = None) -> List[dict]:
        """
        Get info about commits from specific PR.

        Args:
            repo (str, optional): Repository name. Defaults to None.
            pr_number (int, optional):Pull request number. Defaults to None.

        Returns:
            List[dict]: List of dictionaries
        """
        repo = repo or self.repo
        pr_number = pr_number or self.pr_number
        url = f"repos/dyvenia/{repo}/pulls/{pr_number}/commits"
        result = request_to_json(BASE_URL + url)

        list_dict_pr = []
        for i in range(len(result)):
            res_json = result[i]
            commit = res_json["commit"]
            dict_pr = {
                "author": commit["author"]["name"],
                "pr_number": pr_number,
                "date_commit": commit["author"]["date"],
                "message": commit["message"],
                "comment_count": commit["comment_count"],
            }
            list_dict_pr.append(dict_pr)
        return list_dict_pr

    def commits_to_df(self, commits: List[dict] = None) -> pd.DataFrame:
        """
        Get all commits for pull request and convert to DF.
        """
        return pd.DataFrame(commits)

    def str_to_datetime(self, date_str: str = None) -> datetime:
        """
        Convert string to datetime.

        Args:
            date_str (str, optional): Date in string format. Defaults to None.

        Returns:
            datetime: Date in datetime format
        """
        date_str_new = " ".join(date_str.split("T"))
        return datetime.fromisoformat(date_str_new[:-1])

    def combine_pr_info_to_df(
        self, repo: str = None, pr_number: int = None
    ) -> pd.DataFrame:
        """
        Collect information about pull request. PR info, how long have been opened, create and close date.

        Args:
            repo (str, optional): Repository name. Defaults to None.
            pr_number (int, optional):Pull request number. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe with information about pull request.
        """
        repo = repo or self.repo
        pr_number = pr_number or self.pr_number
        url = f"repos/dyvenia/{repo}/pulls/{pr_number}"
        result = request_to_json(BASE_URL + url)

        if result["closed_at"] is not None:
            created = self.str_to_datetime(result["created_at"])
            closed = self.str_to_datetime(result["closed_at"])
            duration_days = (closed - created).days
        else:
            duration_days = 0

        dict_general = {
            "pr_name": result["title"],
            "pr_number": pr_number,
            "state": result["state"],
            "created_at": result["created_at"],
            "updated_at": result["updated_at"],
            "closed_at": result["closed_at"],
            "merged_at": result["merged_at"],
            "duration_days": duration_days,
        }

        return pd.DataFrame(dict_general, index=[0])
