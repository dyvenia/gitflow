from typing import List
import requests

BASE_URL = "https://api.github.com/"


class GitHubRepos:
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


class GitHubPR:
    def __init__(self):
        pass

    def request_to_json(self, url: str = None):
        repos = requests.get(url)
        return repos.json()

    def get_files_from_pr(self, repo: str = None, pr_number: int = None):
        """
        Get files changed from specific PR.
        needed: filename, status, additions, deletions, changes

        Returns:
            list of dicts -> convert to DF maybe - in final solution. 1 dict result[0] gives 1 commit from PR( For/while needed to extract info to dict)
        """
        url = f"repos/dyvenia/{repo}/pulls/{pr_number}/files"
        result = self.request_to_json(BASE_URL + url)
        list_dict_pr = []
        for i in range(len(result)):
            res_json = result[i]
            dict_pr = {
                "filename": res_json["filename"].split("/")[-1],
                "path_to_file": res_json["filename"],
                # "pr_number": pr_number,
                # "repo": repo,
                "status": res_json["status"],
                "additions": res_json["additions"],
                "deletions": res_json["deletions"],
                "changes": res_json["changes"],
            }
            print("___", dict_pr)
            list_dict_pr.append(dict_pr)
        return list_dict_pr

    def get_commit_from_pr(self, repo: str = None, pr_number: int = None):
        """
        Get info about commits from specific PR.
        needed: commit->author->name="",
        date,
        commiter(probably same as author),
        message

        Returns:
            list of dicts -> convert to DF maybe - in final solution. 1 dict result[0] gives 1 commit from PR( For/while needed to extract info to dict)
        """
        url = f"repos/dyvenia/{repo}/pulls/{pr_number}/commits"
        result = self.request_to_json(BASE_URL + url)

        list_dict_pr = []
        for i in range(len(result)):
            res_json = result[i]
            commit = res_json["commit"]
            dict_pr = {
                "author": commit["author"]["name"],
                "date_commit": commit["author"]["date"],
                "message": commit["message"],
                # "pr_number": pr_number,
                "comment_count": commit["comment_count"],
            }
            list_dict_pr.append(dict_pr)
        return list_dict_pr
