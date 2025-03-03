from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Wallet(models.Model):
    public_key = models.CharField(max_length=200, unique=True, db_index=True)
    private_key = models.CharField(max_length=600, unique=True, db_index=True)
    balance = models.DecimalField(max_digits=10, decimal_places=5, default=0.0)
    key = models.CharField(max_length=255, db_index=True)  # Stores a hashed key

    def __str__(self):
        return self.public_key

    def set_key(self, raw_key):
        """Hashes and stores the encryption key securely"""
        self.key = make_password(raw_key)
        self.save()

    def check_key(self, raw_key):
        """Checks if the provided key matches the stored hashed key"""
        return check_password(raw_key, self.key)
