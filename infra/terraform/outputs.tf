output "jenkins_ip" {
  description = "IP publique de la VM Jenkins"
  value       = aws_instance.jenkins.public_ip
}

output "kubernetes_ip" {
  description = "IP publique de la VM Kubernetes"
  value       = aws_instance.kubernetes.public_ip
}

output "url_jenkins" {
  value = "http://${aws_instance.jenkins.public_ip}:8080"
}

output "url_application" {
  value = "http://${aws_instance.kubernetes.public_ip}"
}
