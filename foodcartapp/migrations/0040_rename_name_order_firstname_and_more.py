# Generated by Django 5.2.4 on 2025-07-24 05:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_rename_orderitem_orderproducts'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='name',
            new_name='firstname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='surname',
            new_name='lastname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='phone_number',
            new_name='phonenumber',
        ),
    ]
