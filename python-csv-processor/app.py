import csv
import logging
import boto3
import os

logging_level = os.environ["LOGGING_LEVEL"]

logger = logging.getLogger()
logger.setLevel(logging_level)

dynamodb_client = boto3.client("dynamodb")


def lambda_handler(event, context):
    logger.debug(f"Event: {event}")
    logger.debug()(f"Context: {context}")
    s3_location = get_s3_location(event)
    write_data_to_dynamodb(s3_location)


def write_data_to_dynamodb(s3_location: str):
    with open(s3_location, newline="") as csvfile:
        for line in csvfile:
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


def get_s3_location(event) -> str:
    s3 = event["Records"][0]["s3"]
    s3_key = s3["object"]["key"]
    s3_bucket_name = s3["bucket"]["name"]

    s3_location = s3_bucket_name + "/" + s3_key
    return s3_location
