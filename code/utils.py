from typing import List
import requests

BASE_URL = "https://api.github.com/"
USERNAME = "add_username"
TOKEN = "add_token"


def get_repos_count(url: str = "users/dyvenia") -> int:
    """
    Count public repositories in Dyvenia organization.

    Args:
        url (str, optional): Part of the API url path. Defaults to "users/dyvenia".

    Returns:
        int: Number of repositories.
    """
    test = requests.get(BASE_URL + url)
    result = test.json()
    return result["public_repos"]


def get_repo_names(org_name: str = "dyvenia") -> List[str]:
    """
    Get public repositories names from Dyvenia.

    Args:
        org_name (str, optional): Organization name. Defaults to "dyvenia".

    Returns:
        List[str]: List of repository names.
    """
    repos = requests.get(BASE_URL + f"users/{org_name}/repos")
    result = repos.json()
    repos = get_repos_count()
    repo_names = [result[num]["name"] for num in range(repos)]
    return repo_names


def request_to_json(url: str = None):
    result = requests.get(url, auth=(USERNAME, TOKEN))
    return result.json()
