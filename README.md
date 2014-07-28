Server
==========

Environment
------------
It's usually good to keep each python project in a seperate environment, to better manage dependencies and the like. 
virtualenv and virtualenvwrapper are great tools for this (both of which are avaialbe through pip). 

I recommend reading the docs for each at:
- virtualenv.readthedocs.org
- virtualenvwrapper.readthedocs.org

and putting this block into your bash config file

```
export WORKON_HOME = ~/Envs
mkdir -p $WORKON_HOME
source /usr/local/bin/virtualenvwrapper.sh
```

Then just run mkvirtualenv "name" and follow the directions in the requirements file to get everything you need for the project and an isolated environment. 
