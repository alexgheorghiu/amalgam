# Amalgam

Note: These are the instructions for developer

Amalgam is collection of (mainly) [Python](https://python.org) scripts with a web interface (based on [Flask](https://flask.palletsprojects.com)) you can use in SEO.

# Table of content #
* [Project structure](#project-structure)
* [How to run only crawler](#how-to-run-only-crawler)  
* [How to play with database](#how-to-play-with-database)
* [How to run tests](#how-to-run-tests)
* [How to run it](#how-to-run-it)  
	* How to run it ( [XUbuntu 20](#how-to-run-it-xubuntu-20) )
	* How to run it ( [Windows 10](#how-to-run-it-windows-10) )


## Project structure ##

* [lab] - only used by developers to test new ideas
* [pieces] - folder with other folders and sub-projects
* [amalgam] - folder with sources
	* [crawler] - crawler
	* [models] - DB model  
	* [static] - static files: css, js, images  
	* [templates] - Jinja pages  
	* [tests] - tests
* [documentation] - folder with different documentation
	* [design] - things related to design
	* *.sql - SQLite SQL files 
	* amalgam_mysql.sql - SQL script to create an Amalgam DB
* app.py - the actual starting point of the application
* manage_db.py - manage current database (SQLite | MySQL )  
* DEV.md - this file
* requirements.txt - the Python dependencies for the project (used by pip3)


## How to run tests
```sh
python -m amalgam.tests.test_all
```


## How to run only crawler
While being inside the [amalgam] folder run:
```sh
python -m amalgam.crawler.crawler
```


## How to play with database
While being inside the [amalgam] folder run:
```sh
# Create tables inside DB 
python manage_db.py -a empty

# Create tables inside DB  and add some data
python manage_db.py -a mock
```


## How to run it ##


### How to run it - XUbuntu 20

Fix broken installs

```sh
sudo apt-get --fix-broken install
```

Install pip3

```sh
apt install python3-pip
```

Install virtualenv

```sh
pip3 install virtualenv
```

See that the virtualenv is in the path. 

The executable are usually stored inside (/home/alex/.local/bin).

So you need to check if .profile contains

```sh
# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi
```

and if it does either logout / login or run

```sh
source .profile
```

Install virtualenvwrapper	

```sh
	pip3 install virtualenvwrapper
``` 
	
Create folder to keep your virtual enviroments
```sh
	mkdir ~/.virtualenvs
```
	
Edit ~/.bashrc and add

```sh
	# Things for virtualenvwrapper
	export WORKON_HOME=$HOME/.virtualenvs
	VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
	. /"$HOME"/.local/bin/virtualenvwrapper.sh
```

Load .bashrc

```sh
	source ~/.bashrc
```

Setup virtual env	

```sh
	virtualenv env
```	

Make a virtual enviroment

```sh
	mkvirtualenv amalgam
```

Activate enviroment

```sh
	workon amalgam
```

For visualization install GraphViz

```sh
	sudo apt install graphviz
```

Install Python libraries

```sh
	pip3 install -r requirements.txt
	
	See https://github.com/realpython/discover-flask/blob/master/requirements.txt
```

__Note__: If you got an error like:
```
 " fatal error: libpq-fe.h: No such file or directory"
```

simply run:

```sh
sudo apt-get install libpq-dev
```

Run Flask	

```sh
	python app.py
```

See in browser

Access it at:  http://127.0.0.1:5000/


Visual Studion Code

	* Load workspace
	* Ctrl-Shift-P to select the Python interpreter (and pick amalgam). More: https://code.visualstudio.com/docs/python/environments
	



### How to run it (Windows 10) ##