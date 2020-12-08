from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
import numpy as np
# from django.db.models import Sum
# from django.shortcuts import reverse
# from django_countries.fields import CountryField


SCRIPT_CHOICES = (
    ('A', 'Apout'),
    ('B', 'Blog'),
    ('I', 'Index'),
    ('G', 'Group'),
    ('S', 'Sup-group'),
    ('F', 'Featurs'),
    ('U', 'Sup-feature'),
)

CONTENT_CHOICES = (
    ('S', 'Single spectrum'),
    ('G', 'Group spectra'),
    ('R', 'Reference')
)

NIR_TYPE_CHOICES = (
    ('N', 'Not mentioned'),
    ('U', 'Unknown'),
    ('A', 'Type A'),
    ('B', 'Type B'),
)


# class UserProfile(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
#     one_click_purchasing = models.BooleanField(default=False)

#     def __str__(self):
#         return self.user.username


class Spectrum(models.Model):
    origin = models.CharField(max_length=60)
    code = models.CharField(max_length=60)
    y_axis = models.TextField()
    x_range_max = models.FloatField(blank=True, null=True)
    x_range_min = models.FloatField(blank=True, null=True)
    nir_profile = models.ForeignKey(
        'NirProfile', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.origin

    def slug(self):
        return '_'joine(self.origin.split())

    def x_axis(self):
        return np.linspace(self.x_range_min, self.x_range_max, num=np.shape(self.y_axis)[1])

    def y_axis(self):
        return np.array(exec("["+y_axis+"]"))
        
    def get_absolute_url(self):
        return reverse("core:spectrum", kwargs={
            'slug': self.slug()
        })

    def get_add_to_graph_url(self):
        return reverse("core:add-to-graph", kwargs={
            'slug': self.slug()
        })

    def get_remove_from_graph_url(self):
        return reverse("core:remove-from-graph", kwargs={
            'slug': self.slug()
        })
        
    class Meta:
        verbose_name_plural = "Spectra"


class NirProfile(models.Model):
    # spectrum = models.ForeignKey('spectrum', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    nir_type = models.CharField(max_length=1, choices=NIR_TYPE_CHOICES, default="N")
    nir_method = models.TextField(blank=True, null=True)
    nir_configuration = models.TextField(blank=True, null=True)

    figure_id = models.CharField(max_length=10)


    
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)