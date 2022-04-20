from typing import List
import json
import requests
import pandas as pd
from datetime import datetime

from utils import request_to_json, get_repo_names

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


class GitHubPR:
    """
    Get information about Pull requests.
    """

    def __init__(self, repo: str = None, pr_number: str = None):
        self.repo = repo
        self.pr_number = pr_number

    def get_files_from_pr(self, repo: str = None, pr_number: int = None) -> List[dict]:
        """
        Get files changed from specific PR.

        Args:
            repo (str, optional): Repository name. Defaults to None.
            pr_number (int, optional): Pull request number. Defaults to None.

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

    def get_commits_from_pr(
        self, repo: str = None, pr_number: int = None
    ) -> List[dict]:
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
            pr_number (int, optional): Pull request number. Defaults to None.

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

    def union_dfs_task(self, dfs) -> pd.DataFrame:
        return pd.concat(dfs, ignore_index=True)

    # check if needed
    def combine_all_pr_info(self) -> pd.DataFrame:
        """
        Combine all informations from PR into one data frame.

        Returns:
            pd.DataFrame: DF containing information about commits and files.
        """
        commits_df = self.commits_to_df(self.get_commits_from_pr())
        files_df = self.files_to_df(self.get_files_from_pr())

        combined_df = self.union_dfs_task([files_df, commits_df])
        return combined_df


class GitHubFlow:
    """
    For getting all informations per contributor.
    """

    def __init__(self):
        # self.repo_names = get_repo_names()
        self.contributor_info = GitHubUsers()
        self.pr_info = GitHubPR()

    def get_prs_per_user(self, contributor: str = None, repo: str = None) -> dict:
        """
        List all pull requests per pointed user from repository.

        Args:
            contributor (str, optional): Contributor name. Defaults to None.
            repo (str, optional): Repo name. Defaults to None.

        Returns:
            dict: Dictionary included all PRs per contributor from specific repository.
        """
        url = f"https://api.github.com/search/issues?q=is:pr+repo:dyvenia/{repo}+author:{contributor}"
        pr_info = request_to_json(url)
        final_dict_per_user = {}
        try:
            for ind in range(len(pr_info["items"])):
                dict_per_user = {
                    "contributor": contributor,
                    "repo": repo,
                    "number": pr_info["items"][ind]["number"],
                    "title": pr_info["items"][ind]["title"],
                }

                final_dict_per_user[pr_info["items"][ind]["id"]] = dict_per_user

        except KeyError as e:
            print(f"For {contributor} : {e} is not found")

        return final_dict_per_user

    def list_all_pr_per_contributors(self, dict_repo_login: dict = None) -> List[dict]:
        """
        List combined pull requests per every

        Args:
            dict_repo_login (dict, optional): Each contribution that occurs in a given organization.
            The contributor is the key. The value is the repository list that the user contributes. Defaults to None.

        Returns:
            List[dict]: List of dictionaries. Key is the PR id. Info about specific PR in a value.
        """
        list_of_dict_prs = []
        for key, value in dict_repo_login.items():
            for repo in value:
                dict_pr = self.get_prs_per_user(key, repo)
                list_of_dict_prs.append(dict_pr)
        return list_of_dict_prs

    def create_pairs_contributor_repo(self, df_repo_login: pd.DataFrame = None) -> dict:
        """
        Create pairs contributor-repository. Pairing for each contribution that occurs in a given organization.

        Args:
            df_repo_login (pd.DataFrame, optional): Each contribution that occurs in a given organization. Defaults to None.

        Returns:
            dict: The contributor is the key. The value is the repository list that the user contributes.
        """
        dict_repo_login = {}
        dict_repo_login_raw = df_repo_login.to_dict("records")

        for dct in dict_repo_login_raw:
            try:
                dict_repo_login[dct["login"]].append(dct["repo"])
            except KeyError:
                dict_repo_login[dct["login"]] = [dct["repo"]]

        return dict_repo_login

    def run(self):
        # temporary - to minimize the number of requests
        repo_names = [
            "dyvenia",
            "elt_workshop",
            "git-workshop",
            "gitflow",
            "notebooks",
            "timeflow",
            "timeflow_ui",
            "timelogs",
            "viadot",
        ]

        df_all_contributions = self.contributor_info.get_all_contributions(repo_names)
        dict_repo_login = self.create_pairs_contributor_repo(
            df_all_contributions[["repo", "login"]]
        )
        list_of_dict_prs = self.list_all_pr_per_contributors(dict_repo_login)

        df_transformed = pd.DataFrame(
            [list_of.values() for list_of in list_of_dict_prs]
        )
        df = pd.DataFrame()
        for x in df_transformed.columns:
            df = pd.concat([df, df_transformed[x].apply(pd.Series)])

        return df[["contributor", "repo", "number", "title"]].dropna()
