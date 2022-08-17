from django.db import models

# Create your models here.
from django.db import models
# Create your models here.
#country_code_options
from django.contrib.auth.models import AbstractUser
import datetime,pytz
class libra_rian(models.Model):
	email=models.EmailField(verbose_name="email", max_length=60, unique=True)
	username=models.CharField(verbose_name="nic name",max_length=30,default='')
	password=models.TextField(default="")
	status=models.CharField(max_length=30,default='')
	first_name=models.CharField(max_length=100)
	last_name=models.CharField(max_length=100)
	user_type= models.CharField(max_length=12,default='librarian')
	address_line_1=models.CharField(max_length=200,default='')
	address_line_2=models.CharField(max_length=200,default='')
	profile_pic=models.ImageField(upload_to='consumer/profile_image',default='deafult_profile_pic.jpeg')
	is_verified=models.BooleanField(default=False)
	is_active=models.BooleanField(default=True)
	is_user_blocked=models.BooleanField(default=False)
	otp=models.CharField(max_length=200,default='')
	country_code=models.CharField(max_length=10)
	phone_number=models.CharField(max_length=15)
	country=models.CharField(max_length=100,default='')#(multiple=False)
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['first_name','last_name','country_code','phone_number']
	def __str__(self):
		return 'ID='+str(self.id)+'user='+str(self.username)

class libra_rian_token(models.Model):
	uzr=models.OneToOneField(libra_rian,on_delete=models.CASCADE,related_name='token')
	token=models.CharField(max_length=10,default='')
	def __str__(self):
		return 'ID='+str(self.id)+'user='+str(self.uzr)+'token='+str(self.token)
	



