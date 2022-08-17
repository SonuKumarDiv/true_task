from django.db import models

# Create your models here.

from django.db import models
from accounts import models as ac_models

class authorizations(models.Model):
	user=models.OneToOneField(ac_models.libra_rian,on_delete=models.CASCADE,related_name='authorize')
	job_task=models.CharField(max_length=100,null=True,blank=True)
	view_book=models.BooleanField(default=True)
	manage_book=models.BooleanField(default=True)
	remove_book=models.BooleanField(default=True)
	add_book=models.BooleanField(default=True)
	add_member=models.BooleanField(default=True)
	update=models.BooleanField(default=True)
	delete_member=models.BooleanField(default=True)
	view_member=models.BooleanField(default=True)
	barrow_book=models.BooleanField(default=True)
	return_book=models.BooleanField(default=True)

    #social Profile

class Book_detail(models.Model):
	librarian=models.ForeignKey(ac_models.libra_rian,blank=True,on_delete=models.SET_NULL,null=True,related_name='librarian')
	book_used_by =models.ManyToManyField(ac_models.libra_rian,null=True,blank=True,related_name='book_used_by')
	book_name=models.CharField(max_length=60)
	author_name=models.CharField(max_length=30,default='')
	status=models.CharField(max_length=30,default='')
	book_issue_date=models.DateTimeField(auto_now=True )
	book_returned_date=models.DateTimeField(auto_now=True )
	book_price=models.IntegerField(default=0)
	