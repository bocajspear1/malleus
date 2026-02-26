from django.db import models

class PortAllocation(models.Model):
    username = models.TextField(max_length=200)
    port = models.IntegerField(unique=True)
    
