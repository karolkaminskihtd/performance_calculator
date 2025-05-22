import argparse
import os
from dotenv import load_dotenv
from github import Github, Auth

load_dotenv()

def get_github_data(created_date=None, limit=None):
    """
    Get GitHub repository data with optional date filtering.
    
    Args:
        created_date (str, optional): Date string to filter workflow runs.
            Can be a specific date like "2024-01-24" or date range like "2024-01-01..2024-01-31".
            Can also use GitHub date qualifiers like "<=2024-01-01" or ">=2023-12-31".
    
    Returns:
        dict: Dictionary containing processed repository data
    """
    owner = os.environ.get("GITHUB_OWNER")
    repo_name = os.environ.get("GITHUB_REPO")
    token = os.environ.get("GITHUB_TOKEN")

    if not all([owner, repo_name, token]):
        print("Error: Missing required environment variables (GITHUB_OWNER, GITHUB_REPO, GITHUB_TOKEN)")
        return None

    results = analyze_repository(owner, repo_name, token, created_date, limit)
    
    if not results:
        print("Error: Failed to analyze repository")
        return None
    
    # Format the results for return
    statistics = {
        'builds': results['builds']['runs'],
        'repository': results['repository'],
        'url': results['url'],
        'total_count': results['builds']['total_count']
    }
    
    return statistics


def analyze_repository(owner, repo_name, token=None, created_date=None, limit=None):
    """
    Analyze a GitHub repository to get builds, PRs, commits, and authors.
    
    Args:
        owner (str): Repository owner (username or organization).
        repo_name (str): Repository name.
        token (str, optional): GitHub access token for authentication.
        created_date (str, optional): Date string to filter workflow runs.
            Can be a specific date like "2024-01-24" or date range like "2024-01-01..2024-01-31".
            Can also use GitHub date qualifiers like "<2024-01-01" or ">2023-12-31".
        
    Returns:
        dict: Repository analysis results.
    """
    # Set up authentication
    if token:
        auth = Auth.Token(token)
        g = Github(auth=auth)
    else:
        g = Github()  # Unauthenticated, limited API access
    
    try:
        # Get repository
        repo = g.get_repo(f"{owner}/{repo_name}")
        
        # Get repository stats
        results = {
            "repository": repo.full_name,
            "url": repo.html_url,
            "last_updated": repo.updated_at.strftime("%Y-%m-%d"),
        }
        
        # Get workflow runs (builds)
        results["builds"] = get_workflow_runs(repo, created_date, limit)
        
        # # Get pull requests
        # results["pull_requests"] = get_pull_requests(repo)
        
        # # Get commits
        # results["commits"] = get_commits(repo)
        
        # # Get authors/contributors
        # results["contributors"] = get_contributors(repo)
        
        return results
    
    except Exception as e:
        print(f"Error analyzing repository: {e}")
        return None
    finally:
        g.close()  # Close connections after use


def get_workflow_runs(repo, created_date=None, limit=None):
    """
    Get workflow runs (builds) for the repository.
    
    Args:
        repo: GitHub repository object.
        created_date (str, optional): Date string to filter workflow runs.
            Can be a specific date like "2024-01-24" or date range like "2024-01-01..2024-01-31".
            Can also use GitHub date qualifiers like "<=2024-01-01" or ">=2023-12-31".
            GitHub query syntax examples:
            - "2023-01-01"            - Runs created on this specific date
            - "2023-01-01..2023-01-31" - Runs created in this date range
            - ">=2023-01-01"          - Runs created on or after this date
            - "<=2023-01-31"          - Runs created on or before this date
            - "<2023-02-01"           - Runs created before this date
            - ">2022-12-31"           - Runs created after this date
    """
    try:
        # Apply created_date filter if specified
        if created_date:
            workflow_runs = repo.get_workflow_runs(created=created_date)
        else:
            workflow_runs = repo.get_workflow_runs()
            
        runs = []
        
        # Display all attributes of the first workflow run
        # if workflow_runs.totalCount > 0:
        #     first_run = workflow_runs[0]
        #     print("\nWorkflow Run Attributes:")
        #     for attr in dir(first_run):
        #         if not attr.startswith('_'):  # Skip private attributes
        #             try:
        #                 value = getattr(first_run, attr)
        #                 print(f"{attr}: {value}")
        #             except Exception as e:
        #                 print(f"{attr}: Error accessing attribute - {e}")
        
        for run in workflow_runs[:limit] if limit else workflow_runs:
            pull_requests = run.raw_data.get("pull_requests", [])
            
            runs.append({
                "id": run.id,
                "author": run.actor.login if run.actor else None,
                "workflow_name": run.name,
                "pr_name": run.display_title,
                "status": run.status,
                "conclusion": run.conclusion,
                "head_branch": run.head_branch,
                "base_branch": pull_requests[0].get("base", {}).get("ref", None) if pull_requests else None,
                "pull_requests_count": len(run.pull_requests),
                "run_attempt": run.run_attempt,
                "run_number": run.run_number,
                "created_at": run.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })
        
        return {
            "total_count": workflow_runs.totalCount,
            "runs": runs
        }
    except Exception as e:
        print(f"Error getting workflow runs: {e}")
        return {"total_count": 0, "runs": []}


def get_pull_requests(repo):
    """Get pull requests for the repository."""
    try:
        pulls = repo.get_pulls(state='all')
        pr_list = []

        if pulls.totalCount == 0:
            print("No pull requests found.")
            return {"total_count": 0, "pull_requests": []}
        
        for pr in pulls[:100]:  # Limit to 100 PRs to avoid excessive data
            pr_list.append({
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "created_at": pr.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "user": pr.user.login,
                "url": pr.html_url,
            })
        
        return {
            "total_count": pulls.totalCount,
            "pull_requests": pr_list
        }
    except Exception as e:
        print(f"Error getting pull requests: {e}")
        return {"total_count": 0, "pull_requests": []}


def get_commits(repo):
    """Get commits for the repository."""
    try:
        commits = repo.get_commits()
        commit_list = []
        
        for commit in commits[:100]:  # Limit to 100 commits to avoid excessive data
            commit_list.append({
                "sha": commit.sha,
                "author": commit.author.login if commit.author else "Unknown",
                "message": commit.commit.message.split("\n")[0],  # First line of message
                "date": commit.commit.author.date.strftime("%Y-%m-%d %H:%M:%S"),
                "url": commit.html_url,
            })
        
        return {
            "total_count": commits.totalCount,
            "commits": commit_list
        }
    except Exception as e:
        print(f"Error getting commits: {e}")
        return {"total_count": 0, "commits": []}


def get_contributors(repo):
    """Get contributors for the repository."""
    try:
        contributors = repo.get_contributors()
        contributor_list = []
        
        for contributor in contributors:
            contributor_list.append({
                "login": contributor.login,
                "contributions": contributor.contributions,
                "url": contributor.html_url,
            })
        
        return {
            "total_count": len(contributor_list),
            "contributors": contributor_list
        }
    except Exception as e:
        print(f"Error getting contributors: {e}")
        return {"total_count": 0, "contributors": []}
