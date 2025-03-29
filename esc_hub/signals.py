from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Hub

@receiver(post_save, sender=Hub)
def update_routes_on_new_hub(sender, instance, created, **kwargs):
    if created:
        from .utils import build_mst  # ✅ Import inside function
        build_mst()


