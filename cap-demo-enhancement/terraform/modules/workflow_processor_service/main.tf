
# workflow_processor_service ECS Service Module
variable "cluster_id" {
  description = "ECS Cluster ID"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for the service"
  type        = list(string)
}

variable "security_group_ids" {
  description = "Security group IDs"
  type        = list(string)
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

# Basic ECS service configuration
resource "aws_ecs_service" "workflow_processor_service" {
  name            = "workflow-processor-service"
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.workflow_processor_service.arn
  desired_count   = 1
  
  deployment_configuration {
    maximum_percent         = 200
    minimum_healthy_percent = 50
  }
  
  network_configuration {
    subnets         = var.subnet_ids
    security_groups = var.security_group_ids
  }
}

resource "aws_ecs_task_definition" "workflow_processor_service" {
  family             = "workflow-processor-service"
  network_mode       = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                = "256"
  memory             = "512"
  execution_role_arn = aws_iam_role.workflow_processor_service_execution.arn
  task_role_arn      = aws_iam_role.workflow_processor_service_task.arn
  
  container_definitions = jsonencode([
    {
      name  = "workflow-processor-service"
      image = "nginx:latest"  # Placeholder image
      
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/workflow-processor-service"
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

# IAM roles for the service
resource "aws_iam_role" "workflow_processor_service_execution" {
  name = "workflow-processor-service-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role" "workflow_processor_service_task" {
  name = "workflow-processor-service-task-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "workflow_processor_service_execution_policy" {
  role       = aws_iam_role.workflow_processor_service_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

output "service_name" {
  value = aws_ecs_service.workflow_processor_service.name
}

output "task_definition_arn" {
  value = aws_ecs_task_definition.workflow_processor_service.arn
}
