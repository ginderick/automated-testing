
provider "aws" {
  region = "ap-southeast-1"
}

######################
# S3 Bucket and config
######################

resource "aws_s3_bucket" "test_bucket" {
  bucket = "my-test-bucket-ginderick123"

  tags = {
    Name        = "my-test-bucket"
    Environment = "dev"
  }
}

resource "aws_s3_object" "new_upload" {
  bucket = aws_s3_bucket.test_bucket.id
  key    = "new_upload/"

}

resource "aws_s3_object" "for_processing" {
  bucket = aws_s3_bucket.test_bucket.id
  key    = "for_processing/"

}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.test_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.csv_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "new_upload/"
  }

  depends_on = [aws_lambda_permission.allow_bucket]

}

######################
# Lambda Function 1
######################

data "archive_file" "zip_python_code" {
  type        = "zip"
  source_dir  = "${path.module}/python-csv-processor/"
  output_path = "${path.module}/python-csv-processor/python-csv-processor-v3.zip"
}

resource "aws_lambda_function" "csv_processor" {
  filename      = "${path.module}/python-csv-processor/python-csv-processor-v3.zip"
  function_name = "lambda_csv_processor"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "app.lambda_handler"
  runtime       = "python3.8"
  environment {
    variables = {
      LOGGING_LEVEL = "INFO"
    }
  }
  depends_on = []

}


data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }

}

######################
# Lambda Function 2
######################

data "archive_file" "zip_python_code2" {
  type        = "zip"
  source_dir  = "${path.module}/python/"
  output_path = "${path.module}/python/hello-pythonv1-2.zip"
}

resource "aws_lambda_function" "csv_processor2" {
  filename      = "${path.module}/python/hello-pythonv1-2.zip"
  function_name = "lambda2"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "hello-python.lambda_handler"
  runtime       = "python3.8"
  depends_on    = []

}


######################
# Lambda Function Role
######################

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json

}

resource "aws_iam_policy" "function_logging_policy" {
  name = "function-logging-policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Action : [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Effect : "Allow",
        Resource : "arn:aws:logs:*:*:*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:GetObject"
        ],
        "Resource" : "arn:aws:s3:::*/*"
      }
    ]
  })

}

resource "aws_iam_role_policy_attachment" "function_logging_policy_attachment" {
  role       = aws_iam_role.iam_for_lambda.id
  policy_arn = aws_iam_policy.function_logging_policy.arn

}

resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.csv_processor.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.test_bucket.arn

}


######################
# Cloudwatch
######################

resource "aws_cloudwatch_log_group" "function_log_group" {
  name = "/aws/lambda/${aws_lambda_function.csv_processor.function_name}"
}

resource "aws_cloudwatch_log_group" "function_log_group2" {
  name = "/aws/lambda/${aws_lambda_function.csv_processor2.function_name}"
}

######################
# DynamoDB
######################
resource "aws_dynamodb_table" "basic-dynamodb-table" {
  name         = "APIList"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "APIName"
  range_key    = "Environment"

  attribute {
    name = "APIName"
    type = "S"
  }

  attribute {
    name = "Environment"
    type = "S"
  }

  attribute {
    name = "Status"
    type = "S"
  }


  global_secondary_index {
    name            = "StatusIndex"
    hash_key        = "Status"
    range_key       = "Environment"
    projection_type = "KEYS_ONLY"
  }

  tags = {
    Name        = "dynamodb-table-1"
    Environment = "production"
  }
}




######################
# EventBridge
######################
resource "aws_cloudwatch_event_rule" "example" {
  name                = "invoke-lambda-function2"
  description         = "Invoke lambda function 2 every 35 mins"
  schedule_expression = "rate(2 minutes)"
  is_enabled          = true
}

resource "aws_cloudwatch_event_target" "example" {
  arn       = aws_lambda_function.csv_processor2.arn
  rule      = aws_cloudwatch_event_rule.example.id
  target_id = aws_lambda_function.csv_processor2.function_name

}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_check_foo" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.csv_processor2.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.example.arn
}






