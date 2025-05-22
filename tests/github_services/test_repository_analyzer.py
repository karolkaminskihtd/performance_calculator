import pytest
from unittest.mock import MagicMock, patch
from performance_calculator.github_services import repository_analyzer

@pytest.fixture
def mock_repo():
    mock = MagicMock()
    mock.full_name = "owner/repo"
    mock.html_url = "https://github.com/owner/repo"
    mock.stargazers_count = 42
    mock.forks_count = 7
    mock.created_at.strftime.return_value = "2023-01-01"
    mock.updated_at.strftime.return_value = "2023-06-01"
    return mock

def test_get_workflow_runs_success():
    mock_run = MagicMock()
    mock_run.id = 1
    mock_run.name = "CI"
    mock_run.status = "completed"
    mock_run.conclusion = "success"
    mock_run.head_branch = "main"
    mock_run.created_at.strftime.return_value = "2023-01-01 12:00:00"
    runs = [mock_run] * 3
    
    # Create a proper paginated mock object that contains both the items and totalCount
    mock_workflow_runs = MagicMock()
    mock_workflow_runs.__iter__.return_value = iter(runs)
    mock_workflow_runs.__len__.return_value = len(runs)
    mock_workflow_runs.totalCount = 3
    
    repo = MagicMock()
    repo.get_workflow_runs.return_value = mock_workflow_runs

    result = repository_analyzer.get_workflow_runs(repo)
    assert result["total_count"] == 3
    assert len(result["runs"]) == 3
    assert result["runs"][0]["workflow_name"] == "CI"

def test_get_workflow_runs_exception():
    repo = MagicMock()
    repo.get_workflow_runs.side_effect = Exception("API error")
    result = repository_analyzer.get_workflow_runs(repo)
    assert result == {"total_count": 0, "runs": []}

def test_get_pull_requests_exception():
    repo = MagicMock()
    repo.get_pulls.side_effect = Exception("API error")
    result = repository_analyzer.get_pull_requests(repo)
    assert result == {"total_count": 0, "pull_requests": []}

def test_get_commits_exception():
    repo = MagicMock()
    repo.get_commits.side_effect = Exception("API error")
    result = repository_analyzer.get_commits(repo)
    assert result == {"total_count": 0, "commits": []}

def test_get_contributors_success():
    mock_contributor = MagicMock()
    mock_contributor.login = "contrib1"
    mock_contributor.contributions = 10
    mock_contributor.html_url = "https://github.com/contrib1"
    mock_contributors = [mock_contributor] * 3

    repo = MagicMock()
    repo.get_contributors.return_value = mock_contributors

    result = repository_analyzer.get_contributors(repo)
    assert result["total_count"] == 3
    assert len(result["contributors"]) == 3
    assert result["contributors"][0]["login"] == "contrib1"

def test_get_contributors_exception():
    repo = MagicMock()
    repo.get_contributors.side_effect = Exception("API error")
    result = repository_analyzer.get_contributors(repo)
    assert result == {"total_count": 0, "contributors": []}

@patch("performance_calculator.github_services.repository_analyzer.get_workflow_runs")
@patch("performance_calculator.github_services.repository_analyzer.get_pull_requests")
@patch("performance_calculator.github_services.repository_analyzer.get_commits")
@patch("performance_calculator.github_services.repository_analyzer.get_contributors")
@patch("performance_calculator.github_services.repository_analyzer.Github")
@patch("performance_calculator.github_services.repository_analyzer.Auth")
def test_analyze_repository_success(mock_auth, mock_github, mock_get_contributors, mock_get_commits, mock_get_pull_requests, mock_get_workflow_runs, mock_repo):
    mock_github_instance = MagicMock()
    mock_github.return_value = mock_github_instance
    mock_github_instance.get_repo.return_value = mock_repo

    mock_get_workflow_runs.return_value = {"total_count": 1, "runs": []}
    mock_get_pull_requests.return_value = {"total_count": 2, "pull_requests": []}
    mock_get_commits.return_value = {"total_count": 3, "commits": []}
    mock_get_contributors.return_value = {"total_count": 4, "contributors": []}

    result = repository_analyzer.analyze_repository("owner", "repo", token="token123")
    assert result["repository"] == "owner/repo"
    assert result["stars"] == 42
    assert result["builds"]["total_count"] == 1
    assert result["pull_requests"]["total_count"] == 2
    assert result["commits"]["total_count"] == 3
    assert result["contributors"]["total_count"] == 4

@patch("performance_calculator.github_services.repository_analyzer.Github")
def test_analyze_repository_exception(mock_github):
    mock_github_instance = MagicMock()
    mock_github.return_value = mock_github_instance
    mock_github_instance.get_repo.side_effect = Exception("Not found")
    result = repository_analyzer.analyze_repository("owner", "repo")
    assert result is None