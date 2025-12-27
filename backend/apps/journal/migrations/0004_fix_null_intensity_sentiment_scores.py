# Generated migration to allow null values

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0003_journalentry_detected_emotions_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journalentry',
            name='intensity_score',
            field=models.FloatField(blank=True, help_text='Emotional intensity: 0.0 to 1.0', null=True),
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='sentiment_score',
            field=models.FloatField(blank=True, default=0.0, help_text='Sentiment: -1.0 (negative) to +1.0 (positive)', null=True),
        ),
    ]

