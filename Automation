import json
import boto3
import requests
import schedule
import time
from datetime import datetime

# DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TeamPerformance')  # Replace with your DynamoDB table name

# API URL to fetch data from
api_url = "https://56x1fbqe8k.execute-api.us-east-1.amazonaws.com/Stage/"  # Replace with your actual API URL

def fetch_and_store_data():
    # Step 1: Fetch data from the API
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for 4xx/5xx errors
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return

    # Step 2: Process and store data in DynamoDB
    timestamp = datetime.utcnow().isoformat()  # Use current timestamp

    for team_data in data:
        team_name = team_data["TeamName"]
        service_type = team_data["Type"]
        latency = team_data["AverageLatency"]
        success_rate = team_data["SuccessRate"]

        # Step 3: Retrieve the current record for the team (if exists)
        try:
            response = table.get_item(Key={'TeamName': team_name, 'Timestamp': timestamp})
            existing_item = response.get('Item')

            # If an existing record is found, compare the success rates
            if existing_item:
                existing_success_rate = existing_item['SuccessRate']

                # Only update if the new success rate is higher
                if success_rate > existing_success_rate:
                    print(f"New highest success rate for {team_name}: {success_rate} (Previous: {existing_success_rate})")
                    table.put_item(
                        Item={
                            'TeamName': team_name,
                            'Timestamp': timestamp,
                            'Type': service_type,
                            'AverageLatency': latency,
                            'SuccessRate': success_rate
                        }
                    )
                else:
                    print(f"No update for {team_name} as the success rate is not higher.")
            else:
                # If no record exists for this team, insert the new data
                print(f"No existing record for {team_name}. Inserting new data.")
                table.put_item(
                    Item={
                        'TeamName': team_name,
                        'Timestamp': timestamp,
                        'Type': service_type,
                        'AverageLatency': latency,
                        'SuccessRate': success_rate
                    }
                )

        except Exception as e:
            print(f"Error checking or inserting data for team '{team_name}': {e}")

# Schedule the script to run every 5 minutes (or adjust as needed)
def schedule_script():
    # Schedule the task every 5 minutes
    schedule.every(5).minutes.do(fetch_and_store_data)

    print("Scheduler started. The script will fetch and store data every 5 minutes.")

    # Keep the script running to process scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)  # Wait for 1 second before checking the schedule again

if __name__ == "__main__":
    schedule_script()
