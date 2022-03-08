import requests

BASE_URL = "https://api.github.com/"


class GithubRepos:
    def __init__(self):
        pass

    def get_repos_number(self, url: str = "users/dyvenia"):
        """
        Get number of public repositories from Dyvenia.
        """
        test = requests.get(BASE_URL + url)
        result = test.json()
        return result["public_repos"]

    def get_repo_names(self, url: str = "users/dyvenia/repos"):
        """
        Get public repositories names from Dyvenia.
        """
        repos = requests.get(BASE_URL + url)
        result = repos.json()
        repos = self.get_repos_number()
        repo_names = [result[num]["name"] for num in range(repos)]
        return repo_names
