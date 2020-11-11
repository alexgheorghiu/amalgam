# amalgam

These are the instructions for developer

# Project structure #
* How to run it ( [XUbuntu 20](#how-to-run-it-xubuntu-20) )
* How to run it ( [Windows 10](#how-to-run-it-windows-10) )


## Project structure ##

* [lab] - only used by developers to test new ideas
* [pieces] - folder with other folders and sub-projects
* [static] - static files: css
* [templates] - Jinja pages
* [test] - folder with tests
* app.py - the actual starting point of the application
* README.md - this file
* requirements.txt - the Python dependencies for the project (used by pip3)




## How to run it ([X]Ubuntu 20) ##

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

Run Flask	

```sh
	python app.py
```

See in browser

Access it at:  http://127.0.0.1:5000/


Visual Studion Code

	* Load workspace
	* Ctrl-Shift-P to select the Python interpreter (and pick amalgam). More: https://code.visualstudio.com/docs/python/environments
	



## How to run it (Windows 10) ##