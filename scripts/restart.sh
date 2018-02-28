#!/bin/bash

sudo supervisorctl restart class-blast_uwsgi
sudo supervisorctl restart class-blast-celery