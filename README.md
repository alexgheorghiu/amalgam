# Amalgam
Amalgam is collection of (mainly) [Python](https://python.org) scripts with a web interface (based on [Flask](https://flask.palletsprojects.com)) you can use in SEO.

More info for developers : [Dev page](./dev.md)

# Project structure #
* How to run it ( [Docker](#how-to-run-it-docker) )
* How to run it ( [Windows 10](#how-to-run-it-windows-10) )
* How to run it ( [XUbuntu 20](#how-to-run-it-ubuntu-20) )
* Scripts ( [Scripts](#scripts) )
	* Run crawler against a site ( [Crawler](#Crawler) ) 

## How to run it (Docker)

### Step 1: Install Docker

Go on [Docker's download page](https://docs.docker.com/desktop/#download-and-install) and install Docker

### Step 2: Run the app

```sh
docker run -it -p 5000:5000 scriptoid/amalgam:0.1
```
**Note 1** : Port 5000 of your PC should be available

**Note 2** : If you want to run it on a different port use the following command:

```sh
docker run -it -p <Your Port>:5000 scriptoid/amalgam:0.1
```

replacing 'Your Port' with a free port at your desire.

### Step 3: Use the application

Just open a browser and access [http://localhost:5000](http://localhost:5000)

### Step 4: Stop the application

Simply go to console application launched by Docker and press Ctrl-C.


## How to run it (Windows 10)

### Step 1: Download the app

Download the [amalgam](https://github.com/alexgheorghiu/amalgam/archive/main.zip) zip file and unzip it into a folder.

### Step 2:  Have Python3 installed

Check if you have Python installed. Open a Command Prompt (Start > Command Prompt) and type:

	python --version 

You should get something like

![Windows Console](./windows-install-python.png)

If not then download it and install it from:
[https://www.python.org/](https://www.python.org/)

**Note**: 
Remember to check "Add Python 3.x to PATH" during installation so you can access Python from Command Prompt

### Step 3: Have Pip3 installed. Usually Python3 comes with PIP3 by default but you can check (in Command Prompt) with:

	pip3 --version


### Step 4: Install Python libraries		
First go inside the folder of the project and open a Command Prompt and then type:

	pip install -r requirements.txt


### Step 5: Launch app
From a Command Prompt inside the project folder type:
	python app.py


### Step 6: See in browser
Access it at:  http://127.0.0.1:5000/ with any browser.


## How to run it (Ubuntu 20)

### Step 1:  Have Python3 installed

Check if you have Python installed

	python --version 

If not then run:

    sudo apt-get install python3

### Step 2: Have Pip3 installed. Usually Python3 comes with PIP3 by default but you can check with:

	pip3 --version


### Step 3: Install Python libraries		
	sudo pip install -r requirements.txt


### Step 4: Launch app
	python app.py


### Step 5: See in browser
Access it at:  http://127.0.0.1:5000/

# Scripts 

Scripts are small programs that are part of Amalgam but do not require to run the whole Amalgam application. 

They are isolated enough (from main application) to be able to run them independently.

## Crawler
The Crawler script is the part of Amalgam that is crawling the pages of a site and collects informations.

**Note** : In order to run it you should have complete the step _"Install Python libraries"_ - for you operating system -  inside the above tutorial.

To run it go inside [lab]/crawler/requests

	cd ./lab/crawler/requests

and run

	python crawler.py --domain=<name_of_domain> --max-links=<maximum number of links>

The collected data wil be available inside:

	crawl-requests-report.log

file.