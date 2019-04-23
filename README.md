# Cisco Command Center

Cisco Command Center is a project to collect and correlate event data across multiple Cisco Security (and possibly third-party) products, and display that data in an easy to understand interface.  The end goal is to allow Security Analysts to easily identify attacks and the offending hosts, and perform remediations against those attacks - all from a single web application.

## Installation

Cisco Command Center uses a Python Flask backend web server, a MongoDB database, and a Vue javascript framework front-end.

First, make a copy of *config.example.json* file as *config.json*.  From the project root directory:

>```cp config.example.json config.json```

You'll then need to enter your database and product API credentials into the *config.json* file.  Currently, Command Center requires all API keys to be entered - this will be addressed shortly.

You can leverage an existing MongoDB database, or if you're doing local development, you can use MongoDB within a container.  To spool up a container, you can run the following:

>### Download & Deploy MongoDB Container
>1. ```docker pull mongo```
>2. ```docker run --name YOURCONTAINERNAME --restart=always -d -p 27017:27017 mongo >ongod --auth```
>3. ```sudo docker exec -i -t YOURCONTAINERNAME bash```
>>### Add MongoDB Authentication
>>1. ```mongo```
>>2. ```use admin```
>>3. ```db.createUser({user:"USERNAME",pwd:"PASSWORD",roles:[{role:"root",db:"admin"}]})```
>>4. ```exit```
>8. ```exit```

Next, we'll pull in the front-end dependencies (via npm), and compile the production code.  From the project root directory:

>### Install Node Dependencies
>1. ```cd www```
>2. ```npm install```
>3. ```npm run build```

Finally, we'll grab our Python dependencies, and run the web server.  From the project root directory:

>### Install Python Dependencies
>1. ```python3 -m venv venv```
>2. ```source venv/bin/activate```
>3. ```pip install -r requirements.txt```
>4. ```python app.py```

At this point your Command Center instance should be up and running.