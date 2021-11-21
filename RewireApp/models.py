"""
models.py
""" 
from django.db import models
from django.contrib.auth.models import User


class Flow(models.Model):
    startingUser = models.CharField(max_length=50)
    targettingUser = models.CharField(max_length=50)
    focusStartTime = models.DateTimeField(auto_now_add=True)
    focusEndTime = models.DateTimeField(auto_now_add=True)
    #figure out what else to add 




