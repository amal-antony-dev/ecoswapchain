from django.db import models
import uuid

class Address(models.Model):
    trader = models.ForeignKey("esc_trader.Trader", on_delete=models.CASCADE, related_name='addresses', null=True)
    house_no_or_name = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100)
    district_number = models.IntegerField(null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"
    
    
    
class Message(models.Model):
    order = models.ForeignKey('esc_order.SwapOrder', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('esc_user.EcoUser', on_delete=models.CASCADE, related_name='sent_messages') 
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"


class ShippingDetails(models.Model):
    SHIPPING_METHOD_CHOICES = [
        ('swap', 'Swap Shipping Service'),
        ('self', 'Self Exchange'),
    ]

    shipping_method = models.CharField(max_length=20, choices=SHIPPING_METHOD_CHOICES, null=True, blank=True)
    seller_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='seller_shipping_details')
    buyer_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='buyer_shipping_details')
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    shipping_confirmed_by_seller = models.BooleanField(default=False)
    shipping_confirmed_by_buyer = models.BooleanField(default=False)
    product_verified = models.BooleanField(default=False)
    source_hub = models.ForeignKey('esc_hub.Hub', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_hub')
    destination_hub = models.ForeignKey('esc_hub.Hub', on_delete=models.SET_NULL, null=True, blank=True, related_name='target_hub')
    current_hub = models.ForeignKey('esc_hub.Hub', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_hub')



class SwapOrder(models.Model):
    STATUS_CHOICES = [
    ('pending', 'Pending'),            # Order placed, awaiting confirmation
    ('confirmed', 'Confirmed'),        # Order confirmed by seller
    ('processing', 'Processing'),      # Preparing for shipment
    ('packed', 'Packed'),              # Order has been packed
    ('shipped', 'Shipped'),            # Order is in transit
    ('out-for-delivery', 'Out for Delivery'),  # Last-mile delivery in progress
    ('delivered', 'Delivered'),        # Order successfully delivered
    ('cancelled', 'Cancelled'),        # Order cancelled before shipment
]


    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('escrow', 'Escrow'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    id = models.UUIDField(primary_key=True, auto_created=True, unique=True, default=uuid.uuid4)
    item = models.ForeignKey('esc_nft.NFT', on_delete=models.CASCADE, related_name='orders')
    seller = models.ForeignKey('esc_trader.Trader', on_delete=models.CASCADE, related_name='orders_as_seller')
    buyer = models.ForeignKey('esc_trader.Trader', on_delete=models.CASCADE, related_name='orders_as_buyer')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=15, decimal_places=5, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    ownership_transfer_transaction = models.ForeignKey('esc_transaction.NFTTransaction', on_delete=models.SET_NULL, null=True, blank=True, related_name='order')
    escrow_transaction = models.ForeignKey('esc_transaction.TokenTransaction', on_delete=models.SET_NULL, null=True, blank=True, related_name='order')
    shipping_details = models.OneToOneField(ShippingDetails, on_delete=models.SET_NULL, null=True, blank=True, related_name='order')

    def __str__(self):
        return f"Order {self.id} - ({self.status})"