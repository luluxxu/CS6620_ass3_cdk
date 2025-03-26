
import boto3
import time
import os
import urllib.request

def lambda_handler(event, context):
    bucket_name = os.environ.get('BUCKET_NAME')
    s3 = boto3.client('s3')
    
    # Step 1: Create assignment1.txt with content "Empty Assignment 1"
    content1 = "Empty Assignment 1"
    s3.put_object(Bucket=bucket_name, Key="assignment1.txt", Body=content1)
    print(f"Created assignment1.txt with content: '{content1}'")
    time.sleep(3)
    
    # Step 2: Update assignment1.txt with new content "Empty Assignment 2222222222"
    content2 = "Empty Assignment 2222222222"
    s3.put_object(Bucket=bucket_name, Key="assignment1.txt", Body=content2)
    print(f"Updated assignment1.txt with content: '{content2}'")
    time.sleep(3)
    
    # Step 3: Delete assignment1.txt
    s3.delete_object(Bucket=bucket_name, Key="assignment1.txt")
    print("Deleted assignment1.txt")
    time.sleep(3)
    
    # Step 4: Create assignment2.txt with content "33"
    content3 = "33"
    s3.put_object(Bucket=bucket_name, Key="assignment2.txt", Body=content3)
    print(f"Created assignment2.txt with content: '{content3}'")
    time.sleep(3)
    
    # Step 5: Call the plotting lambda API
    plotting_api_url = os.environ.get("PLOTTING_API_URL")
    if not plotting_api_url:
        raise Exception("Environment variable PLOTTING_API_URL is not set.")
    
    try:
        with urllib.request.urlopen(plotting_api_url) as response:
            api_response = response.read().decode("utf-8")
            print("Plotting lambda API response:", api_response)
    except Exception as e:
        print("Error calling plotting lambda API:", e)
    
    return {
        "statusCode": 200,
        "body": "Driver lambda executed successfully."
    }
