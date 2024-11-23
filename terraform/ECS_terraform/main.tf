provider "aws" {
  region = "eu-west-2"
}

resource "aws_ecs_task_definition" "ecs_task" {
  family                   = var.FAMILY
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "1024"
  memory                   = "3072"
  task_role_arn            = var.ROLE_ARN
  execution_role_arn       = var.ROLE_ARN

  container_definitions = jsonencode([
    {
      name        = var.CONTAINER
      image       = var.URI
      essential   = true
      cpu         = 0
      memory      = 3072
      memoryReservation = 1024
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
          name          = "task-port"
          appProtocol   = "http"
        }
      ]
      environment = [
        {
          name  = "AWS_ACCESS_KEY_ID"
          value = var.AWS_ACCESS_KEY_ID
        },
        {
          name  = "AWS_SECRET_ACCESS_KEY"
          value = var.AWS_SECRET_ACCESS_KEY
        },
        {
          name  = "BUCKET_NAME"
          value = var.BUCKET_NAME
        },
        {
          name  = "BUCKET_NAME_OUT"
          value = var.BUCKET_NAME_OUT
        },
        {
          name  = "FILE_NAME"
          value = var.FILE_NAME
        }
      ]
    }
  ])
}
