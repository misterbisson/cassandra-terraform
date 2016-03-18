# cassandra-terraform

Follow these steps to get a 3 node cassandra cluster up and running.

* Install terraform.

* Create a vpc with cidr block "172.31.0.0/16" and allow public hostnames and dns resolution.
If you don't allow public hostnames and dns nothing will work and may fail mysterously down the
road.

* ```cp terraform.tfvars.template terraform.tfvars```

* Populate terraform.tfvars with proper values (you will need the vpc id from step 2)

* run
  ```
  terraform get
  ```

That should bring down the external module for cassandra security groups.

* run
  ```
  terraform plan
  ```

Review what is going to happen.

* run
  ```
  terraform apply
  ```

To bring up resources.  At the end you should get the public IP address
of your nodes.  run ```terraform show``` at any time to get those public ips
for the next steps.

*  Once your instances are up, ssh into each instance.  cassandra_0 and cassandra_1 are seed
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

After all the nodes are up and waiting for connection (tail -f /var/log/cassandra/system.out)
  ```
  ubuntu@ip-172-31-32-53:~$ nodetool status
  Datacenter: datacenter1
  =======================
  Status=Up/Down
  |/ State=Normal/Leaving/Joining/Moving
  --  Address       Load       Tokens       Owns    Host ID                               Rack
  UN  172.31.32.53  87.77 KB   256          ?       26b35699-6e4d-45b9-ac02-8849fbc66e90  rack1
  UN  172.31.32.52  90.29 KB   256          ?       0aa4225d-2679-453f-8ef7-36e2f882beb5  rack1
  UN  172.31.32.51  83.73 KB   256          ?       fbc39852-e7b0-4246-8542-f8e4ae8daaaa  rack1
  ```


* You are using resources which is costing you money.  Lets tear it down.
As in the previous step ssh into each node and run the following to stop
cassandra and unmount the data drives.  If you don't do this terraform won't
be able to properly destroy your resources and you will have to manually
destroy the volumes before terraform can finish its work.

  ```
  sudo service cassandra stop
  sudo umount /var/lib/cassandra
  ```

