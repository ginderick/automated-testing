import csv


def lambda_handler(event, context):
    print(f"Event: {event}")
    print(f"Context: {context}")
    return {"message": "Hello world"}
