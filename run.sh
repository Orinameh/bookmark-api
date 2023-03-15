#!/bin/bash

gunicorn -w 4 'src.runner:application'