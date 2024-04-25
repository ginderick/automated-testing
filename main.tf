
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

