# Generated migration for adding checkin/checkout times

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_paymentprovider_owner_alter_paymentprovider_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingguest',
            name='checkin_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='وقت الدخول'),
        ),
        migrations.AddField(
            model_name='bookingguest',
            name='checkout_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='وقت الخروج'),
        ),
    ]
