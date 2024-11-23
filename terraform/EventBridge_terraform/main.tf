provider "aws" {
  region = "eu-west-2"
}

resource "aws_iam_role" "iam_role" {
  name = var.IAM_ROLE_NAME
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "ecs_run_task_policy" {
  name        = var.IAM_POLICY
  description = "Allows ECS tasks to be run and pass roles"
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ecs:RunTask"
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = "iam:PassRole"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_ecs_run_task_policy" {
  role       = aws_iam_role.iam_role.name
  policy_arn = aws_iam_policy.ecs_run_task_policy.arn
}

resource "aws_cloudwatch_event_rule" "event_rule" {
  name        = var.EVENT_RULE
  event_bus_name = "default" 
  event_pattern = jsonencode({
    source      = ["aws.s3"],
    "detail-type" = ["Object Created"],
    detail = {
      bucket = {
        name = [var.BUCKET_NAME]
      },
      object = {
        key = [var.FILE_NAME]
      }
    }
  })
}

data "aws_ecs_task_definition" "latest_ecs_task" {
  task_definition = var.ECS_TASK
}

resource "aws_cloudwatch_event_target" "event_target" {
  rule          = aws_cloudwatch_event_rule.event_rule.name
  arn           = var.CLUSTER_ARN 
  role_arn      = aws_iam_role.iam_role.arn
  ecs_target {
    task_definition_arn = data.aws_ecs_task_definition.latest_ecs_task.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets          = var.SUBNETS
      security_groups  = var.SECURITY_GROUPS
      assign_public_ip = true
    }
  }
}
