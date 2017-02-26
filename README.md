# cassandra-terraform

Follow these steps to get a 3 node cassandra cluster up and running, back it up with ebs snapshots, tear it down and restore from ebs snapshots.

Install terraform last tested at ```Terraform v0.8.7```.

Create a vpc with cidr block "172.31.0.0/16" and allow public hostnames and dns resolution.
If you don't allow public hostnames and dns nothing will work and may fail mysterously down the
road. ```cp terraform.tfvars.template terraform.tfvars```

Populate terraform.tfvars with proper values (you will need the vpc id from step 2) run
  ```
  terraform get
  ```

That should bring down the external module for cassandra security groups. run
  ```
  terraform plan
  ```

Review what is going to happen. run
  ```
  terraform apply
  ```

To bring up resources.  At the end you should get the public IP address
of your nodes.  run ```terraform show``` at any time to get those public ips
for the next steps.

Once your instances are up, ssh into each instance.  cassandra_0 and cassandra_1 are seed
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

After all the nodes are up and waiting for connections (tail -f /var/log/cassandra/system.out)
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

Stop the nodes and take a snapshot of the data drives

First run stress to populate the data directory
```
cassandra-stress write n=1000000
After running cassandra stress on node 3:

Results:
op rate                   : 10384 [WRITE:10384]
partition rate            : 10384 [WRITE:10384]
row rate                  : 10384 [WRITE:10384]
latency mean              : 19.2 [WRITE:19.2]
latency median            : 15.9 [WRITE:15.9]
latency 95th percentile   : 40.8 [WRITE:40.8]
latency 99th percentile   : 65.5 [WRITE:65.5]
latency 99.9th percentile : 137.6 [WRITE:137.6]
latency max               : 499.1 [WRITE:499.1]
Total partitions          : 1000000 [WRITE:1000000]
Total errors              : 0 [WRITE:0]
total gc count            : 0
total gc mb               : 0
total gc time (s)         : 0
avg gc time(ms)           : NaN
stdev gc time(ms)         : 0
Total operation time      : 00:01:36
END

cqlsh:keyspace1> select * from keyspace1.standard1 limit 2;

 key                    | C0                                                                     | C1                                                                     | C2                                                                     | C3                                                                     | C4
------------------------+------------------------------------------------------------------------+------------------------------------------------------------------------+------------------------------------------------------------------------+------------------------------------------------------------------------+------------------------------------------------------------------------
 0x3650384c504f4f4d3231 | 0x4b0ffe8264f7ce71357fca02a8788e0d0795357e31cb925a549433fc0df2230b357a | 0x6422ba46def374bd035cef4f378c71f5d28841fda0e53f1354fb4e2030edd6c98a4d | 0x7e2b238c6089550f3b77e01cf5607bb24aac05c390db828737fc5d569c0075fd5023 | 0x46d1d421d16d2be83bf9b2f762cb003d5702790bf6191e33a10ffdff8fcfd42f41cd | 0xfa128f7e96b00c69c1993f3a2e09f4ca3c5f2baed3757fb8f9d3d9b27845bfed8bd2
 0x3838304f32504b4b3131 | 0x7ccb1a9eed0675b7f9ae203fd9dc57c532ff6851b4d5becbca4ea94975a6115fe58e | 0x3fdd1a44b89787fed88133035c22db73a490c31edf7aa8d62c1585300c2ede3aaaec | 0x3975e72c775325d2dadd0f7ae01b70ceda97f796fa192db4d7d4cf199f4fb0f192ff | 0xc3aa4d432d56390642d1ca6d62aceb532fe23fc07993c1ca7c1ad39c4270cbfccd31 | 0x6d1bc070b0409f168825f0e7fb67a11b6b14d8423d1b8beb5a01ac1f8487d95d15b1

```

Next flush the mem tables to disk, stop cassandra and unmount the ebs volume for each node
```
nodetool flush
sudo pkill cassandra
sudo umount /var/lib/cassandra

```
now create snapshots of the ebs volumes and record the snapshot ids.  Give this process a
few minutes and check in the ec2 console to make sure the snapshots have been created

```
$ terraform show

Outputs:

cassandra_0 = 54.191.125.169
cassandra_0_vol_id = vol-0d2e6e6516fe87156
cassandra_1 = 54.201.172.131
cassandra_1_vol_id = vol-06625bd0646d6f237
cassandra_2 = 54.201.200.121
cassandra_2_vol_id = vol-0bbfa69dbf0fe7ed5
daniel@dirac:~/Sources/cassandra-terraform$ aws ec2 create-snapshot --volume-id vol-0d2e6e6516fe87156{
    "Description": "", 
    "Encrypted": false, 
    "VolumeId": "vol-0d2e6e6516fe87156", 
    "State": "pending", 
    "VolumeSize": 500, 
    "Progress": "", 
    "StartTime": "2017-02-25T21:45:35.000Z", 
    "SnapshotId": "snap-0299ea162fd4d14c7", 
    "OwnerId": "578367184912"
}
daniel@dirac:~/Sources/cassandra-terraform$ aws ec2 create-snapshot --volume-id vol-06625bd0646d6f237{
    "Description": "", 
    "Encrypted": false, 
    "VolumeId": "vol-06625bd0646d6f237", 
    "State": "pending", 
    "VolumeSize": 500, 
    "Progress": "", 
    "StartTime": "2017-02-25T21:46:00.000Z", 
    "SnapshotId": "snap-0fdd1bd9b12b6fe51", 
    "OwnerId": "578367184912"
}
daniel@dirac:~/Sources/cassandra-terraform$ aws ec2 create-snapshot --volume-id vol-0bbfa69dbf0fe7ed5{
    "Description": "", 
    "Encrypted": false, 
    "VolumeId": "vol-0bbfa69dbf0fe7ed5", 
    "State": "pending", 
    "VolumeSize": 500, 
    "Progress": "", 
    "StartTime": "2017-02-25T21:46:18.000Z", 
    "SnapshotId": "snap-0774a8e08c0b6f205", 
    "OwnerId": "578367184912"
}

```

Now run ```terraform destroy```

To restore the cluster from our ebs snapshots, uncomment the snapshot_id fields in the ebs volume resource blocks in cassandra.tf
Populate the snapshot_id fields with the snapshot_ids recorded before you brought
down the cluster.  If you forgot just check for the snapshot ids in the ec2 console.
Now run ```terraform plan``` followed by ```terraform apply``` to create a new cluster
based off the previous ebs snapshots.

To install cassandra do this on each node (Note we are using restore_from_snapshot.sh rather than setup_cassandra.sh)
 ```
  ssh -i <path2key>.pem ubuntu@<cassandra_0_ip>
  bash /tmp/provisioning/restore_from_snapshot.sh 0

  ssh -i <path2key>.pem ubuntu@<cassandra_1_ip>
  bash /tmp/provisioning/restore_from_snapshot.sh 1

  ssh -i <path2key>.pem ubuntu@<cassandra_2_ip>
  bash /tmp/provisioning/restore_from_snapshot.sh 2
  ```
You are using resources which is costing you money.  Lets tear it down.
As in the previous step ssh into each node and run the following to stop
cassandra and unmount the data drives.

  ```
  sudo service cassandra stop
  sudo umount /var/lib/cassandra
  ```
Finish the job with ```terraform destroy```
