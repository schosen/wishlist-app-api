# Generated by Django 3.2.23 on 2024-02-10 18:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20240201_2200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='wishlist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.wishlist'),
        ),
    ]
