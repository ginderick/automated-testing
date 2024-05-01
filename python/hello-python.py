def lambda_handler(event, context):
    print(f"Event: {event}")
    print(f"Context: {context}")
    print("hello world")
    return {"message": "Hello world"}
