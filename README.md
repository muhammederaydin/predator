###PREDATOR###

Real-Time User Tracking Engine for User Journey in Web Sites

Predator uses Apache Kafka for getting data, also for real time tracking 
uses Redis. Created paths are stored in Redis. For every user, predator create 
a list and store them paths in Redis. If predator detect any user which pattern
same as created paths, then send user informations to kafka topics. 
Predator can't execute any action, only detect actions.


Predator Requirements:
  - Python3.6.x
  - Redis 5.0 (Stable Version)
  - Apache Kafka 2.4.0 (Stable Version)
  - MongoDB 3.6 or latest stable version


Python Requirements
  - In the main folder:
        pip install -r requirements.txt


You should create security config file. 
  - First you need to change parameters in Config/local.conf.plain.
  - In the main folder execute this command:
        python manage.py -c
  - If command works correct then .sconf file should be created. 


Start predator.py for start the application


Creating Paths:
  - You must use redis RPUSH method
  - Append paths sequentially
  - If you are creating utm tracker you must use <utm_tracker_> for your key
    For Example:
      RPUSH utm_tracker_mydummy_paths /
  - If you are creating tracker without utm tag you must use <tracker_> for
    your key.
    For Example:
      RPUSH tracker_mydummy_paths /blog
  - If you want take action for specific utm source use <*> for utm and use
  <__> for action name
    For Example : /blog*twitter__mail__
  - If you want take action for any utm source use default
    For Example : /blog*default__sms__

Add to Redis Example:
  - With UTM
    * RPUSH utm_tracker_mydummy_paths / 
    * RPUSH utm_tracker_mydummy_paths /blog 
    * RPUSH utm_tracker_mydummy_paths /about*facebook__sms__email 

  - Without UTM
    * RPUSH tracker_mydummy_paths / 
    * RPUSH tracker_mydummy_paths /blog 
    * RPUSH tracker_mydummy_paths /about__mail 

There will be add a module for action creation in next version...
