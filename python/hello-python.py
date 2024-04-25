def lambda_handler(event, context):
    print(event)
    print(context)
    return {"message": "Hello world"}
