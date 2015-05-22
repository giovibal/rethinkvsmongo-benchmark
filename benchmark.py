#! /home/martin/.virtualenvs/rethinkmongo/bin/python
import rethinkdb as r
from pymongo import MongoClient
import pymongo
import random
import time

COLOR_GREEN = '\033[92m'
END_COLORED_LINE = '\033[0m'

database_name = 'rethinkvsmongo'
table_name = 'metrics'
unix_timestamp = 1432294074
total_operations = 100000

def random_timestamp():
	return random.randrange(unix_timestamp, unix_timestamp+100000, 1)

def random_int():
	return random.randint(100, 300)


def timing(f):
	def wrap(*args):
		time1 = time.time()
		ret = f(*args)
		time2 = time.time()
		total = (time2-time1)*1000.0

		message = "op:{0}/time:{1:.2f}ms".format(total_operations,
		total)

		print "{function} \n{color}{message}{end}".format(
			function=f.func_name,
			color=COLOR_GREEN,
		 	message=message,
			end=END_COLORED_LINE)
		return ret
	return wrap

mongo_connection = MongoClient(host='mongodb://localhost')
mongo_db = mongo_connection[database_name]
mongo_collection = mongo_db[table_name]
mongo_collection.ensure_index([('last_update', pymongo.DESCENDING)], background=True)

r.connect("localhost", 28015, db=database_name).repl()
# r.db_create(database).run()
# r.db(database_name).table_create("metrics").run()
# r.table(table_name).index_create('last_update').run()

metrics_document = {
	"table_name" : "django_session",
	"cumulative_pct_reads" : 69.8599999999999994,
	"cache_hit_rate" : 90.2000000000000028,
	"last_update" : '',
	"reads" : 51,
	"index_hit_rate" : 37.5000000000000000,
	"size" : 1
}

@timing
def find_benchmark_mongodb():
	for i in range(0, total_operations):
		mongo_collection.find({"last_update": {"$in": [random_timestamp()]}})

@timing
def find_benchmark_rethinkdb():
	for i in range(0, total_operations):
		r.table(table_name).filter({"last_update":random_timestamp()})
@timing
def insert_benchmark_mongodb():
	for i in range(0, total_operations):
		data = metrics_document.copy()
		data['last_update'] = unix_timestamp+i
		mongo_collection.insert(data)
@timing
def insert_benchmark_rethinkdb():
	for i in range(0, total_operations):
		metrics_document['last_update'] = unix_timestamp+i
		r.table(table_name).insert(metrics_document, durability='hard').run()
@timing
def update_benchmark_mongodb():
	data = {'size': random_int(), 'reads': random_int(), 'cache_hit_rate': random_int()}
	for i in range(0, total_operations):
		mongo_collection.update({"last_update": {"$in": [random_timestamp()]}}, {"$set": data})

@timing
def update_benchmark_rethinkdb():
	data = {'size': random_int(), 'reads': random_int(), 'cache_hit_rate': random_int()}

	for i in range(0, 10):
		print random_timestamp()
		r.table(table_name).filter({"last_update":random_timestamp()}).update(data,
		durability='soft').run()

# Benchmark
for i in range(0, 3):
	find_benchmark_mongodb()
	find_benchmark_rethinkdb()
