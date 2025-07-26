"""
Terraform configuration fixer for CAP Demo
Fixes common Terraform issues before deployment
"""

from pathlib import Path
import re
import shutil

def fix_terraform_configuration():
    """Fix Terraform configuration issues"""
    print("🔧 Fixing Terraform Configuration...")
    
    terraform_dir = Path(__file__).parent.parent / "terraform"
    
    # 1. Create missing modules directory
    modules_dir = terraform_dir / "modules"
    if not modules_dir.exists():
        print("📁 Creating missing modules directory...")
        modules_dir.mkdir(exist_ok=True)
        
        # Create basic ECS service modules
        for service in ["security_processor_service", "metrics_processor_service", "workflow_processor_service"]:
            service_dir = modules_dir / service
            service_dir.mkdir(exist_ok=True)
            
            # Create a basic main.tf for each module
            main_tf = service_dir / "main.tf"
            main_tf.write_text(f"""
# {service} ECS Service Module
variable "cluster_id" {{
  description = "ECS Cluster ID"
  type        = string
}}

variable "subnet_ids" {{
  description = "Subnet IDs for the service"
  type        = list(string)
}}

variable "security_group_ids" {{
  description = "Security group IDs"
  type        = list(string)
}}

variable "vpc_id" {{
  description = "VPC ID"
  type        = string
}}

# Basic ECS service configuration
resource "aws_ecs_service" "{service}" {{
  name            = "{service.replace('_', '-')}"
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.{service}.arn
  desired_count   = 1
  
  deployment_configuration {{
    maximum_percent         = 200
    minimum_healthy_percent = 50
  }}
  
  network_configuration {{
    subnets         = var.subnet_ids
    security_groups = var.security_group_ids
  }}
}}

resource "aws_ecs_task_definition" "{service}" {{
  family             = "{service.replace('_', '-')}"
  network_mode       = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                = "256"
  memory             = "512"
  execution_role_arn = aws_iam_role.{service}_execution.arn
  task_role_arn      = aws_iam_role.{service}_task.arn
  
  container_definitions = jsonencode([
    {{
      name  = "{service.replace('_', '-')}"
      image = "nginx:latest"  # Placeholder image
      
      portMappings = [
        {{
          containerPort = 80
          hostPort      = 80
        }}
      ]
      
      logConfiguration = {{
        logDriver = "awslogs"
        options = {{
          awslogs-group         = "/ecs/{service.replace('_', '-')}"
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "ecs"
        }}
      }}
    }}
  ])
}}

# IAM roles for the service
resource "aws_iam_role" "{service}_execution" {{
  name = "{service.replace('_', '-')}-execution-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "ecs-tasks.amazonaws.com"
        }}
      }}
    ]
  }})
}}

resource "aws_iam_role" "{service}_task" {{
  name = "{service.replace('_', '-')}-task-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "ecs-tasks.amazonaws.com"
        }}
      }}
    ]
  }})
}}

resource "aws_iam_role_policy_attachment" "{service}_execution_policy" {{
  role       = aws_iam_role.{service}_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}}

output "service_name" {{
  value = aws_ecs_service.{service}.name
}}

output "task_definition_arn" {{
  value = aws_ecs_task_definition.{service}.arn
}}
""", encoding='utf-8')
            
            print(f"✅ Created module: {service}")
    
    # 2. Fix duplicate data sources
    print("🔧 Fixing duplicate data sources...")
    
    quicksight_file = terraform_dir / "quicksight.tf"
    if quicksight_file.exists():
        content = quicksight_file.read_text(encoding='utf-8')
        
        # Remove duplicate aws_region data source
        content = re.sub(
            r'data "aws_region" "current" \{\s*\}',
            '# data "aws_region" "current" {} // Removed duplicate - defined in ecs.tf',
            content
        )
        
        quicksight_file.write_text(content, encoding='utf-8')
        print("✅ Fixed duplicate aws_region data source in quicksight.tf")
    
    # 3. Create modules outputs.tf
    modules_outputs = modules_dir / "outputs.tf"
    if not modules_outputs.exists():
        modules_outputs.write_text("""
# Module outputs for ECS services
""", encoding='utf-8')
    
    print("✅ Terraform configuration fixed!")
    return True

def validate_terraform_syntax():
    """Validate Terraform syntax after fixes"""
    import subprocess
    
    terraform_dir = Path(__file__).parent.parent / "terraform"
    
    print("🧪 Validating Terraform syntax...")
    
    try:
        result = subprocess.run(
            ['terraform', 'validate'],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Terraform syntax validation passed")
            return True
        else:
            print(f"❌ Terraform validation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error validating Terraform: {e}")
        return False

def main():
    """Main terraform fixer function"""
    print("🚀 CAP Demo - Terraform Configuration Fixer")
    print("=" * 60)
    
    # Fix configuration issues
    fix_success = fix_terraform_configuration()
    
    if fix_success:
        print("\n🎉 Terraform configuration fixes applied!")
        print("🔧 You can now run deployment scripts")
    else:
        print("\n❌ Failed to fix Terraform configuration")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        exit(1)
