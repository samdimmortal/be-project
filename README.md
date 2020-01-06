## Linux

`pip install virtualenv`

## Go to project folder and run:  
~~~
virtualenv env --python=python  
. env/bin/activate  
sudo apt-get install python-dev
sudo apt-get install libxml2-dev libxslt-dev libjpeg-dev zlib1g-dev libpng12-dev
pip install -r requirements.txt  
sudo pip uninstall Pillow
sudo pip install Pillow
python manage.py migrate  
~~~
# Run project
~~~
python manage.py runserver
~~~
#### Get results without running the project [Hook while algo is being improved] ####
#### *feed.py* contains an array of search queries, you want to fill up db with. EDIT it, if required. ####
`python feed.py`

## Run algo [is running outside the project]  
`python algo.py 0.5`  
`python algo.py 0.1`  
`python algo.py 1.0`  

Float value is results to show when similarity is above this value else default is 0.1 when no float value entered.


# README #

This README would normally document whatever steps are necessary to get your application up and running.

### How do I get set up? ###

* Summary of set up
* Configuration
* Dependencies
* Database configuration
* Deployment instructions

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin