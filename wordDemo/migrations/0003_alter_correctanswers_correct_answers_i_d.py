# Generated by Django 5.0.6 on 2024-05-22 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wordDemo', '0002_correctanswers_correct_count_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='correctanswers',
            name='correct_answers_i_d',
            field=models.AutoField(db_column='correct_answers_id', primary_key=True, serialize=False),
        ),
    ]