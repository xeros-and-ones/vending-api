# Generated by Django 5.0.1 on 2024-02-06 06:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0003_alter_user_deposit"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="seller_id",
            new_name="seller",
        ),
    ]
