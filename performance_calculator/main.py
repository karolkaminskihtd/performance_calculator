import argparse
import os
from datetime import datetime, timedelta
from github import Github, Auth


def analyze_repository(owner, repo_name, token=None):
    """
    Analyze a GitHub repository to get builds, PRs, commits, and authors.
    
    Args:
        owner (str): Repository owner (username or organization).
        repo_name (str): Repository name.
        token (str, optional): GitHub access token for authentication.
        
    Returns:
        dict: Repository analysis results.
    """
    # Set up authentication
    if token:
        auth = Auth.Token(token)
        g = Github(auth=auth)
    else:
        g = Github()  # Unauthenticated, limited API access
    
    print(f"Analyzing repository: {owner}/{repo_name}")
    
    try:
        # Get repository
        repo = g.get_repo(f"{owner}/{repo_name}")
        
        # Get repository stats
        results = {
            "repository": repo.full_name,
            "url": repo.html_url,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "created_at": repo.created_at.strftime("%Y-%m-%d"),
            "last_updated": repo.updated_at.strftime("%Y-%m-%d"),
        }
        
        # Get workflow runs (builds)
        results["builds"] = get_workflow_runs(repo)
        
        # Get pull requests
        results["pull_requests"] = get_pull_requests(repo)
        
        # Get commits
        results["commits"] = get_commits(repo)
        
        # Get authors/contributors
        results["contributors"] = get_contributors(repo)
        
        return results
    
    except Exception as e:
        print(f"Error analyzing repository: {e}")
        return None
    finally:
        g.close()  # Close connections after use


def get_workflow_runs(repo):
    """Get workflow runs (builds) for the repository."""
    try:
        workflow_runs = repo.get_workflow_runs()
        runs = []
        
        for run in workflow_runs:
            runs.append({
                "id": run.id,
                "workflow_name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "branch": run.head_branch,
                "created_at": run.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })
        
        return {
            "total_count": workflow_runs.totalCount,
            "runs": runs[:100]  # Limit to avoid excessive data
        }
    except Exception as e:
        print(f"Error getting workflow runs: {e}")
        return {"total_count": 0, "runs": []}


def get_pull_requests(repo):
    """Get pull requests for the repository."""
    try:
        pulls = repo.get_pulls(state='all')
        pr_list = []
        
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


def main():
    parser = argparse.ArgumentParser(description="Analyze GitHub repositories")
    parser.add_argument("owner", help="Repository owner (username or organization)")
    parser.add_argument("repo", help="Repository name")
    parser.add_argument("--token", "-t", help="GitHub access token")
    parser.add_argument("--output", "-o", help="Output file path (JSON)")
    args = parser.parse_args()
    
    # Use token from environment variable if not provided
    token = args.token or os.environ.get("GITHUB_TOKEN")
    
    # Analyze repository
    results = analyze_repository(args.owner, args.repo, token)
    
    if results:
        # Display summary results
        print("\nRepository Analysis Summary:")
        print(f"Repository: {results['repository']}")
        print(f"URL: {results['url']}")
        print(f"Stars: {results['stars']}")
        print(f"Forks: {results['forks']}")
        print(f"Created: {results['created_at']}")
        print(f"Last Updated: {results['last_updated']}")
        print(f"\nWorkflow Runs (Builds): {results['builds']['total_count']}")
        print(f"Pull Requests: {results['pull_requests']['total_count']}")
        print(f"Commits: {results['commits']['total_count']}")
        print(f"Contributors: {results['contributors']['total_count']}")
        
        # Save to file if specified
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nFull results saved to {args.output}")
        else:
            # Print more detailed info if not saving to file
            print("\nRecent Workflow Runs:")
            for run in results['builds']['runs'][:5]:  # Show 5 most recent
                print(f"  - {run['workflow_name']} ({run['status']}/{run['conclusion']}) on {run['branch']} at {run['created_at']}")
            
            print("\nRecent Pull Requests:")
            for pr in results['pull_requests']['pull_requests'][:5]:  # Show 5 most recent
                print(f"  - #{pr['number']} {pr['title']} by {pr['user']} ({pr['state']}) created at {pr['created_at']}")
            
            print("\nRecent Commits:")
            for commit in results['commits']['commits'][:5]:  # Show 5 most recent
                print(f"  - {commit['sha'][:7]} {commit['message']} by {commit['author']} at {commit['date']}")
            
            print("\nTop Contributors:")
            sorted_contributors = sorted(results['contributors']['contributors'], key=lambda x: x['contributions'], reverse=True)
            for contributor in sorted_contributors[:5]:  # Show top 5
                print(f"  - {contributor['login']} ({contributor['contributions']} contributions)")


if __name__ == "__main__":
    main()
