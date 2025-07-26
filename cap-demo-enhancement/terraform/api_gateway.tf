# ============================================================================
# CAP Demo - Phase 3: API Gateway & Customer Self-Service Portal
# Customer-facing APIs for data access and workflow automation
# ============================================================================

# ============================================================================
# API Gateway REST API
# ============================================================================

resource "aws_api_gateway_rest_api" "cap_demo_api" {
  name        = "${var.environment}-${var.project_name}-customer-api"
  description = "CAP Demo Customer Self-Service API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-customer-api"
    Component   = "api"
    Phase       = "3"
  })
}

# ============================================================================
# API Gateway Resources Structure
# ============================================================================

# /customers resource
resource "aws_api_gateway_resource" "customers" {
  rest_api_id = aws_api_gateway_rest_api.cap_demo_api.id
  parent_id   = aws_api_gateway_rest_api.cap_demo_api.root_resource_id
  path_part   = "customers"
}

# /customers/{customer_id} resource
resource "aws_api_gateway_resource" "customer_by_id" {
  rest_api_id = aws_api_gateway_rest_api.cap_demo_api.id
  parent_id   = aws_api_gateway_resource.customers.id
  path_part   = "{customer_id}"
}

# /customers/{customer_id}/metrics resource
resource "aws_api_gateway_resource" "customer_metrics" {
  rest_api_id = aws_api_gateway_rest_api.cap_demo_api.id
  parent_id   = aws_api_gateway_resource.customer_by_id.id
  path_part   = "metrics"
}

# /customers/{customer_id}/security resource
resource "aws_api_gateway_resource" "customer_security" {
  rest_api_id = aws_api_gateway_rest_api.cap_demo_api.id
  parent_id   = aws_api_gateway_resource.customer_by_id.id
  path_part   = "security"
}

# /customers/{customer_id}/alerts resource
resource "aws_api_gateway_resource" "customer_alerts" {
  rest_api_id = aws_api_gateway_rest_api.cap_demo_api.id
  parent_id   = aws_api_gateway_resource.customer_by_id.id
  path_part   = "alerts"
}

# /onboarding resource
resource "aws_api_gateway_resource" "onboarding" {
  rest_api_id = aws_api_gateway_rest_api.cap_demo_api.id
  parent_id   = aws_api_gateway_rest_api.cap_demo_api.root_resource_id
  path_part   = "onboarding"
}

# /topics resource for Kafka topic management
resource "aws_api_gateway_resource" "topics" {
  rest_api_id = aws_api_gateway_rest_api.cap_demo_api.id
  parent_id   = aws_api_gateway_rest_api.cap_demo_api.root_resource_id
  path_part   = "topics"
}

# ============================================================================
# Lambda Functions for API Backend
# ============================================================================

# Customer Metrics API Lambda
resource "aws_lambda_function" "customer_metrics_api" {
  filename         = "lambda_placeholder.zip"
  function_name    = "${var.environment}-${var.project_name}-customer-metrics-api"
  role            = aws_iam_role.api_lambda_role.arn
  handler         = "index.lambda_handler"
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      BRONZE_BUCKET = aws_s3_bucket.bronze_layer.bucket
      SILVER_BUCKET = aws_s3_bucket.silver_layer.bucket
      GOLD_BUCKET   = aws_s3_bucket.gold_layer.bucket
      # Temporarily disabled - depends on QuickSight resources
      # ATHENA_DATABASE = aws_glue_catalog_database.cap_demo_data_lake.name
      # ATHENA_WORKGROUP = aws_athena_workgroup.cap_demo_analytics.name
      ATHENA_DATABASE = "cap_demo_database"
      ATHENA_WORKGROUP = "cap_demo_workgroup"
    }
  }

  depends_on = [aws_iam_role_policy_attachment.api_lambda_policy]

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-customer-metrics-api"
    Component   = "api"
    Phase       = "3"
  })
}

