# Amalgam
Amalgam is collection of (mainly) [Python](https://python.org) scripts with a web interface (based on [Flask](https://flask.palletsprojects.com)) you can use in SEO.

More info for developers : [Dev page](./dev.md)

# Project structure #
* How to run it ( [Windows 10](#how-to-run-it-windows-10) )
* How to run it ( [XUbuntu 20](#how-to-run-it-ubuntu-20) )
* Scripts ( [Scripts](#scripts) )
	* Run crawler against a site ( [Crawler](#Crawler) ) 

## How to run it (Windows 10)

### Step 1:  Have Python3 installed

Check if you have Python installed. Open a Command Prompt (Start > Command Prompt) and type:

	python --version 

If not then download it and install it from:
[https://www.python.org/](https://www.python.org/)

### Step 2: Have Pip3 installed. Usually Python3 comes with PIP3 by default but you can check (in Command Prompt) with:

	pip3 --version


### Step 3: Install Python libraries		
First go inside the folder of the project and open a Command Prompt and then type:

	pip install -r requirements.txt


### Step 4: Launch app
From a Command Prompt inside the project folder type:
	python app.py


### Step 5: See in browser
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

To run it go inside [lab]/crawler/requests

	cd ./lab/crawler/requests

and run

	python crawler --domain <name_of_domain>

The collected data wil be available inside:

	crawl-requests-report.log

file.