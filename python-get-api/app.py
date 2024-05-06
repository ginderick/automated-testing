import logging
import boto3
import os
import urllib3

import json

logging_level = os.environ["LOGGING_LEVEL"]


logger = logging.getLogger()
logger.setLevel(logging_level)

dynamodb_client = boto3.client("dynamodb")


def lambda_handler(event, context):
    logger.debug(f"Event: {event}")
    logger.debug(f"Context: {context}")

    query_api()


def execute_gitlab_perf_test():
    # Create a PoolManager instance
    http = urllib3.PoolManager()

    # Define the URL and headers
    url = "https://gitlab.com/api/v4/projects/54833002/trigger/pipeline"
    headers = {"PRIVATE-TOKEN": "glptt-c62ee45eb5e9c9d79cb0577e0ca308c71835be73"}

    # Define the form fields
    encoded_body = json.dumps(
        {
            "token": "glptt-c62ee45eb5e9c9d79cb0577e0ca308c71835be73",
            "ref": "feature/SP0B15-1133",
            "variables[PROJECT_DIR]": "hip-ws-nejb-nrpl25",
            "variables[PROPERTIES_FILE]": f"hip-ws-nejb-nrpl25/config/rhocp-nft.properties",
            "variables[REPORTS_DIR]": "hip-ws-nejb-nrpl25/reports",
            "variables[TEST_TYPE]": "performance",
            "variables[API]": "jmeter.GetDetailsByAttributes.Users=20",
        }
    )
    http = urllib3.PoolManager()

    r = http.request(
        "POST",
        "http://localhost:8080/assets",
        headers={"Content-Type": "application/json"},
        body=encoded_body,
    )

    # Send the POST request
    response = http.request("POST", url, headers=headers, body=encoded_fields)
    logger.info(response)


def query_api():
    ocp_count = 0
    aws_count = 0

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

    for item in response["Items"]:
        print(item)
        if item["Status"]["S"] == "pending":
            if ocp_count < 1 or aws_count < 1:
                if item["Environment"]["S"] == "aws-uat":
                    aws_count += 1
                if item["Environment"]["S"] == "rhocp-nft":
                    ocp_count += 1
                execute_gitlab_perf_test()