# Customer Security API Lambda
resource "aws_lambda_function" "customer_security_api" {
  filename         = "lambda_placeholder.zip"
  function_name    = "${var.environment}-${var.project_name}-customer-security-api"
  role            = aws_iam_role.api_lambda_role.arn
  handler         = "index.lambda_handler"
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      BRONZE_BUCKET = aws_s3_bucket.bronze_layer.bucket
      SILVER_BUCKET = aws_s3_bucket.silver_layer.bucket
      # Temporarily disabled - depends on QuickSight resources
      # ATHENA_DATABASE = aws_glue_catalog_database.cap_demo_data_lake.name
      # ATHENA_WORKGROUP = aws_athena_workgroup.cap_demo_analytics.name
      ATHENA_DATABASE = "cap_demo_database"
      ATHENA_WORKGROUP = "cap_demo_workgroup"
    }
  }

  depends_on = [aws_iam_role_policy_attachment.api_lambda_policy]

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-customer-security-api"
    Component   = "api"
    Phase       = "3"
  })
}

# Customer Onboarding API Lambda
resource "aws_lambda_function" "customer_onboarding_api" {
  filename         = "lambda_placeholder.zip"
  function_name    = "${var.environment}-${var.project_name}-customer-onboarding-api"
  role            = aws_iam_role.api_lambda_role.arn
  handler         = "index.lambda_handler"
  runtime         = "python3.11"
  timeout         = 60

  environment {
    variables = {
      MSK_CLUSTER_ARN = aws_msk_cluster.cap_demo.arn
      KAFKA_BOOTSTRAP_SERVERS = aws_msk_cluster.cap_demo.bootstrap_brokers_tls
      DDB_TABLE = aws_dynamodb_table.customer_metadata.name
    }
  }

  depends_on = [aws_iam_role_policy_attachment.api_lambda_policy]

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-customer-onboarding-api"
    Component   = "api"
    Phase       = "3"
  })
}

# ============================================================================
# DynamoDB for Customer Metadata
# ============================================================================

resource "aws_dynamodb_table" "customer_metadata" {
  name           = "${var.environment}-${var.project_name}-customer-metadata"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "customer_id"

  attribute {
    name = "customer_id"
    type = "S"
  }

  attribute {
    name = "onboarding_status"
    type = "S"
  }

  global_secondary_index {
    name               = "OnboardingStatusIndex"
    hash_key           = "onboarding_status"
    projection_type    = "ALL"
  }

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-customer-metadata"
    Component   = "api"
    Phase       = "3"
  })
}

# ============================================================================
# IAM Roles for API Lambda Functions
# ============================================================================

resource "aws_iam_role" "api_lambda_role" {
  name = "${var.environment}-${var.project_name}-api-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-api-lambda-role"
    Component   = "api"
    Phase       = "3"
  })
}

