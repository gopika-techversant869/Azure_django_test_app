from django.db import models

# Create your models here.
# models.py

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
