# Generated by Django 3.2.7 on 2022-07-24 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('librarian', '0010_auto_20220724_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book_detail',
            name='book_issue_date',
            field=models.DateTimeField(auto_created=True),
        ),
        migrations.AlterField(
            model_name='book_detail',
            name='book_returned_date',
            field=models.DateTimeField(auto_created=True),
        ),
    ]
