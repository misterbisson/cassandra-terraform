resource "aws_instance" "cassandra_0" {
  instance_type = "${var.instance_type}"
  ami = "ami-412dcf21"
  key_name = "${var.ssh_key_name}"
  private_ip = "172.31.32.51"
  subnet_id = "${aws_subnet.main.id}"
  vpc_security_group_ids = ["${module.cassandra_security_group.security_group_id}", "${aws_security_group.allow_internet_access.id}", "${aws_security_group.allow_all_ssh_access.id}"]
  depends_on = ["aws_internet_gateway.gw"]

  tags {
    Name = "${var.user_name}_cassandra_0"
  }

  provisioner "remote-exec" {
    inline = ["sudo mkdir -p /tmp/provisioning",
      "sudo chown -R ubuntu:ubuntu  /tmp/provisioning/"]
    connection {
      type = "ssh"
      user = "ubuntu"
      private_key = "${file(var.ssh_key_path)}"
    }
  }

  provisioner "file" {
    source = "provisioning/setup_cassandra.sh"
    destination = "/tmp/provisioning/setup_cassandra.sh"
    connection {
      type = "ssh"
      user = "ubuntu"
      private_key = "${file(var.ssh_key_path)}"
    }
  }

  provisioner "file" {
    source = "provisioning/restore_from_snapshot.sh"
    destination = "/tmp/provisioning/restore_from_snapshot.sh"
    connection {
      type = "ssh"
      user = "ubuntu"
      private_key = "${file(var.ssh_key_path)}"
    }
  }
}

resource "aws_instance" "cassandra_1" {
  instance_type = "${var.instance_type}"
  ami = "ami-412dcf21"
  key_name = "${var.ssh_key_name}"
  private_ip = "172.31.32.52"
  subnet_id = "${aws_subnet.main.id}"
  vpc_security_group_ids = ["${module.cassandra_security_group.security_group_id}", "${aws_security_group.allow_internet_access.id}", "${aws_security_group.allow_all_ssh_access.id}"]
  depends_on = ["aws_internet_gateway.gw", "aws_instance.cassandra_0"]

  tags {
    Name = "${var.user_name}_cassandra_1"
  }

  provisioner "remote-exec" {
    inline = ["sudo mkdir -p /tmp/provisioning",
      "sudo chown -R ubuntu:ubuntu  /tmp/provisioning/"]
    connection {
      type = "ssh"
      user = "ubuntu"
      private_key = "${file(var.ssh_key_path)}"
    }
  }

  provisioner "file" {
    source = "provisioning/setup_cassandra.sh"
    destination = "/tmp/provisioning/setup_cassandra.sh"
    connection {
      type = "ssh"
      user = "ubuntu"
      private_key = "${file(var.ssh_key_path)}"
    }
  }
  
  provisioner "file" {
    source = "provisioning/restore_from_snapshot.sh"
    destination = "/tmp/provisioning/restore_from_snapshot.sh"
    connection {
      type = "ssh"
      user = "ubuntu"
      private_key = "${file(var.ssh_key_path)}"
    }
  }
}


resource "aws_instance" "cassandra_2" {
  instance_type = "${var.instance_type}"
  ami = "ami-412dcf21"
  key_name = "${var.ssh_key_name}"
  private_ip = "172.31.32.53"
  subnet_id = "${aws_subnet.main.id}"
  vpc_security_group_ids = ["${module.cassandra_security_group.security_group_id}", "${aws_security_group.allow_internet_access.id}", "${aws_security_group.allow_all_ssh_access.id}"]
  depends_on = ["aws_internet_gateway.gw", "aws_instance.cassandra_1"]

  tags {
    Name = "${var.user_name}_cassandra_2"
  }

  provisioner "remote-exec" {
    inline = ["sudo mkdir -p /tmp/provisioning",
      "sudo chown -R ubuntu:ubuntu  /tmp/provisioning/"]
    connection {
      type = "ssh"
      user = "ubuntu"
      private_key = "${file(var.ssh_key_path)}"
    }
  }

  provisioner "file" {
    source = "provisioning/setup_cassandra.sh"
    destination = "/tmp/provisioning/setup_cassandra.sh"
    connection {
      type = "ssh"
      user = "ubuntu"
      private_key = "${file(var.ssh_key_path)}"
    }
  }
  
  provisioner "file" {
    source = "provisioning/restore_from_snapshot.sh"
    destination = "/tmp/provisioning/restore_from_snapshot.sh"
    connection {
      type = "ssh"
      user = "ubuntu"
      private_key = "${file(var.ssh_key_path)}"
    }
  }
}


resource "aws_ebs_volume" "cassandra_0" {
  availability_zone = "us-west-2a"
  size = 500
  type = "gp2"
  # snapshot_id="snap-0299ea162fd4d14c7"
  tags {
    Name = "${var.user_name}_cassandra_0"
  }
}

resource "aws_ebs_volume" "cassandra_1" {
  availability_zone = "us-west-2a"
  size = 500
  type = "gp2"
  # snapshot_id="snap-0fdd1bd9b12b6fe51"
  tags {
    Name = "${var.user_name}_cassandra_1"
  }
}

resource "aws_ebs_volume" "cassandra_2" {
  availability_zone = "us-west-2a"
  size = 500
  type = "gp2"
  # snapshot_id="snap-0774a8e08c0b6f205"
  tags {
    Name = "${var.user_name}_cassandra_2"
  }
}

resource "aws_volume_attachment" "cassandra_0_ebs_att" {
  device_name = "/dev/sdh"
  volume_id = "${aws_ebs_volume.cassandra_0.id}"
  instance_id = "${aws_instance.cassandra_0.id}"
}

resource "aws_volume_attachment" "cassandra_1_ebs_att" {
  device_name = "/dev/sdh"
  volume_id = "${aws_ebs_volume.cassandra_1.id}"
  instance_id = "${aws_instance.cassandra_1.id}"
}

resource "aws_volume_attachment" "cassandra_2_ebs_att" {
  device_name = "/dev/sdh"
  volume_id = "${aws_ebs_volume.cassandra_2.id}"
  instance_id = "${aws_instance.cassandra_2.id}"
}

