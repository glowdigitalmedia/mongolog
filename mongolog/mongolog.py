"""
MongoLog 
Written by Harel Malka in 2010 as part of the Glow Machine (www.theglowmachine.com). 
Adapted to generic use 2013 with permission.
harel@harelmalka.com / harel@thisisglow.com

MongoLog is a drop in replacement to a standard logging module where all log messages 
are kept in a mongodb collection. This allows many hosts to log into the same centralised location without messing about with file names. 
The writes are not 'safe'  by default to allow speedy log writes but setting SAFETY_LEVEL to the number of replica set members required for a safe save will ensure all saves are safe. 
Default log level is DEBUG, which can be easily set to INFO/WARNING/ERROR from the settings block at the top of the page. 
To log regardless of log level settings, use the 'any' method.
Connections ot mongo are attempted first on a replica set client and fail to a single instance conncetion if no replica set is available. 
The connection is closed on the destruction of this object.

Usage: 

from mongolog import MongoLog
LOG = MongoLog(logger="mylogger")
LOG.info("This is my informative message", mydetail="Some custom detail", anotherparam="another irrelevant informative parameter")
LOG.error("This is an error message", stack="Dump of stack trace")

"""

from pymongo import MongoClient, MongoReplicaSetClient, ASCENDING, DESCENDING
from pymongo.read_preferences import ReadPreference
import socket
import datetime

MONGO_DB_NAME = 'log'
MONGO_HOST_NAME = 'mongodb://localhost:27017'
HOSTNAME = socket.gethostbyaddr(socket.gethostname())[0]
SYSTEM_LOG_LEVEL = 'DEBUG'
LOG_COLLECTION_NAME = 'system_log'
MONGO_POOL_SIZE = 30
MONGO_REPLICA_SET_NAME = 'rs0'
SAFETY_LEVEL = 0 # Set to how many members of replica set to write for a safe save. 

class MongoLog(object):
	try:
		connection = MongoReplicaSetClient(MONGO_HOST_NAME, max_pool_size=MONGO_POOL_SIZE, replicaSet=MONGO_REPLICA_SET_NAME, read_preference = ReadPreference.PRIMARY_PREFERRED)
	except Exception as e:  
		connection = MongoClient(host=MONGO_HOST_NAME, max_pool_size=MONGO_POOL_SIZE) 
	collection_name = LOG_COLLECTION_NAME
	db = connection[MONGO_DB_NAME]
	logger = 'syslog' # default logger
	hostname = HOSTNAME
	log_level_map = {
		'DEBUG': 0,
		'INFO': 1,
		'WARNING': 2,
		'ERROR': 3
	}
	min_level = log_level_map[SYSTEM_LOG_LEVEL]
	
	def __init__(self, logger=None, *args, **kwargs):
		if logger:
			self.logger = logger 
		self.col = self.db[self.collection_name]
		self.col.ensure_index([('timestamp', DESCENDING)])
		self.col.ensure_index([('logger', ASCENDING)])
		self.col.ensure_index([('level', ASCENDING)])
		
	def __del__(self):
		self.connection.close()

	def log(self, level=None, detail="", **kwargs):
		doc = {
			'logger': self.logger,
			'host': self.hostname,
			'level':level,
			'timestamp': datetime.datetime.utcnow(),
			'detail': detail
		} 
		doc.update(kwargs)
		_kw = { 'w': SAFETY_LEVEL } if SAFETY_LEVEL>0 else {}
		return self.col.insert(doc, **_kw)
	
	def in_level(self, level):
		return  self.min_level<=self.log_level_map[level]
			
	def any(self, detail, **kwargs):
		"""
		Force logging regardless of loggine level 
		"""
		return self.log(level='INFO', detail=detail, **kwargs)
	
	def debug(self, detail, **kwargs):
		"""
		Log if in debug level
		""" 
		if self.in_level('DEBUG'): 
			return self.log(level='DEBUG', detail=detail, **kwargs)
		
	def info(self, detail, **kwargs):
		"""
		Log if in info level
		""" 
		if self.in_level('INFO'): 
			return self.log(level='INFO', detail=detail,  **kwargs)
	
	def warning(self, detail, **kwargs):
		"""
		Log if in warning level
		""" 
		if self.in_level('WARNING'): 
			return self.log(level='WARNING', detail=detail, **kwargs)
	
	def error(self, detail, **kwargs):
		"""
		Log if in error level
		""" 
		if self.in_level('ERROR'): 
			return self.log(level='ERROR', detail=detail, **kwargs)

	def get_by_hostname(self, hostname): 
		return self.col.find(hostname=hostname)
	
