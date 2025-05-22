import os
import csv
import glob
from datetime import datetime, timedelta
from collections import defaultdict

def calculate_github_personal_performance():
    """
    Analyze GitHub workflow data and calculate build success ratios for each author on a weekly basis.
    
    This function:
    1. Finds the most recent github_workflow_data CSV file in the results folder
    2. Calculates the success/failure ratio for each author
    3. Groups the data by author and week
    4. Outputs a CSV with author, date_range, and build_ratio columns
    """
    # Find the most recent GitHub workflow data file
    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')
    workflow_files = glob.glob(os.path.join(results_dir, 'github_workflow_data_*.csv'))
    
    if not workflow_files:
        print("No GitHub workflow data files found in the results directory.")
        return
    
    # Sort files by timestamp in the filename (newest first)
    latest_file = max(workflow_files, key=lambda x: os.path.basename(x).split('_')[-1].split('.')[0])
    print(f"Using data from: {os.path.basename(latest_file)}")
    
    # Parse the CSV file
    data = []
    with open(latest_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    
    # Process the data: convert created_at to datetime
    for row in data:
        row['created_at'] = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S')
    
    # Group data by author and week
    author_week_stats = defaultdict(lambda: defaultdict(lambda: {'success': 0, 'failure': 0}))
    
    for row in data:
        # Get the start of the week (Monday)
        created_date = row['created_at']
        week_start = created_date - timedelta(days=created_date.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Format date range string
        date_range = f"{week_start.strftime('%Y-%m-%d')}...{week_end.strftime('%Y-%m-%d')}"
        
        # Increment the appropriate counter
        if row['conclusion'] == 'success':
            author_week_stats[row['author']][date_range]['success'] += 1
        elif row['conclusion'] == 'failure':
            author_week_stats[row['author']][date_range]['failure'] += 1

        author_week_stats[row['author']][date_range]['failure'] += (int(row['run_attempt']) - 1)
    
    # Calculate ratios and prepare results
    results = []
    
    for author, weeks in author_week_stats.items():
        for date_range, stats in weeks.items():
            success_count = stats['success']
            failure_count = stats['failure']
            
            # Calculate build ratio (success/failure)
            # Handle division by zero case
            if failure_count == 0:
                build_ratio = float('inf') if success_count > 0 else 0
            else:
                build_ratio = success_count / failure_count
                
            results.append({
                'author': author,
                'date_range': date_range,
                'build_ratio': round(build_ratio, 2) if build_ratio != float('inf') else 'inf'
            })
    
    # Generate output filename with current timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(results_dir, f'github_performance_by_author_{timestamp}.csv')
    
    # Save results to CSV
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['author', 'date_range', 'build_ratio']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    
    print(f"Results saved to: {output_file}")
    
    return results
