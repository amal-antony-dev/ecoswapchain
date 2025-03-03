from django.db import models
import random

# Create your models here.

class Otp(models.Model):
    code = models.IntegerField(null = True)
    email = models.EmailField(max_length=254, unique=True)

    def generate(self):
        otp = random.randint(10**(6 - 1), 10**6 - 1)
        self.code = otp
        

