import csv
import logging
import boto3
import os
from io import StringIO

logging_level = os.environ["LOGGING_LEVEL"]

logger = logging.getLogger()
logger.setLevel(logging_level)

dynamodb_client = boto3.client("dynamodb")
s3_client = boto3.client("s3")


def lambda_handler(event, context):
    logger.debug(f"Event: {event}")
    logger.debug(f"Context: {context}")
    s3_bucket_name, s3_key = get_s3_info(event)
    csv_contents = get_csv_contents(s3_bucket_name, s3_key)
    write_data_to_dynamodb(csv_contents)


def get_csv_contents(bucket_name: str, key: str):
    response = s3_client.get_object(Bucket=bucket_name, Key=key)

    csv_content = response["Body"].read().decode("utf-8")
    return csv_content


def write_data_to_dynamodb(csv_content: str):
    lines = csv.reader(csv_content)
    for line in lines:
        data = line.strip().split(",")
        api = data[0].strip('"')
        environment = data[1].strip('"')
        status = data[2].strip('"')

        put_item_in_dynamodb("APIList", api, environment, status)


def put_item_in_dynamodb(table_name: str, api: str, environment: str, status: str):
    try:
        response = dynamodb_client.put_item(
            Item={
                "APIName": {
                    "S": api,
                },
                "Environment": {
                    "S": environment,
                },
                "Status": {
                    "S": status,
                },
            },
            TableName=table_name,
        )
        logger.info(response)
    except Exception as e:
        logger.error(e)


def get_s3_info(event) -> tuple[str, str]:
    s3 = event["Records"][0]["s3"]
    s3_key = s3["object"]["key"]
    s3_bucket_name = s3["bucket"]["name"]

    return s3_bucket_name, s3_key
