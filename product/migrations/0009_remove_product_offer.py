# Generated by Django 4.0.7 on 2022-10-18 12:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_product_offer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='offer',
        ),
    ]
