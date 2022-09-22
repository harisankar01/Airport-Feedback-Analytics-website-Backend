from django.db import models


class Airport_feedbacks(models.Model):
    airport_name = models.CharField(max_length=500)
    link = models.CharField(max_length=500)
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=500)
    author_country = models.CharField(max_length=5000)
    date = models.DateTimeField()
    content = models.CharField(max_length=10000)
    overall_rating = models.CharField(max_length=500)
    queuing_rating = models.CharField(max_length=500)
    terminal_cleanliness_rating = models.CharField(max_length=500)
    airport_shopping_rating = models.CharField(max_length=500)
    recommended = models.IntegerField()
