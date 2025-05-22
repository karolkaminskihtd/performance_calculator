import argparse
from datetime import datetime, timedelta

def format_date_range(start_date=None, end_date=None, days=None):
    """
    Create a GitHub date filter string based on provided parameters.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        days (int): Number of days back from today
        
    Returns:
        str: Formatted date range string for GitHub API
    """
    today = datetime.now()
    
    # If days is provided, calculate start_date from it
    if days is not None:
        start_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
        # If no end_date is specified, use today
        if not end_date:
            end_date = today.strftime("%Y-%m-%d")
    
    # Create GitHub date filter string
    if start_date and end_date:
        return f"{start_date}..{end_date}"
    elif start_date:
        return f">={start_date}"
    elif end_date:
        return f"<={end_date}"
    else:
        return None
    
def parsed_arguments():
    parser = argparse.ArgumentParser(description='Analyze GitHub repository data with date filtering.')
    
    # Date filtering options
    date_group = parser.add_argument_group('Date filtering options')
    date_group.add_argument('--date', 
                        help='Filter workflow runs by creation date. Format can be: '
                             'YYYY-MM-DD for specific date, '
                             'YYYY-MM-DD..YYYY-MM-DD for date range, '
                             '>YYYY-MM-DD or <YYYY-MM-DD for dates after or before')
    date_group.add_argument('--start-date', 
                        help='Start date for filtering workflow runs (YYYY-MM-DD)')
    date_group.add_argument('--end-date', 
                        help='End date for filtering workflow runs (YYYY-MM-DD)')
    date_group.add_argument('--days', type=int,
                        help='Get workflow runs from the last N days')
    
    # Output options
    output_group = parser.add_argument_group('Output options')
    output_group.add_argument('--output',
                          help='Save results to the specified JSON file')
    output_group.add_argument('--limit', type=int,
                          help='Limit the number of workflow runs to display')
    
    return parser.parse_args()

def get_date_filter(args):
    date_filter = None
    if args.date:
        date_filter = args.date
    else:
        date_filter = format_date_range(
            start_date=args.start_date, 
            end_date=args.end_date, 
            days=args.days
        )
    return date_filter