output "alb_dns_name"      { value = module.app.alb_dns_name }
output "ecr_repository_url" { value = module.app.ecr_repository_url }
output "ecs_cluster_name"   { value = module.app.ecs_cluster_name }
