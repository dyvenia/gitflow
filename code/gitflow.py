from typing import List
import requests
import pandas as pd

BASE_URL = "https://api.github.com/"


class GithubRepos:
    """
    Get information about repositories from organisation.
    """

    def get_repos_number(self, url: str = "users/dyvenia") -> int:
        """
        Get number of public repositories from Dyvenia.
        """
        test = requests.get(BASE_URL + url)
        result = test.json()
        return result["public_repos"]

    def get_repo_names(self, url: str = "users/dyvenia/repos") -> List[str]:
        """
        Get public repositories names from Dyvenia.
        """
        repos = requests.get(BASE_URL + url)
        result = repos.json()
        repos = self.get_repos_number()
        repo_names = [result[num]["name"] for num in range(repos)]
        return repo_names


class GitHubUsers:
    def get_repo_contributors(self, repo: str = None):
        url = f"https://api.github.com/repos/dyvenia/{repo}/contributors"
        req = requests.get(url)
        return req.json()

    def get_all_contributions(self, repos: List[str] = None):
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
