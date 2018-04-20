# CLASS-BLAST

**Class-Blast** created to parse data from one service and bring it to another.


## Features
- Celery tasks supported
- Payment account system
- Account credentials system
- Mapper model

**Class-Blast** automatically authorized at services and remembers selected fields, that simplifies the work with the subsequent import selection

## Project apps

- auth_core
- base
- core
- scraper

## Installation

Install the dependencies from **requirements.txt** and start the server.

    $ source venv/bin/activate
    $ python src/manage.py migrate
    $ python src/manage.py runserver

### Launch Celery 

    $ cd src/apps/
    $ celery worker -A core --loglevel=DEBUG

### Install RabbitMQ

Mac OS:

    brew install rabbitmq

Linux:

    sudo apt-get install rabbitmq-server

### Installing chrome driver

    mkdir -p $HOME/bin chmod +x chromedriver mv src/drivers/chromedriver $HOME/bin
    additional: echo "export PATH=$PATH:$HOME/bin" >> $HOME/.bash_profile

Mac OS: 

    export PATH=$PATH:/{folder with driver}/

### Install PhantomJS:

    export PHANTOM_JS="phantomjs-2.1.1-linux-x86_64" wget https://bitbucket.org/ariya/phantomjs/downloads/$PHANTOM_JS.tar.bz2 sudo tar xvjf $PHANTOM_JS.tar.bz2 sudo mv 
    $PHANTOM_JS /usr/local/share sudo ln -sf /usr/local/share/$PHANTOM_JS/bin/phantomjs /usr/local/bin


