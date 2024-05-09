import logging
import boto3
import os
import urllib3

import pkg_resources
import json

logging_level = os.environ["LOGGING_LEVEL"]

environment = os.environ["ENVIRONMENT"]
token = os.environ["TOKEN"]
branch = os.environ["BRANCH"]
service = os.environ["SERVICE"]
api = os.environ["API"]
number_of_users = os.environ["NUMBER_OF_USERS"]

logger = logging.getLogger()
logger.setLevel(logging_level)

dynamodb_client = boto3.client("dynamodb")


def lambda_handler(event, context):
    logger.debug(f"Event: {event}")
    logger.debug(f"Context: {context}")

    items = get_items_from_dynamodb()
    query_api(items)


def execute_gitlab_perf_test():
    http = urllib3.PoolManager()
    url = "https://gitlab.com/api/v4/projects/54833002/trigger/pipeline"

    encoded_data = json.dumps(
        {
            "token": token,
            "ref": branch,
            "variables[PROJECT_DIR]": service,
            "variables[PROPERTIES_FILE]": f"{service}/config/{environment}.properties",
            "variables[REPORTS_DIR]": f"{service}/reports",
            "variables[TEST_TYPE]": "performance",
            "variables[API]": f"jmeter.{api}.Users={number_of_users}",
        }
    )
    response = http.request(
        "POST", url, body=encoded_data, headers={"Content-Type": "application/json"}
    )

    result = json.loads(response.data.decode("utf-8"))["json"]
    logger.info(response)


def get_items_from_dynamodb():
    table_name = "APIList"
    index_name = "StatusIndex"

    filter_expression = "#attr_name = :attr_value"
    expression_attribute_values = {":attr_value": {"S": "pending"}}
    expression_attribute_names = {"#attr_name": "Status"}

    response = dynamodb_client.query(
        TableName=table_name,
        IndexName=index_name,
        KeyConditionExpression=filter_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ExpressionAttributeNames=expression_attribute_names,
    )

    return response["Items"]


def query_api(items):
    ocp_count = 0
    aws_count = 0

    for item in items:
        print(item)
        if item["Status"]["S"] == "pending":
            if ocp_count < 1 or aws_count < 1:
                if item["Environment"]["S"] == "aws-uat":
                    aws_count += 1
                if item["Environment"]["S"] == "rhocp-nft":
                    ocp_count += 1
                execute_gitlab_perf_test()
