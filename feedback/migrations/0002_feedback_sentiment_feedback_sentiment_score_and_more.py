# Generated by Django 5.2.2 on 2025-06-30 04:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='sentiment',
            field=models.CharField(blank=True, choices=[('positivo', 'Positivo'), ('neutral', 'Neutral'), ('negativo', 'Negativo')], help_text='Sentimiento detectado automáticamente en el comentario', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='sentiment_score',
            field=models.FloatField(blank=True, help_text='Puntuación numérica del análisis de sentimiento (-1.0 a 1.0)', null=True),
        ),
        migrations.CreateModel(
            name='FeedbackResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_text', models.TextField(help_text='Texto de respuesta a la retroalimentación del paciente', verbose_name='Respuesta')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('doctor', models.ForeignKey(help_text='Médico que responde', limit_choices_to={'role': 'doctor'}, on_delete=django.db.models.deletion.CASCADE, related_name='feedback_responses', to=settings.AUTH_USER_MODEL)),
                ('feedback', models.OneToOneField(help_text='Retroalimentación a la que se responde', on_delete=django.db.models.deletion.CASCADE, related_name='response', to='feedback.feedback')),
            ],
            options={
                'verbose_name': 'Respuesta a retroalimentación',
                'verbose_name_plural': 'Respuestas a retroalimentaciones',
                'ordering': ['-created_at'],
            },
        ),
    ]
