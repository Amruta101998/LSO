# Generated by Django 4.0.2 on 2022-02-27 15:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_orders_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.TextField(max_length=30)),
                ('amount', models.IntegerField(max_length=300)),
                ('order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.orders')),
            ],
        ),
    ]
