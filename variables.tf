variable "user_name" {}
variable "access_key" {}
variable "secret_key" {}
variable "ssh_key_path" {}
variable "ssh_key_name" {}
variable "vpc_id" {}
variable "security_group_name" {}

# cannot do interolations in varables.
# default source_cidr_block is the main subnet
# defined in aws_subnet.main.cidr_block.
variable "source_cidr_block" {
  default = "172.31.32.0/20"
}

variable "region" {
  default = "us-west-2"
}
