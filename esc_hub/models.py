from django.db import models
from geopy.distance import geodesic

class Hub(models.Model):
    """Represents a shipping hub in the network."""
    manager = models.OneToOneField('esc_user.EcoUser', on_delete=models.CASCADE, null = True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    district = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    pincode = models.CharField(max_length=6, null=True)
    hub_type = models.CharField(
        max_length=10,
        choices=[("Primary", "Primary"), ("Secondary", "Secondary"), ("Tertiary", "Tertiary")]
    )

    def __str__(self):
        return f"{self.district} ({self.hub_type})"

class Route(models.Model):
    """Represents a route between two hubs."""
    source = models.ForeignKey('esc_hub.Hub', related_name="source_hub", on_delete=models.CASCADE)
    destination = models.ForeignKey('esc_hub.Hub', related_name="destination_hub", on_delete=models.CASCADE)
    distance = models.FloatField(null=True)  # Distance in km
    time = models.FloatField(null=True)  # Estimated time in hours
    cost = models.FloatField(null=True)  # Cost for shipping

    def save(self, *args, **kwargs):
        """Automatically calculate distance using geolocation."""
        if not self.distance:
            coords_1 = (self.source.latitude, self.source.longitude)
            coords_2 = (self.destination.latitude, self.destination.longitude)
            self.distance = geodesic(coords_1, coords_2).km  # Calculate distance
            self.time = self.distance / 50  # Assuming 50 km/h average speed
            self.cost = self.distance * 0.5  # Example: Cost per km
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.source} → {self.destination} ({self.distance:.2f} km)"

