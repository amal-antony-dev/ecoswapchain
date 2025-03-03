from django.db import models

# Create your models here.

class EscToken(models.Model):
    user = models.ForeignKey("esc_trader.Trader", on_delete=models.CASCADE, related_name='carbon_credits')
    credits = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.user.username} - {self.credits} credits"
