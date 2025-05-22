import json
from performance_calculator.github_services.repository_analyzer import get_github_data
from performance_calculator.calculator_utils.arguments_helper import *


def main():
    args = parsed_arguments()
    date_filter = get_date_filter(args)
    
    result = get_github_data(created_date=date_filter, limit=args.limit)

    print(result['builds'])
    
    # if result and 'builds' in result:
    #     if result['builds']:
    #         print("\nWorkflow Runs Summary:")
    #         for i, run in enumerate(result['builds']):
    #             base_info = f"{i+1}. {run['workflow_name']} ({run['status']}/{run['conclusion']}) at {run['created_at']}"
                
    #             if args.detailed:
    #                 print(f"{base_info}")
    #                 print(f"   ID: {run['id']}")
    #                 print(f"   Branch: {run['head_branch']}")
    #                 print(f"   Author: {run['author']}")
    #                 print(f"   Run Number: {run['run_number']}")
    #                 print(f"   Run Attempt: {run['run_attempt']}")
    #                 if run['pr_name']:
    #                     print(f"   PR Title: {run['pr_name']}")
    #                 print("")
    #             else:
    #                 print(f"- {base_info}")
        
    #     # Save to file if requested
    #     if args.output:
    #         try:
    #             with open(args.output, 'w') as f:
    #                 json.dump(result, f, indent=2)
    #             print(f"\nResults saved to {args.output}")
    #         except Exception as e:
    #             print(f"Error saving results to file: {e}")

if __name__ == "__main__":
    main()
