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

