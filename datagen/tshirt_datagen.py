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
    
    extra_columns = ','.join( ['col'+str(i)+' text' for i in range(arguments.num_columns)] )

    query = '''CREATE COLUMNFAMILY {columnfamily} ( 
               key text PRIMARY KEY,
               color text,
               size text,
               qty int,
               data_blob blob,
               {extra_columns})'''.format(columnfamily=arguments.columnfamily, extra_columns=extra_columns)

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
        data_blob = str(color)+str(size)+str(qty)
        key = "key_%d" % row_count

        extra_columns = ','.join( [' col'+str(i) for i in range(arguments.num_columns)] )
        extra_formaters = ",%s"*arguments.num_columns

        query = '''INSERT INTO {columnfamily} (
                   key,
                   color,
                   size,
                   qty,
                   data_blob,
                   {extra_columns} )
                   VALUES (%s,%s,%s,%s,%s{extra_formaters})'''.format(columnfamily=arguments.columnfamily,
                                                                         extra_columns=extra_columns,
                                                                         extra_formaters=extra_formaters)
        params = [
        key,
        color,
        size,
        qty,
        buffer(data_blob.encode('hex')),
        ] + ['val'+str(i) for i in range( arguments.num_columns) ]

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

def validate_data(arguments, rw):
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
        data_blob = str(color)+str(size)+str(qty)
        key = "key_%d" % row_count
        extra_columns = ','.join( [' col'+str(i) for i in range(arguments.num_columns)] )
        extra_column_vals = ['val'+str(i) for i in range( arguments.num_columns) ]

        query = "select * from {columnfamily} where key='{key}'".format(columnfamily=arguments.columnfamily,
                                                                           key=key)
        error = None
        latency = 0.0
        row = None
        try:
            start_time = time.time()
            row = session.execute( query )[0]
        except Exception as e:
            error = str( e )
            print error
        finally:
            latency = time.time() - start_time
            rw.writerow( ['read', key, latency, str(error)] )

        assert row.key == key, "Can't find %s in row.key." % key
        assert row.color == color, "Can't find %s in row.color." % color
        assert row.qty == qty, "Can't find %s in row.qty." % str(qty)
        assert row.size == size, "Can't find %s in row.size." % str(size)
        assert row.data_blob == data_blob.encode('hex'), "Can't find %s in row.data_blob" % str(row.data_blob)
        for i, col in enumerate(extra_column_vals):
            assert col in row, "Missing extra column %s in row." % col

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

if arguments.keyspace in [ k.keyspace_name for k in session.execute("select * from schema_keyspaces") ]:
    session.execute("DROP KEYSPACE %s" % arguments.keyspace)

session.execute("CREATE KEYSPACE %s WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}" % arguments.keyspace)
session.execute('USE %s' % arguments.keyspace)

with open('perf.csv', 'w') as results_file:
    results_writer = csv.writer( results_file, delimiter=',')

    results_writer.writerow( ['operation', 'key', 'latency', 'error'] )

    create_schema( arguments )

    insert_data( arguments, results_writer )

    validate_data( arguments, results_writer )
