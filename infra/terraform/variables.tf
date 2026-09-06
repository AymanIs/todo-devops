variable "region" {
  description = "Region AWS utilisee pour le projet"
  type        = string
  default     = "eu-west-3"
}

variable "prefixe" {
  description = "Prefixe applique au nom des ressources"
  type        = string
  default     = "todo-devops"
}

variable "type_jenkins" {
  description = "Taille de la VM Jenkins"
  type        = string
  default     = "t3.medium"
}

variable "type_k8s" {
  description = "Taille de la VM Kubernetes (minikube demande 2 vCPU minimum)"
  type        = string
  default     = "t3.medium"
}

variable "cle_publique" {
  description = "Chemin de la cle publique SSH injectee dans les VM"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "ip_admin" {
  description = "Adresse autorisee a joindre SSH, Jenkins et l'application"
  type        = string
  default     = "0.0.0.0/0"
}
