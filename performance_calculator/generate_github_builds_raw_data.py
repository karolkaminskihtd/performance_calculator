import csv
import os
from datetime import datetime
from performance_calculator.github_services.repository_analyzer import get_github_data
from performance_calculator.calculator_utils.arguments_helper import *


def generate_github_builds_raw_data():
    args = parsed_arguments()
    date_filter = get_date_filter(args)
    
    result = get_github_data(created_date=date_filter, limit=args.limit)

    print(result['builds'])
    
    if result and 'builds' in result:
        # Create results directory if it doesn't exist
        results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        # Generate a filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = os.path.join(results_dir, f'github_workflow_data_{timestamp}.csv')
        
        # Define CSV headers based on the keys in the data
        headers = ['author', 'workflow_name', 'pr_name', 'conclusion', 
                  'head_branch', 'base_branch', 'run_attempt', 'created_at']
        
        # Write data to CSV file
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            for i, run in enumerate(result['builds']):
                info_row = [run['author'], run['workflow_name'], run['pr_name'],
                           run['conclusion'], run['head_branch'], run['base_branch'], 
                           run['run_attempt'], run['created_at']]
                writer.writerow(info_row)
                print(f"{i + 1}: {','.join(str(item) for item in info_row)}")
        
        print(f"\nData saved to {csv_filename}")

if __name__ == "__generate_github_builds_raw_data__":
    generate_github_builds_raw_data()
