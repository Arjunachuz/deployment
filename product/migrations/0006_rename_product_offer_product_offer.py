# Generated by Django 4.0.7 on 2022-10-17 15:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_alter_product_product_offer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='product_offer',
            new_name='offer',
        ),
    ]
