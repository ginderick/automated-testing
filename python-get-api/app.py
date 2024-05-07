import logging
import boto3
import os
import urllib3

import pkg_resources
import json

logging_level = os.environ["LOGGING_LEVEL"]


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
            "token": "glptt-c62ee45eb5e9c9d79cb0577e0ca308c71835be73",
            "ref": "develop",
            "variables[PROJECT_DIR]": "hip-ws-nejb-nrpl25",
            "variables[PROPERTIES_FILE]": "hip-ws-nejb-nrpl25/config/rhocp-nft.properties",
            "variables[REPORTS_DIR]": "hip-ws-nejb-nrpl25/reports",
            "variables[TEST_TYPE]": "performance",
            "variables[API]": "jmeter.GetDetailsByAttributes.Users=20",
        }
    )
    response = http.request(
        "POST", url, body=encoded_data, headers={"Content-Type": "application/json"}
    )

    result = json.loads(response.data.decode("utf-8"))["json"]
    logger.info(result)


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
