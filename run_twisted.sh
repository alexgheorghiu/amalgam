#!/usr/bin/env bash

export PYTHONPATH=$PYTHONPATH:.

# WSGI must point to the Flask object
twistd -n web --path=. --wsgi amalgam.app.app