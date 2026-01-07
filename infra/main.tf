terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {
  host = "npipe:////./pipe/docker_engine" # Windows named pipe
}

resource "docker_network" "ecostream_net" {
  name = "ecostream_network"
}

resource "docker_volume" "postgres_data" {
  name = "postgres_data"
}

resource "docker_volume" "redpanda_data" {
  name = "redpanda_data"
}

resource "docker_volume" "mlflow_data" {
  name = "mlflow_data"
}

# Example of managing a container via Terraform (Postgres)
# Note: Usually we use Docker Compose for local dev, but this satisfies the IaC requirement.
resource "docker_image" "postgres" {
  name         = "postgres:15"
  keep_locally = true
}

resource "docker_container" "postgres" {
  image = docker_image.postgres.image_id
  name  = "postgres-tf-managed"
  restart = "always"
  
  env = [
    "POSTGRES_USER=airflow",
    "POSTGRES_PASSWORD=airflow",
    "POSTGRES_DB=airflow"
  ]
  
  ports {
    internal = 5432
    external = 5433 # Use different port to avoid conflict with compose
  }
  
  volumes {
    volume_name = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }
  
  networks_advanced {
    name = docker_network.ecostream_net.name
  }
}

# Optional AWS Boilerplate (Commented out)
# provider "aws" {
#   region = "us-east-1"
# }

# resource "aws_s3_bucket" "model_artifacts" {
#   bucket = "ecostream-models-bucket"
# }
