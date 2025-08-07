import math
import json
import boto3
import requests
import schedule
import time
from datetime import datetime

# DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('service-table')  # Replace with your DynamoDB table name

# API URL to fetch data from
api_url = "https://uwwrudi7qc.execute-api.us-east-1.amazonaws.com/prod/"  # Replace with your actual API URL

def calculate_score(latency, success_rate, team_name):
    print("latency", latency)
    print("success_rate", success_rate)
    
    if (success_rate < 100):
        ret = math.inf
    elif (latency == 0):
        ret = math.inf
    elif (team_name == "404 HORN NOT FOUND"):
        ret = math.inf
    else:
        ret = latency
    return ret

service_score_dict = {
    "leeter": math.inf,
    "reverser": math.inf,
    "swapcaser": math.inf
}
url_dict = {
    "leeter": "*",
    "reverser": "*",
    "swapcaser": "*"
}
team_name_dict = {
    "leeter": "*",
    "reverser": "*",
    "swapcaser": "*"
}
def fetch_and_store_data():
    def step1():
        # Step 1: Fetch data from the API
        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an exception for 4xx/5xx errors
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from API: {e}")
            return
        timestamp = datetime.utcnow().isoformat()  # Use current timestamp
        #print("data", data)
        #print("timestamp", timestamp)
        return data
    data = step1()
    # Step 2: Process the data

    def step2(data):
        #print("data", data)
        for team_data in data["body"]:
            #print("team_data ->",team_data)
            team_name = team_data["TeamName"]
            url = team_data["Uri"]
            service_type = team_data["Type"]
            latency = team_data["AverageLatency"]
            success_rate = team_data["SuccessRate"]
            service_score = calculate_score(latency, success_rate, team_name)
            if (service_score < service_score_dict[service_type]):
                service_score_dict[service_type] = service_score
                url_dict[service_type] = url
                team_name_dict[service_type] = team_name

        print("url_dict", url_dict)
        print("service_score_dict", service_score_dict)
    step2(data)
    def step3():
        def do_update(service_name):
            endpoint = url_dict[service_name]
            service_type = service_name
            team_name = team_name_dict[service_name]
            print("service name", service_name)
            print("endpoint", endpoint)
            print("service_type", service_type)
            print("team_name", team_name)
            table.delete_item(
                Key={
                    'Endpoint': endpoint,
                    'ServiceType': service_type,
                }
            )
            table.put_item(
                Item={
                    'TeamName': team_name,
                    'ServiceType': service_type,
                    'Endpoint': endpoint
                }
            )
        do_update("leeter")
        #do_update("swapcaser")
        do_update("reverser")
    step3()

# Schedule the script to run every 5 minutes (or adjust as needed)
def schedule_script():
    # Schedule the task every 5 minutes
    schedule.every(5).seconds.do(fetch_and_store_data)

    print("Scheduler started. The script will fetch and store data every 5 minutes.")

    # Keep the script running to process scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)  # Wait for 1 second before checking the schedule again

if __name__ == "__main__":
    schedule_script()