# Output values for the ECS service module

output "service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.service.name
}

output "service_arn" {
  description = "ARN of the ECS service"
  value       = aws_ecs_service.service.id
}

output "task_definition_arn" {
  description = "ARN of the task definition"
  value       = aws_ecs_task_definition.service.arn
}

output "task_definition_family" {
  description = "Family of the task definition"
  value       = aws_ecs_task_definition.service.family
}

output "task_definition_revision" {
  description = "Revision of the task definition"
  value       = aws_ecs_task_definition.service.revision
}

output "auto_scaling_target_arn" {
  description = "ARN of the auto scaling target"
  value       = aws_appautoscaling_target.ecs_target.arn
}

output "scale_up_policy_arn" {
  description = "ARN of the scale up policy"
  value       = aws_appautoscaling_policy.scale_up.arn
}

output "scale_down_policy_arn" {
  description = "ARN of the scale down policy"
  value       = aws_appautoscaling_policy.scale_down.arn
}
