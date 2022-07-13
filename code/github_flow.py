from typing import List
import pandas as pd

from utils import request_to_json, get_repo_names
from github_pr import GitHubPR
from github_users import GitHubUsers

# temporary - to minimize the number of requests
REPO_NAMES = [
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
                if pr_info["items"][ind]["closed_at"] is not None:
                    created = self.pr_info.str_to_datetime(
                        pr_info["items"][ind]["created_at"]
                    )
                    closed = self.pr_info.str_to_datetime(
                        pr_info["items"][ind]["closed_at"]
                    )
                    duration_days = (closed - created).days
                else:
                    duration_days = 0

                dict_per_user = {
                    "contributor_name": contributor,
                    "repo_name": repo,
                    "pr_number": pr_info["items"][ind]["number"],
                    "title": pr_info["items"][ind]["title"],
                    "created_at": pr_info["items"][ind]["created_at"],
                    "updated_at": pr_info["items"][ind]["updated_at"],
                    "closed_at": pr_info["items"][ind]["closed_at"],
                    # "merged_at": pr_info["items"][ind]["merged_at"],
                    "duration_days": duration_days,
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

    def run_pr_info(self) -> pd.DataFrame:
        """
        Method to generate DataFrame with information about all pull requests.
        DataFrame contains information about PR name and PR number per user and repository where he contributes.

        Returns:
            pd.DataFrame: Data Frame["contributor", "repo", "number", "title"].
        """
        df_all_contributions = self.contributor_info.get_all_contributions(REPO_NAMES)
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

        return df[
            [
                "contributor_name",
                "repo_name",
                "pr_number",
                "title",
                "created_at",
                "updated_at",
                "closed_at",
                "duration_days",
            ]
        ].dropna()

    def run_commit_info(self) -> pd.DataFrame:
        """
        Method to generate DataFrame with information about all commits from pull requests.
        DataFrame contains information about author, pr_number, message and date_commit.

        Returns:
            pd.DataFrame: Data Frame["author", "pr_number", "date_commit", "message", "comment_count"].
        """
        df = self.run_pr_info()
        dict_pr_number_repo = {
            row["pr_number"]: row["repo_name"] for _, row in df.iterrows()
        }
        df_combined = pd.DataFrame()
        try:
            for pr_number, repo in dict_pr_number_repo.items():
                df_commits = self.pr_info.commits_to_df(
                    self.pr_info.get_commits_from_pr(repo, pr_number)
                )
                df_combined = pd.concat([df_combined, df_commits])
        except Exception as e:
            print("Exception in get_commits_from_pr - ", e)
            df_combined = pd.concat([df_combined, pd.DataFrame()])

        return df_combined

    def run_files_info(self) -> pd.DataFrame:
        """
        Method to generate DataFrame with information about all files changed in pull requests.
        DataFrame contains information about filename, path_to_file, pr_number, repo name, status
        what happend with the file (additions, deletions, changes).

        Returns:
            pd.DataFrame: Data Frame["filename", "path_to_file", "pr_number",
            "repo", "status", "additions","deletions", "changes"].
        """
        df = self.run_pr_info()
        dict_pr_number_repo = {
            row["pr_number"]: row["repo_name"] for _, row in df.iterrows()
        }
        df_combined = pd.DataFrame()
        try:
            for pr_number, repo in dict_pr_number_repo.items():
                df_commits = self.pr_info.files_to_df(
                    self.pr_info.get_files_from_pr(repo, pr_number)
                )
                df_combined = pd.concat([df_combined, df_commits])
        except Exception as e:
            print("Exception in get_files_from_pr - ", e)
            df_combined = pd.concat([df_combined, pd.DataFrame()])

        return df_combined
