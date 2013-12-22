taskmaster
==========


Run the server
--------------
    cd taskmaster/
    cp taskmaster/settings.sample.py taskmaster/settings.py
    ./bootstrap.sh
    venv/bin/python runserver.py


Setup redis
-----------
Follow instructions at http://redis.io/topics/quickstart OR

    git clone https://github.com/jpmunz/quickstart.git quickstart
    cd quickstart/redis/
    sudo ./start.sh 6379
    hit 127.0.0.1:5000/test_db/

Mac OS X Setup
---
Download the reddis package from reddis.io
   
   unzip the tar.gz
   Follow instructions here http://jasdeep.ca/2012/05/installing-redis-on-mac-os-x/
   Profit

