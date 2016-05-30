from cassandra.cluster import Cluster
from cassandra.policies import RetryPolicy
import sys
import argparse
import datetime
from itertools import cycle, product
import csv
import time

class AlwaysRetryPolicy(RetryPolicy):
    """
    A retry policy that never retries and always propagates failures to
    the application.
    """

    def on_read_timeout(self, *args, **kwargs):
        return (self.RETRY, None)

    def on_write_timeout(self, *args, **kwargs):
        return (self.RETRY, None)

    def on_unavailable(self, *args, **kwargs):
        return (self.RETRY, None)


def create_schema(arguments):
    session = Cluster([arguments.host]).connect()
    session.execute("USE %s;" % arguments.keyspace)

    query = '''CREATE COLUMNFAMILY {columnfamily} ( 
               key text PRIMARY KEY,
               color text,
               size text,
               qty int)'''.format(columnfamily=arguments.columnfamily)

    session.execute( query )
    

 # create and insert the data
def insert_data(arguments, rw):
    
    cluster = Cluster([arguments.host])
    cluster.default_retry_policy = AlwaysRetryPolicy()
    session = cluster.connect()
    session.execute("USE %s;" % arguments.keyspace)
    
    color_list=['red', 'green', 'blue', 'yellow', 'purple', 'pink', 'grey', 'black', 'white', 'brown']
    size_list=['P', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']
    qty_list=xrange(500)
    elements = cycle(product(color_list,size_list,qty_list))

    row_count = arguments.start_key
    while True:
        if row_count >= arguments.num_keys:
                break
        row_count += 1


        color, size, qty = elements.next()
        key = "key_%d" % row_count

        query = '''INSERT INTO {columnfamily} (
                   key,
                   color,
                   size,
                   qty)
                   VALUES (%s,%s,%s,%s)'''.format(columnfamily=arguments.columnfamily)
        params = [
        key,
        color,
        size,
        qty,
        ]

        error = None
        latency = 0.0
        try:
            start_time = time.time()
            session.execute( query, params )
        except Exception as e:
            error = str( e )
            print error
        finally:
            latency = time.time() - start_time
            rw.writerow( ['insert', key, latency, str(error)] )


parser = argparse.ArgumentParser(description="Create some data")
parser.add_argument('-l', '--host', type=str, help='host to connect to', default='localhost')
parser.add_argument('-p', '--port', type=int, help='host port to connect to', default=9160)
parser.add_argument('-r', '--num_keys', type=int, help='The total number of rows inserted', default=100000)
parser.add_argument('-k', '--keyspace', type=str, help='Name of keyspace.  Will be dropped if it already exists.', default='ks')
parser.add_argument('-c', '--columnfamily', type=str, help='name of the columnfamily.', default='cf')
parser.add_argument('-s', '--start_key', type=str , help='Start with key num', default=0)
parser.add_argument('-e', '--num_columns', type=int, help='The number of extra columns created', default=3)


arguments = parser.parse_args()

if arguments.num_columns < 1:
    arguments.num_columns = 1

if arguments.num_keys < 1:
    arguments.num_keys = 1

if arguments.start_key < 1:
    arguments.start_key = 1

 # Create keyspace.  Delete old one if it exists.
session = Cluster([arguments.host]).connect()
session.execute("USE system")

if [ k.keyspace_name == arguments.keyspace for k in session.execute("select * from system_schema.keyspaces") ]:
    session.execute("DROP KEYSPACE %s" % arguments.keyspace)

session.execute("CREATE KEYSPACE %s WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 2}" % arguments.keyspace)
session.execute('USE %s' % arguments.keyspace)

with open('perf.csv', 'w') as results_file:
    results_writer = csv.writer( results_file, delimiter=',')

    results_writer.writerow( ['operation', 'key', 'latency', 'error'] )

    create_schema( arguments )

    insert_data( arguments, results_writer )
    
