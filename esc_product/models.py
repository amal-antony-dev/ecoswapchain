from django.db import models

# Create your models here.

class RootCategory(models.Model):
    name = models.CharField(max_length=255)
    
class MainCategory(models.Model):
    name = models.CharField(max_length=255)
    
class Materials(models.Model):
    MATERIAL_CHOICES = [
        ("wood", "Wood"),
        ("metal", "Metal"),
        ("plastic", "Plastic"),
        ("glass", "Glass"),
        ("paper", "Paper"),
        ("fabric", "Fabric"),
        ("ceramic", "Ceramic"),
        ("rubber", "Rubber"),
        ("leather", "Leather"),
        ("stone", "Stone"),
        ("bamboo", "Bamboo"),
        ("cotton", "Cotton"),
        ("silk", "Silk"),
        ("wool", "Wool"),
        ("linen", "Linen"),
        ("hemp", "Hemp"),
        ("jute", "Jute"),
        ("coir", "Coir"),
        ("sisal", "Sisal"),
        ("cork", "Cork"),
    ]

    name = models.CharField(max_length=255, choices=MATERIAL_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()  # Returns the human-readable name
    
class Certification(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    certificationNumber = models.CharField(max_length=255)
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="certifications")

class Product(models.Model):

    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('used_good', 'Used - Good'),
        ('used_fair', 'Used - Fair'),
        ('for_parts', 'For Parts or Not Working'),
    ]
    
    rootCategory = models.ForeignKey(RootCategory, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    mainCategory = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    
    materials = models.ManyToManyField(Materials, related_name="products")
    
    features = models.JSONField(null=True, blank=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, null=True, blank=True)
  
    
    
    recycled_content = models.FloatField(null=True, blank=True, help_text="Percentage of recycled materials used (0-100).")
    recyclability = models.BooleanField(default=False, help_text="Is the product recyclable?")
    carbon_footprint = models.FloatField(null=True, blank=True, help_text="Estimated carbon footprint in kg CO2e.")
    energy_efficiency = models.FloatField(null=True, blank=True, help_text="Energy consumption rating (e.g., kWh per year).")
    durability = models.IntegerField(null=True, blank=True, help_text="Expected lifespan in years.")
    repairability_score = models.FloatField(null=True, blank=True, help_text="Ease of repairability score (0-100).")
    ethical_sourcing = models.BooleanField(default=False, help_text="Are materials ethically sourced?")
    cruelity_free = models.BooleanField(default=False, help_text="Is the product cruelty-free?")
    plastic_free = models.BooleanField(default=False, help_text="Is the product plastic-free?")
    natural = models.BooleanField(default=False, help_text="Is the product made from natural materials?")
    destructable = models.BooleanField(default=False, help_text="Is the product destructible?")
    hazardous = models.BooleanField(default=False, help_text="Is the product hazardous?")
    
    sustainability_score = models.FloatField(null=True, blank=True, help_text="Sustainability score (0-100).")
    
    owned_from = models.DateField(auto_now=True)
    
    
    
   



class ProductImage(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="additionalImages")
    image = models.ImageField(upload_to="product_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


