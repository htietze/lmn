# Generated by Django 3.1.2 on 2020-11-16 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lmn', '0003_auto_20201114_2231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='posted_date',
            field=models.DateField(),
        ),
    ]
