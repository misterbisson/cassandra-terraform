# cassandra-terraform

Automate creation of new cassandra clusters in EC2 with terraform

1. Install terraform.

2. Create a vpc with cidr block "172.31.0.0/16" and allow public hostnames and dns resolution.
If you don't allow public hostnames and dns nothing will work and may fail mysterously down the
road.

3. cp terraform.tfvars.template terraform.tfvars

4. Populate terraform.tfvars with proper values (you will need the vpc id from step 2)

5. run:
```
terraform get
```

That should bring down the external module for cassandra security groups.
6. run:
```
terraform plan
```

Review what is going to happen.

7. run:
```
terraform apply
```

To bring up resources.  At the end you should get the public IP address
of your nodes.  run ```terraform show``` at any time to get those public ips
for the next steps.

8.  Once your instances are up, ssh into each instance.  cassandra_0 and cassandra_1 are seed
nodes so you must do those one at a time.

On each node in sequence do the following steps:

```
ssh -i <path2key>.pem ubuntu@<cassandra_0_ip>
bash /tmp/provisioning/setup_cassandra.sh 0

ssh -i <path2key>.pem ubuntu@<cassandra_1_ip>
bash /tmp/provisioning/setup_cassandra.sh 1

ssh -i <path2key>.pem ubuntu@<cassandra_2_ip>
bash /tmp/provisioning/setup_cassandra.sh 2
```

9. You are using resources which is costing you money.  Lets tear it down.
As in the previous step ssh into each node and run the following to stop
cassandra and unmount the data drives.  If you don't do this terraform won't
be able to properly destroy your resources and you will have to manually
destroy the volumes before terraform can finish its work.

```
sudo service cassandra stop
sudo umount /var/lib/cassandra
```

