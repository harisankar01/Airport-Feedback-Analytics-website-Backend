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
    terminal_cleanliness_rating = models.CharField(max_length=500, blank=True)
    terminal_seating_rating = models.CharField(max_length=500, blank=True)
    terminal_signs_rating = models.CharField(max_length=500, blank=True)
    food_beverages_rating = models.CharField(max_length=500, blank=True)
    airport_shopping_rating = models.CharField(max_length=500, blank=True)
    wifi_connectivity_rating = models.CharField(max_length=500, blank=True)
    airport_staff_rating = models.CharField(max_length=500, blank=True)
    recommended = models.IntegerField(blank=True, null=True)

