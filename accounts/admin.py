from django.contrib import admin

# Register your models here.
from django.contrib import admin
from . import models
#from django.contrib.auth.admin import UserAdmin


#admin.site.register(Account, AccountAdmin)
admin.site.register(models.libra_rian)
admin.site.register(models.libra_rian_token)

