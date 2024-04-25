
provider "aws" {
  region = "ap-southeast-1"
}

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

resource "aws_cloudwatch_log_group" "function_log_group" {
  name = "/aws/lambda/${aws_lambda_function.test_lambda.function_name}"


}

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
  function_name = aws_lambda_function.test_lambda.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.test_bucket.arn

}


data "archive_file" "zip_python_code" {
  type        = "zip"
  source_dir  = "${path.module}/python/"
  output_path = "${path.module}/python/hello-pythonv1-1.zip"
}

resource "aws_lambda_function" "test_lambda" {
  filename      = "${path.module}/python/hello-pythonv1-1.zip"
  function_name = "example_lambda_name"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "hello-python.lambda_handler"
  runtime       = "python3.8"
  depends_on    = []

}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.test_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.test_lambda.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "new_upload/"
  }

  depends_on = [aws_lambda_permission.allow_bucket]

}
