output "sns_topic_arn" {
  value       = aws_sns_topic.main.arn
  description = "SNS topic ARN"
}

output "sqs_queue_url" {
  value       = aws_sqs_queue.main.id
  description = "SQS queue URL"
}

output "sqs_queue_arn" {
  value       = aws_sqs_queue.main.arn
  description = "SQS queue ARN"
}

output "app_user_access_key_id" {
  value       = aws_iam_access_key.app_user_key.id
  description = "Access key ID for app IAM user"
  sensitive   = true
}

output "app_user_secret_access_key" {
  value       = aws_iam_access_key.app_user_key.secret
  description = "Secret access key for app IAM user"
  sensitive   = true
}