# Lambda execution policy for API functions
resource "aws_iam_policy" "api_lambda_policy" {
  name        = "${var.environment}-${var.project_name}-api-lambda-policy"
  description = "Policy for CAP Demo API Lambda functions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:PutObject"
        ]
        Resource = [
          aws_s3_bucket.bronze_layer.arn,
          "${aws_s3_bucket.bronze_layer.arn}/*",
          aws_s3_bucket.silver_layer.arn,
          "${aws_s3_bucket.silver_layer.arn}/*",
          aws_s3_bucket.gold_layer.arn,
          "${aws_s3_bucket.gold_layer.arn}/*"
        ]
      },
      # Temporarily disabled - depends on QuickSight resources
      # {
      #   Effect = "Allow"
      #   Action = [
      #     "athena:GetQueryExecution",
      #     "athena:GetQueryResults",
      #     "athena:StartQueryExecution",
      #     "athena:StopQueryExecution"
      #   ]
      #   Resource = [
      #     aws_athena_workgroup.cap_demo_analytics.arn
      #   ]
      # },
      # {
      #   Effect = "Allow"
      #   Action = [
      #     "glue:GetTable",
      #     "glue:GetDatabase", 
      #     "glue:GetPartitions"
      #   ]
      #   Resource = [
      #     "arn:aws:glue:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:catalog",
      #     "arn:aws:glue:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:database/${aws_glue_catalog_database.cap_demo_data_lake.name}",
      #     "arn:aws:glue:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/${aws_glue_catalog_database.cap_demo_data_lake.name}/*"
      #   ]
      # },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.customer_metadata.arn,
          "${aws_dynamodb_table.customer_metadata.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kafka:DescribeCluster",
          "kafka:GetBootstrapBrokers"
        ]
        Resource = [
          aws_msk_cluster.cap_demo.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "api_lambda_policy" {
  role       = aws_iam_role.api_lambda_role.name
  policy_arn = aws_iam_policy.api_lambda_policy.arn
}

# ============================================================================
# API Gateway Methods
# ============================================================================

# GET /customers/{customer_id}/metrics
resource "aws_api_gateway_method" "get_customer_metrics" {
  rest_api_id   = aws_api_gateway_rest_api.cap_demo_api.id
  resource_id   = aws_api_gateway_resource.customer_metrics.id
  http_method   = "GET"
  authorization = "AWS_IAM"

  request_parameters = {
    "method.request.path.customer_id" = true
    "method.request.querystring.start_date" = false
    "method.request.querystring.end_date" = false
    "method.request.querystring.metric_type" = false
  }
}

resource "aws_api_gateway_integration" "get_customer_metrics" {
  rest_api_id = aws_api_gateway_rest_api.cap_demo_api.id
  resource_id = aws_api_gateway_resource.customer_metrics.id
  http_method = aws_api_gateway_method.get_customer_metrics.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.customer_metrics_api.invoke_arn
}

# GET /customers/{customer_id}/security
resource "aws_api_gateway_method" "get_customer_security" {
  rest_api_id   = aws_api_gateway_rest_api.cap_demo_api.id
  resource_id   = aws_api_gateway_resource.customer_security.id
  http_method   = "GET"
  authorization = "AWS_IAM"

  request_parameters = {
    "method.request.path.customer_id" = true
    "method.request.querystring.start_date" = false
    "method.request.querystring.end_date" = false
    "method.request.querystring.severity" = false
  }
}

resource "aws_api_gateway_integration" "get_customer_security" {
  rest_api_id = aws_api_gateway_rest_api.cap_demo_api.id
  resource_id = aws_api_gateway_resource.customer_security.id
  http_method = aws_api_gateway_method.get_customer_security.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.customer_security_api.invoke_arn
}

# POST /onboarding - Customer onboarding workflow
resource "aws_api_gateway_method" "post_onboarding" {
  rest_api_id   = aws_api_gateway_rest_api.cap_demo_api.id
  resource_id   = aws_api_gateway_resource.onboarding.id
  http_method   = "POST"
  authorization = "AWS_IAM"
}

resource "aws_api_gateway_integration" "post_onboarding" {
  rest_api_id = aws_api_gateway_rest_api.cap_demo_api.id
  resource_id = aws_api_gateway_resource.onboarding.id
  http_method = aws_api_gateway_method.post_onboarding.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.customer_onboarding_api.invoke_arn
}

# ============================================================================
# Lambda Permissions for API Gateway
# ============================================================================

resource "aws_lambda_permission" "api_gateway_metrics" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.customer_metrics_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.cap_demo_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_security" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.customer_security_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.cap_demo_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_onboarding" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.customer_onboarding_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.cap_demo_api.execution_arn}/*/*"
}

# ============================================================================
# API Gateway Deployment
# ============================================================================

resource "aws_api_gateway_deployment" "cap_demo_api" {
  depends_on = [
    aws_api_gateway_integration.get_customer_metrics,
    aws_api_gateway_integration.get_customer_security,
    aws_api_gateway_integration.post_onboarding
  ]

  rest_api_id = aws_api_gateway_rest_api.cap_demo_api.id
  stage_name  = var.environment

  lifecycle {
    create_before_destroy = true
  }
}

# ============================================================================
# API Gateway Custom Domain (Optional)
# ============================================================================

# CloudWatch log group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "/aws/apigateway/${aws_api_gateway_rest_api.cap_demo_api.name}"
  retention_in_days = 30

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-api-gateway-logs"
    Component   = "api"
    Phase       = "3"
  })
}

# API Gateway stage with logging
resource "aws_api_gateway_stage" "cap_demo_api" {
  deployment_id = aws_api_gateway_deployment.cap_demo_api.id
  rest_api_id   = aws_api_gateway_rest_api.cap_demo_api.id
  stage_name    = var.environment

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_logs.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      caller         = "$context.identity.caller"
      user           = "$context.identity.user"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      resourcePath   = "$context.resourcePath"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-api-gateway-stage"
    Component   = "api"
    Phase       = "3"
  })
}
