# Generated by Django 2.1.7 on 2019-04-06 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libbackend', '0003_auto_20190331_2133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='authors',
            field=models.ManyToManyField(blank=True, related_name='books', to='libbackend.Author'),
        ),
        migrations.AlterField(
            model_name='book',
            name='genres',
            field=models.ManyToManyField(blank=True, related_name='books', to='libbackend.Genre'),
        ),
    ]