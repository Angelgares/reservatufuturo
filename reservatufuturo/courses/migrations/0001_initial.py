# Generated by Django 5.1.3 on 2024-11-22 20:10

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
                ('image', models.ImageField(blank=True, null=True, upload_to='course_images/')),
                ('teacher', models.CharField(max_length=100)),
                ('capacity', models.IntegerField(help_text='Maximum number of students')),
                ('description', models.TextField()),
                ('starting_date', models.DateField()),
                ('ending_date', models.DateField()),
                ('type', models.CharField(choices=[('Admnistrición General', 'Administración General'), ('Justicia', 'Justicia'), ('Educación', 'Educación'), ('Sanidad', 'Sanidad'), ('Policía', 'Policía'), ('Bomberos', 'Bomberos'), ('Prisiones', 'Prisiones'), ('Hacienda', 'Hacienda'), ('Inspecto de Trabajo', 'Inspector de Trabajo'), ('Técnicos de Ayuntamientos', 'Técnicos de Ayuntamientos'), ('Informática', 'Informática'), ('Telecomunicaciones', 'Telecomunicaciones'), ('Tecnología de la Información', 'Tecnologías de la Información')], default='Magisterio', max_length=50)),
            ],
        ),
    ]
