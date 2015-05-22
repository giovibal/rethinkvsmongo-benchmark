#! /home/martin/.virtualenvs/rethinkmongo/bin/python
import rethinkdb as r
from pymongo import MongoClient
from pymongo import DESCENDING, ASCENDING
import random
import time

import calendar
from datetime import datetime

def unix_utc_now():
	d = datetime.utcnow()
	_unix = calendar.timegm(d.utctimetuple())

	return _unix

database_name = 'rethinkvsmongo'
table_name = 'metrics'


mongo_connection = MongoClient(host='mongodb://localhost')
mongo_db = mongo_connection[database_name]
mongo_collection = mongo_db[table_name]
mongo_collection.ensure_index([('last_update', DESCENDING)], background=True)

r.connect("localhost", 28015, db=database_name).repl()
# r.db_create(database).run()
# r.db(database_name).table_create("metrics").run()
# r.table(table_name).index_create('last_update').run()

now = unix_utc_now()
metrics_document = {
	"table_name" : "django_session",
	"cumulative_pct_reads" : 69.8599999999999994,
	"cache_hit_rate" : 90.2000000000000028,
	"last_update" : '',
	"reads" : 51,
	"index_hit_rate" : 37.5000000000000000,
	"size" : 1
}





def insert_benchmark_mongodb():
	for i in range(0, 100000):
		try:
			del metrics_document['_id']
		except:
			pass
		metrics_document['last_update'] = now+i
		mongo_collection.insert(metrics_document)

def insert_benchmark_rethink():
	for i in range(0, 100000):
		metrics_document['last_update'] = now+i
		r.table(table_name).insert(metrics_document, durability='hard').run()

def update_benchmark_mongodb():
	# Last document timestamp
	# timestamp =  mongo_collection.find_one(sort=[ ("last_update", DESCENDING) ]) #1432382558
	#
	# last_update = timestamp['last_update']
	# last_twenty_thousand = last_update-20000 # result - 1432362558
	# print last_twenty_thousand
	random_timestamp = random.randrange(1432282559, 1432382558, 1)
	data = {'size': 145, 'reads': 12, 'cache_hit_rate': 100}
	for i in range(0, 100000):
		mongo_collection.update({"last_update": {"$in": [random_timestamp]}}, {"$set": data})

def update_benchmark_rethinkdb():
	rethink_cursor = r.table(table_name).order_by(index=r.desc('last_update')).limit(1).run()

	for result in rethink_cursor:
		print result['last_update']

# Benchmark
start = time.time()
update_benchmark_rethinkdb()
end = time.time()
print end - start
