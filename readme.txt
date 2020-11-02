
Project structure
How to run it (XUbuntu 20)
How to run it (Windows 10)


Project structure
=================
[lab] - only used by developers to test new ideas
[pieces] - folder with other folders and sub-projects
[static] - static files: css
[templates] - Jinja pages
[test] - folder with tests
app.py - the actual starting point of the application
readme.txt - this file
requirements.txt - the Python dependencies for the project (used by pip3)




How to run it (XUbuntu 20)
=========================

Fix broken installs
	sudo apt-get --fix-broken install

Install pip3
	apt install python3-pip
	
Install virtualenv
	pip3 install virtualenv

See that the virtualenv is in the path. 
	The executable are usually stored inside (/home/alex/.local/bin).
	So you need to check if .profile contains
		# set PATH so it includes user's private bin if it exists
		if [ -d "$HOME/.local/bin" ] ; then
			PATH="$HOME/.local/bin:$PATH"
		fi
	and if it does either logout / login or run
		source .profile

Install virtualenvwrapper	
	pip3 install virtualenvwrapper
	
Create folder to keep your virtual enviroments
	mkdir ~/.virtualenvs
	
Edit ~/.bashrc and add
	# Things for virtualenvwrapper
	export WORKON_HOME=$HOME/.virtualenvs
	VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
	. /"$HOME"/.local/bin/virtualenvwrapper.sh
	
Load .bashrc
	source ~/.bashrc

Setup virtual env	
	virtualenv env
	
Make a virtual enviroment
	mkvirtualenv amalgam

Activate enviroment
	workon amalgam
		
For visualization install GraphViz
	sudo apt install graphviz

Install Python libraries
	pip3 install -r requirements.txt
	
	See https://github.com/realpython/discover-flask/blob/master/requirements.txt


Run Flask	
	python app.py


Visual Studion Code
	* Load workspace
	* Ctrl-Shift-P to select the Python interpreter (and pick amalgam). More: https://code.visualstudio.com/docs/python/environments
	



How to run it (Windows 10)
==========================

Install pip
	???
	
Install virtualenv
	pip install virtualenv

Setup virtual env	
	virtualenv env
	
Activate virtualenv
	Windows:
		.\env\Scripts\activate.bat
		
	Linux
		source ./env/bin/activate.sh
		

Install Python libraries
	pip install -r requirements.txt
	
	See https://github.com/realpython/discover-flask/blob/master/requirements.txt


Run Flask	
	python app.py