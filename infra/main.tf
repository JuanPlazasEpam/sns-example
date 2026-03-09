terraform {
  required_version = ">= 1.3.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# SNS topic (KMS-encrypted)
resource "aws_sns_topic" "main" {
  name            = "${var.project_name}-topic"
  kms_master_key_id = "alias/aws/sns"
}

# Dead-letter queue for failed messages (KMS-encrypted)
resource "aws_sqs_queue" "dlq" {
  name                      = "${var.project_name}-dlq"
  message_retention_seconds = 1209600 # 14 days
  kms_master_key_id         = "alias/aws/sqs"
}

# Main SQS queue (KMS-encrypted)
resource "aws_sqs_queue" "main" {
  name                       = "${var.project_name}-queue"
  visibility_timeout_seconds = 30
  message_retention_seconds  = 86400
  kms_master_key_id          = "alias/aws/sqs"

  # Redrive policy: send messages to DLQ after several failed receives.
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 5
  })
}

resource "aws_iam_user" "app_user" {
  name = "${var.project_name}-app-user"
}

resource "aws_iam_access_key" "app_user_key" {
  user = aws_iam_user.app_user.name
}

data "aws_iam_policy_document" "app_user_policy_doc" {
  statement {
    effect = "Allow"
    actions = [
      "sns:Publish",
    ]
    resources = [
      aws_sns_topic.main.arn,
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
    ]
    resources = [
      aws_sqs_queue.main.arn,
    ]
  }
}

resource "aws_iam_user_policy" "app_user_policy" {
  name   = "${var.project_name}-app-policy"
  user   = aws_iam_user.app_user.name
  policy = data.aws_iam_policy_document.app_user_policy_doc.json
}

# Allow SNS topic to send messages to the SQS queue
data "aws_iam_policy_document" "sqs_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }

    actions = [
      "sqs:SendMessage",
    ]

    resources = [
      aws_sqs_queue.main.arn,
    ]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_sns_topic.main.arn]
    }
  }
}

resource "aws_sqs_queue_policy" "main" {
  queue_url = aws_sqs_queue.main.id
  policy    = data.aws_iam_policy_document.sqs_policy.json
}

# Subscribe the queue to the topic
resource "aws_sns_topic_subscription" "sqs_subscription" {
  topic_arn = aws_sns_topic.main.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.main.arn
}

