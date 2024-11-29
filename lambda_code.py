import boto3
import csv
import os

# access AWS resources
dynamodb = boto3.resource('dynamodb')  # DynamoDB (table) service
sns = boto3.client('sns')  # SNS (notification) service
s3 = boto3.client('s3')  #  S3 (storage) service

# environment variables
TABLE_NAME: str = os.environ['DYNAMO_TABLE']
SNS_TOPIC: str = os.environ['SNS_TOPIC']


def lambda_handler(event, context) -> dict[str, str | int]:
    # extract S3 bucket and file information
    bucket_name: str = event['Records'][0]['s3']['bucket']['name']
    file_key: str = event['Records'][0]['s3']['object']['key']
    
    try:
        # get csv file from bucket
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        csv_data = response['Body'].read().decode('utf-8').splitlines()

        # parse CSV and store in DynamoDB table
        table = dynamodb.Table(TABLE_NAME)  # get table
        reader = csv.DictReader(csv_data)  # read csv

        # add each performance to the DynamoDB table (row by row)
        for row in reader:
            table.put_item(Item={
                'Performer': row['Performer'],
                'Date-Stage': f"{row['Date']}-{row['Stage']}",
                'Start': row['Start'],
                'End': row['End']
            })

        # send success notification
        sns.publish(TopicArn=SNS_TOPIC, 
                    Message='CSV file successfully uploaded and parsed', 
                    Subject='Success')
        return {'statusCode': 200, 'body': 'CSV processed successfully'}

    except Exception as e:
        # send failure notification with error message
        sns.publish(TopicArn=SNS_TOPIC, 
                    Message=str(e), 
                    Subject='Error')
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
