# Generated manually to fix Professional model fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('professionals', '0002_alter_escalationticket_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professional',
            name='specialization',
            field=models.CharField(blank=True, default='', help_text='Area of specialization (e.g., Anxiety, Depression)', max_length=200),
        ),
        migrations.AlterField(
            model_name='professional',
            name='city',
            field=models.CharField(blank=True, default='', help_text='City where professional practices', max_length=100),
        ),
    ]

