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

```
from mongolog import MongoLog
LOG = MongoLog(logger="mylogger")
LOG.info("This is my informative message", mydetail="Some custom detail", anotherparam="another irrelevant informative parameter")
LOG.error("This is an error message", stack="Dump of stack trace")
```
