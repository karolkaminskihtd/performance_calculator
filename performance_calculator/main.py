import json
from datetime import datetime, timedelta
from performance_calculator.github_services.repository_analyzer import get_github_data

def main():
    get_github_data()

if __name__ == "__main__":
    main()
