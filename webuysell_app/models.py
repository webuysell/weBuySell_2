from django.db import models
from datetime import datetime
from django.conf import settings
import re, bcrypt

class UserManager(models.Manager):
    def register_validator(self, postData):
        errors = {}
        if len(postData['first_name']) < 2:
            errors['first_name'] = "Name must be at least 2 characters long."
        if len(postData['last_name']) < 2:
            errors['last_name'] = "Name must be at least 2 characters long."
        if len(postData['password']) < 8:
            errors['password'] = "Password cannot be less than 8 characters."
        if postData['password'] != postData['confirm_password']:
            errors['match'] = "Passwords do not match."
        if len(postData['email']) < 6:
            errors['email'] = "email is too short"
        EMAIL_REGEX = re.compile('^[_a-z0-9-]+(.[_a-z0-9-]+)@[a-z0-9-]+(.[a-z0-9-]+)(.[a-z]{2,4})$')
        if len(postData["email"]) == 0:
            errors["email_blank"] = "Email is required."
        elif not EMAIL_REGEX.match(postData['email']):
            errors['reg_email'] = "Email in wrong format"
        users_with_email = User.objects.filter(email=postData['email'])
        if len(users_with_email) >= 1:
            errors['dup'] = "Email taken, use another"
        return errors

    def update_validator(self, postData):
        errors = {}
        if len(postData['firstname']) < 2:
            errors['firstname'] = "Name must be at least 2 characters long."
        if len(postData['lastname']) < 2:
            errors['lastname'] = "Name must be at least 2 characters long."
        if len(postData['email']) < 6:
            errors['email'] = "email is too short"
        EMAIL_REGEX = re.compile('^[_a-z0-9-]+(.[_a-z0-9-]+)@[a-z0-9-]+(.[a-z0-9-]+)(.[a-z]{2,4})$')
        if len(postData["email"]) == 0:
            errors["email_blank"] = "Email is required."
        elif not EMAIL_REGEX.match(postData['email']):
            errors['reg_email'] = "Email in wrong format"
        if len(postData['password']) < 8:
            errors['password'] = "Password cannot be less than 8 characters."
        return errors

    def login_validator(self, postData):
        errors = {}
        if len(postData['password']) < 8:
            errors['password'] = "Password cannot be less than 8 characters."
        if len(postData['email']) < 6:
            errors['email'] = "email is too short"
        EMAIL_REGEX = re.compile('^[_a-z0-9-]+(.[_a-z0-9-]+)@[a-z0-9-]+(.[a-z0-9-]+)(.[a-z]{2,4})$')
        if len(postData["email"]) == 0:
            errors["email_blank"] = "Email is required."
        elif not EMAIL_REGEX.match(postData['email']):
            errors['reg_email'] = "Email in wrong format"

        return errors

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)
    followers= models.ManyToManyField("self", symmetrical=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    profile_pic = models.ImageField(null=True, blank=True, upload_to='images')

    objects = UserManager()

class ProductManager(models.Manager):
    def product_validator(self, postData):
        errors = {}
        
        #product_name
        if len(postData['product_name']) == 0:
            errors['product_name'] = 'Product name cannot be blank.'
        #condition
        if len(postData['condition']) == 0:
            errors['condition_blank'] = 'Condition cannot be blank.'
        #price
        if len(postData['price']) == 0.00:
            errors["price_blank"] = "You want some money at least"
        #negotiation
        if len(postData["negotiation"]) == 0:
            errors["negotiation_blank"] = "Please say Yes or No"

        return errors

class Product(models.Model):
    product_name = models.CharField(max_length=55)
    condition = models.CharField(max_length=55)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    negotiation = models.CharField(max_length=55)
    seller = models.ForeignKey(User, related_name="owner", on_delete=models.CASCADE)
    profile_pic = models.ImageField(null=True, blank=True, upload_to='images')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    objects = ProductManager()