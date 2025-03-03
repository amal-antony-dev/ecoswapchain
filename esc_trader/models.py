from django.db import models


class Trader(models.Model):
    eco_user = models.OneToOneField("esc_user.EcoUser", on_delete=models.CASCADE, related_name="eco_trader")
    wallet = models.OneToOneField("esc_wallet.Wallet", verbose_name=("Main Wallet"), on_delete=models.CASCADE, null=True)
    total_sales = models.IntegerField(default=0)
    total_purchases = models.IntegerField(default=0)
    date_joined = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

