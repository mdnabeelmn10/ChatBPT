from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    TIER_CHOICES = (('FREE', 'Free'), ('PAID', 'Paid'))
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='FREE')
