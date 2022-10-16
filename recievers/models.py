from django.db import models
from datetime import datetime


class Receiver(models.Model):
    """
    class for company which recieves the invoice
    """
    name = models.CharField(max_length=200)
    address = models.TextField()
    website = models.URLField(blank=True)
    created = models.DateTimeField(default=datetime.now)

    logo = models.ImageField(default='images/logo.png')

    def __str__(self):
        return str(self.name)
