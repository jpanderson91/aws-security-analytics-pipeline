# Cost-Optimized Terraform Variables for Security Analytics Pipeline
# This configuration prioritizes cost savings while maintaining functionality

aws_region = "us-east-1"
environment = "dev"
project_name = "security-analytics"
owner = "john-anderson-portfolio"
alert_email = "johnanderson@example.com"  # Replace with your actual email

# Cost optimization settings
kinesis_shard_count = 1                    # Minimum for functionality
data_retention_days = 30                   # Reduced from 90 days
log_level = "INFO"

# GuardDuty - Disabled initially to save ~$30-100/month
# You can enable it manually in console for testing, then disable
enable_guardduty = false

# CloudTrail - Keep enabled as it's mostly free for management events
enable_cloudtrail = true

# Lambda optimization
lambda_memory_size = 256                   # Reduced from 512MB (saves ~50% on execution cost)
lambda_timeout = 60                        # Reduced from 300 seconds

# Additional cost optimization flags (if we add them)
enable_s3_intelligent_tiering = true       # Automatically optimize storage costs
cloudwatch_log_retention_days = 7          # Reduced from 14 days
