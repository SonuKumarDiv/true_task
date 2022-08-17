# Generated by Django 3.2.7 on 2022-07-23 07:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book_detail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_name', models.CharField(max_length=60)),
                ('author_name', models.CharField(default='', max_length=30)),
                ('status', models.CharField(default='', max_length=30)),
                ('book_issue_date', models.DateTimeField(auto_now_add=True)),
                ('book_returned_date', models.DateTimeField(auto_now=True)),
                ('book_price', models.IntegerField(default=0)),
                ('book_used_by', models.ManyToManyField(blank=True, related_name='book_used_by', to='accounts.Member')),
                ('librarian', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='librarian', to='accounts.libra_rian')),
            ],
        ),
        migrations.CreateModel(
            name='authorizations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_task', models.CharField(blank=True, max_length=100, null=True)),
                ('view_book', models.BooleanField(default=False)),
                ('manage_book', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='authorize', to='accounts.libra_rian')),
            ],
        ),
    ]
