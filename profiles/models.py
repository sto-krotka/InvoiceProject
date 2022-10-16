from django.db import models
from django.contrib.auth.models import User
from xdg.Exceptions import ValidationError

from profiles.utils import generate_account_number


class Profile(models.Model):
    """class for the owner of the invoice"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=26, blank=True)
    company_name = models.CharField(max_length=220)
    company_info = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    avatar = models.ImageField(default='images/avatar.png')
    company_logo = models.ImageField(default='images/logo.png')

    def __str__(self):
        return f'profile of: {self.user}'

    def save(self, *args, **kwargs):
        if self.account_number == "":
            self.account_number = generate_account_number()
        return super().save(*args, **kwargs)

    #
    # def clean(self):
    #     if len(self.account_number) != 26:
    #         raise ValidationError('Back account must be 26 charaters long')