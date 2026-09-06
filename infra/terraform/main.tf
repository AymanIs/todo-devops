# Reseau : on reutilise le VPC par defaut de la region, suffisant pour le projet.
data "aws_vpc" "defaut" {
  default = true
}

data "aws_subnets" "publics" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.defaut.id]
  }
}

# Derniere image Ubuntu 22.04 publiee par Canonical
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_key_pair" "cle" {
  key_name   = "${var.prefixe}-cle"
  public_key = file(var.cle_publique)
}

resource "aws_security_group" "jenkins" {
  name        = "${var.prefixe}-sg-jenkins"
  description = "SSH et interface Jenkins"
  vpc_id      = data.aws_vpc.defaut.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ip_admin]
  }

  ingress {
    description = "Interface web Jenkins"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [var.ip_admin]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.prefixe}-sg-jenkins" }
}

resource "aws_security_group" "kubernetes" {
  name        = "${var.prefixe}-sg-k8s"
  description = "SSH, API Kubernetes, NodePort et NGINX"
  vpc_id      = data.aws_vpc.defaut.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ip_admin]
  }

  ingress {
    description = "NGINX (reverse proxy vers l'application)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "NodePort du service todo-app"
    from_port   = 30080
    to_port     = 30080
    protocol    = "tcp"
    cidr_blocks = [var.ip_admin]
  }

  ingress {
    description     = "API Kubernetes depuis Jenkins"
    from_port       = 6443
    to_port         = 6443
    protocol        = "tcp"
    security_groups = [aws_security_group.jenkins.id]
  }

  ingress {
    description     = "PostgreSQL depuis Jenkins"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.jenkins.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.prefixe}-sg-k8s" }
}

resource "aws_instance" "jenkins" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.type_jenkins
  subnet_id                   = data.aws_subnets.publics.ids[0]
  key_name                    = aws_key_pair.cle.key_name
  vpc_security_group_ids      = [aws_security_group.jenkins.id]
  associate_public_ip_address = true

  root_block_device {
    volume_size = 20
  }

  tags = {
    Name = "${var.prefixe}-jenkins"
    Role = "ci"
  }
}

resource "aws_instance" "kubernetes" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.type_k8s
  subnet_id                   = data.aws_subnets.publics.ids[0]
  key_name                    = aws_key_pair.cle.key_name
  vpc_security_group_ids      = [aws_security_group.kubernetes.id]
  associate_public_ip_address = true

  root_block_device {
    volume_size = 30
  }

  tags = {
    Name = "${var.prefixe}-k8s"
    Role = "runtime"
  }
}

# L'inventaire Ansible est ecrit automatiquement : plus rien a recopier a la main.
resource "local_file" "inventaire" {
  filename        = "${path.module}/../ansible/inventory.ini"
  file_permission = "0644"

  content = <<-INV
    [jenkins]
    ${aws_instance.jenkins.public_ip}

    [kubernetes]
    ${aws_instance.kubernetes.public_ip}

    [all:vars]
    ansible_user=ubuntu
    ansible_ssh_private_key_file=~/.ssh/id_rsa
    ansible_ssh_common_args='-o StrictHostKeyChecking=no'
    k8s_private_ip=${aws_instance.kubernetes.private_ip}
  INV
}
