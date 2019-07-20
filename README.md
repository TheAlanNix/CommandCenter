# Cisco Command Center

Cisco Command Center is a project to collect and correlate event data across multiple Cisco Security (and possibly third-party) products, and display that data in an easy to understand interface.  The end goal is to allow Security Analysts to easily identify attacks and the offending hosts, and perform remediations against those attacks - all from a single web application.

## Requirements

* Must have Docker installed

## Installation

Cisco Command Center uses a Python Flask backend web server, a MongoDB database, and a Vue javascript framework front-end.

First, make a copy of *.example.env* file as *.env*.  From the project root directory:

>```cp .example.env .env```

You'll then need to enter the MongoDB database credentials you'd like to use, and product API credentials, into the *.env* file.

By default, Command Center will deploy a MongoDB container, but if you'd like to use an external MongoDB, you certainly can.

Once the *.env* file configuration is complete, you can simply run the following command from the root project directory to start all of the Docker containers:

>```docker-compose up```

This will download/compile all of the containers, and start them.  By default, this will run the containers in the foreground.  I recommend doing this at least once to make sure everything starts appropriately.  Once you've verified the *.env* is correct, you can run the following to daemon-ize the containers:

>```docker-compose up -d```

At this point your Command Center instance should be up and running.