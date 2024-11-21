# Generated by Django 5.1.3 on 2024-11-21 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Course name', max_length=100)),
                ('price', models.FloatField(help_text='Course price', max_length=10)),
                ('image', models.ImageField(blank=True, null=True, upload_to='course_images')),
                ('teacher', models.CharField(max_length=100)),
                ('capacity', models.IntegerField(help_text='Maximum number of students')),
                ('description', models.TextField()),
                ('starting_date', models.DateField()),
                ('ending_date', models.DateField()),
                ('type', models.CharField(choices=[('INF', 'Informática'), ('BIO', 'Biología'), ('QUI', 'Química'), ('FIS', 'Física'), ('MAT', 'Matemáticas'), ('HIS', 'Historia'), ('ECO', 'Economía'), ('PSI', 'Psicología'), ('ART', 'Arte'), ('IDI', 'Idiomas')], default='Magisterio', max_length=15)),
            ],
        ),
    ]
