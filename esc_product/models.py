from django.db import models

# Create your models here.

class RootCategory(models.Model):
    name = models.CharField(max_length=255)
    
class MainCategory(models.Model):
    name = models.CharField(max_length=255)

class Product(models.Model):
    rootCategory = models.ForeignKey(RootCategory, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    mainCategory = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    
    features = models.JSONField(null=True, blank=True)
    material = models.CharField(max_length=255, null=True, blank=True)
    condition = models.CharField(max_length=255, null=True, blank=True)




class ProductImage(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="additionalImages")
    image = models.ImageField(upload_to="product_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


