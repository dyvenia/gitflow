from typing import List
import requests


BASE_URL = "https://api.github.com/"


def get_repos_count(url: str = "users/dyvenia") -> int:
    """
    Count public repositories in Dyvenia organisation.

    Args:
        url (str, optional): API url. Defaults to "users/dyvenia".

    Returns:
        int: number of repositories
    """
    test = requests.get(BASE_URL + url)
    result = test.json()
    return result["public_repos"]


def get_repo_names(url: str = "users/dyvenia/repos") -> List[str]:
    """
    Get public repositories names from Dyvenia.

    Args:
        url (str, optional): API url. Defaults to "users/dyvenia/repos".

    Returns:
        List[str]: List of repository names
    """
    repos = requests.get(BASE_URL + url)
    result = repos.json()
    repos = get_repos_count()
    repo_names = [result[num]["name"] for num in range(repos)]
    return repo_names


def request_to_json(url: str = None):
    repos = requests.get(url)
    return repos.json()
