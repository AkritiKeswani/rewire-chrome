"""
models.py
""" 
from django.db import models
from django.contrib.auth.models import User


class Flow(models.Model):
    startingUser =  models.ForeignKey(Participant, on_delete=models.CASCADE)
    targettingUser =  models.ForeignKey(Participant, on_delete=models.CASCADE)
    focusStartTime = models.DateTimeField(auto_now_add=True)
    focusEndTime = models.DateTimeField(auto_now_add=True)





