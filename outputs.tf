output "cassandra_0" {
    value = "${aws_instance.cassandra_0.public_ip}"
}

output "cassandra_1" {
  value = "${aws_instance.cassandra_1.public_ip}"
}

output "cassandra_2" {
  value = "${aws_instance.cassandra_2.public_ip}"
}

output "cassandra_0_vol_id" {
  value = "${aws_ebs_volume.cassandra_0.id}"
}

output "cassandra_1_vol_id" {
  value = "${aws_ebs_volume.cassandra_1.id}"
}

output "cassandra_2_vol_id" {
  value = "${aws_ebs_volume.cassandra_2.id}"
}


