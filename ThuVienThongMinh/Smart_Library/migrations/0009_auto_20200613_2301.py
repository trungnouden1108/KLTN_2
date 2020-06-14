# Generated by Django 3.0.3 on 2020-06-13 16:01

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Smart_Library', '0008_auto_20200613_2138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='id_book',
            field=models.CharField(default='', max_length=8),
        ),
        migrations.AlterField(
            model_name='cart',
            name='create1',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 13, 23, 1, 45, 504978, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='cart',
            name='create2',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 13, 23, 1, 45, 504978, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='cart',
            name='create3',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 13, 23, 1, 45, 504978, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='docgia',
            name='id_DG',
            field=models.CharField(default='', max_length=8),
        ),
        migrations.AlterField(
            model_name='id_book',
            name='id_Book',
            field=models.CharField(blank=True, default='', max_length=8),
        ),
        migrations.AlterField(
            model_name='id_docgia',
            name='Id_Docgia',
            field=models.CharField(blank=True, default='', max_length=8),
        ),
    ]