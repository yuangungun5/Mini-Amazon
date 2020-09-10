from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image

class Product(models.Model):
    productID = models.AutoField(primary_key=True)
    description = models.CharField(max_length=100)
    price =  models.IntegerField(default=10)
    image = models.ImageField(default='loading.png', upload_to='product_images')

    def get_absolute_url(self):
        return reverse('product-detail', kwargs = {'pk': self.pk})

    def save(self, **kwargs):
        super().save( **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
    
class Order(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    upsAccount = models.CharField(max_length=100, null=True, blank=True)    
    status = models.CharField(max_length=20, default='created')
    coordinateX = models.IntegerField(default=0)
    coordinateY = models.IntegerField(default=0)
    timeCreated = models.DateTimeField(auto_now=True)
    
    '''
    timePacking = models.DateTimeField(null=True, blank=True)
    timePacked = models.DateTimeField(null=True, blank=True)
    timeLoading = models.DateTimeField(null=True, blank=True)
    timeLoaded = models.DateTimeField(null=True, blank=True)
    timeDelivering = models.DateTimeField(null=True, blank=True)
    timeDelivered = models.DateTimeField(null=True, blank=True)
    '''
    
    def get_absolute_url(self):
        return reverse('order-detail', kwargs = {'pk': self.pk})

class Cart(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False)
    total_price = models.IntegerField(default=0)
    count = models.IntegerField(default=1)
    order_id = models.IntegerField(default=0)

class Warehouse(models.Model):
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)

class Stock(models.Model):
    warehouse_id = models.IntegerField(default=0)
    product_id = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)

class Money(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    recharge=models.IntegerField(default=0)

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False)
