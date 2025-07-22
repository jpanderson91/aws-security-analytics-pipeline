# CloudWatch Dashboard for Security Analytics Pipeline

resource "aws_cloudwatch_dashboard" "security_analytics" {
  dashboard_name = "${var.project_name}-security-analytics-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.event_processor.function_name],
            ["AWS/Lambda", "Invocations", "FunctionName", aws_lambda_function.event_processor.function_name],
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.event_processor.function_name],
            ["AWS/Lambda", "Throttles", "FunctionName", aws_lambda_function.event_processor.function_name]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Lambda Function Performance"
          view   = "timeSeries"
          stacked = false
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/Kinesis", "IncomingRecords", "StreamName", aws_kinesis_stream.security_events.name],
            ["AWS/Kinesis", "IncomingBytes", "StreamName", aws_kinesis_stream.security_events.name],
            ["AWS/Kinesis", "OutgoingRecords", "StreamName", aws_kinesis_stream.security_events.name],
            ["AWS/Kinesis", "OutgoingBytes", "StreamName", aws_kinesis_stream.security_events.name]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Kinesis Stream Activity"
          view   = "timeSeries"
          stacked = false
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 8
        height = 6

        properties = {
          metrics = [
            ["AWS/S3", "BucketSizeBytes", "BucketName", aws_s3_bucket.security_data_lake.bucket, "StorageType", "StandardStorage"],
            ["AWS/S3", "NumberOfObjects", "BucketName", aws_s3_bucket.security_data_lake.bucket, "StorageType", "AllStorageTypes"]
          ]
          period = 86400
          stat   = "Average"
          region = var.aws_region
          title  = "S3 Data Lake Growth"
          view   = "timeSeries"
        }
      },
      {
        type   = "metric"
        x      = 8
        y      = 6
        width  = 8
        height = 6

        properties = {
          metrics = [
            ["AWS/SNS", "NumberOfMessagesPublished", "TopicName", aws_sns_topic.security_alerts.name],
            ["AWS/SNS", "NumberOfNotificationsDelivered", "TopicName", aws_sns_topic.security_alerts.name],
            ["AWS/SNS", "NumberOfNotificationsFailed", "TopicName", aws_sns_topic.security_alerts.name]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Security Alerts"
          view   = "timeSeries"
        }
      },
      {
        type   = "metric"
        x      = 16
        y      = 6
        width  = 8
        height = 6

        properties = {
          metrics = [
            ["AWS/CloudTrail", "ErrorCount", "TrailName", aws_cloudtrail.security_trail.name],
            ["AWS/CloudTrail", "TotalEvents", "TrailName", aws_cloudtrail.security_trail.name]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "CloudTrail Activity"
          view   = "timeSeries"
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 12
        width  = 24
        height = 6

        properties = {
          query = "SOURCE '/aws/lambda/${aws_lambda_function.event_processor.function_name}'\n| fields @timestamp, @message\n| filter @message like /Processing complete/\n| sort @timestamp desc\n| limit 100"
          region = var.aws_region
          title  = "Recent Lambda Processing Events"
          view   = "table"
        }
      }
    ]
  })
}

# Custom Metrics Dashboard for Security Analytics
resource "aws_cloudwatch_dashboard" "security_metrics" {
  dashboard_name = "${var.project_name}-security-metrics-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "number"
        x      = 0
        y      = 0
        width  = 6
        height = 6

        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", "FunctionName", aws_lambda_function.event_processor.function_name]
          ]
          period = 3600
          stat   = "Sum"
          region = var.aws_region
          title  = "Events Processed (Last Hour)"
          view   = "singleValue"
        }
      },
      {
        type   = "number"
        x      = 6
        y      = 0
        width  = 6
        height = 6

        properties = {
          metrics = [
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.event_processor.function_name]
          ]
          period = 3600
          stat   = "Sum"
          region = var.aws_region
          title  = "Processing Errors (Last Hour)"
          view   = "singleValue"
        }
      },
      {
        type   = "number"
        x      = 12
        y      = 0
        width  = 6
        height = 6

        properties = {
          metrics = [
            ["AWS/SNS", "NumberOfMessagesPublished", "TopicName", aws_sns_topic.security_alerts.name]
          ]
          period = 3600
          stat   = "Sum"
          region = var.aws_region
          title  = "Security Alerts (Last Hour)"
          view   = "singleValue"
        }
      },
      {
        type   = "number"
        x      = 18
        y      = 0
        width  = 6
        height = 6

        properties = {
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.event_processor.function_name]
          ]
          period = 3600
          stat   = "Average"
          region = var.aws_region
          title  = "Avg Processing Time (ms)"
          view   = "singleValue"
        }
      }
    ]
  })
}

# Cost Tracking Dashboard
resource "aws_cloudwatch_dashboard" "cost_tracking" {
  dashboard_name = "${var.project_name}-cost-tracking-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "log"
        x      = 0
        y      = 0
        width  = 12
        height = 8

        properties = {
          query = "fields @timestamp, @message\n| filter @message like /REPORT/\n| parse @message /Duration: (?<duration>\\d+\\.\\d+) ms.*Billed Duration: (?<billed_duration>\\d+) ms.*Memory Size: (?<memory_size>\\d+) MB.*Max Memory Used: (?<max_memory>\\d+) MB/\n| stats avg(duration), avg(max_memory), count() by bin(5m)"
          region = var.aws_region
          title  = "Lambda Resource Utilization"
          view   = "table"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 8

        properties = {
          metrics = [
            ["AWS/Kinesis", "IncomingBytes", "StreamName", aws_kinesis_stream.security_events.name],
            ["AWS/S3", "BucketSizeBytes", "BucketName", aws_s3_bucket.security_data_lake.bucket, "StorageType", "StandardStorage"]
          ]
          period = 3600
          stat   = "Average"
          region = var.aws_region
          title  = "Data Volume (Cost Drivers)"
          view   = "timeSeries"
        }
      }
    ]
  })
}

# Output dashboard URLs
output "dashboard_urls" {
  description = "CloudWatch dashboard URLs"
  value = {
    security_analytics = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.security_analytics.dashboard_name}"
    security_metrics   = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.security_metrics.dashboard_name}"
    cost_tracking     = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.cost_tracking.dashboard_name}"
  }
}
