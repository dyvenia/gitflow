from typing import List
import requests

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
