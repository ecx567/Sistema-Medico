from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Feedback(models.Model):
    RATING_CHOICES = [(1, '1 - Deficiente'), (2, '2 - Regular'), 
                      (3, '3 - Bueno'), (4, '4 - Muy Bueno'), 
                      (5, '5 - Excelente')]
    SENTIMENT_CHOICES = [
        ('positivo', 'Positivo'),
        ('neutral', 'Neutral'),
        ('negativo', 'Negativo'),
    ]
    
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                               related_name='given_feedbacks', 
                               limit_choices_to={'role': 'patient'})
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                              related_name='received_feedbacks',
                              limit_choices_to={'role': 'doctor'})
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, 
                                  related_name='feedback')
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True, 
                                 help_text="Notas administrativas (no visibles para pacientes o médicos)")

    # Campos para análisis de sentimiento
    sentiment = models.CharField(
        max_length=20, 
        choices=SENTIMENT_CHOICES,
        blank=True, 
        null=True,
        help_text="Sentimiento detectado automáticamente en el comentario"
    )
    sentiment_score = models.FloatField(
        null=True, 
        blank=True,
        help_text="Puntuación numérica del análisis de sentimiento (-1.0 a 1.0)"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Retroalimentación'
        verbose_name_plural = 'Retroalimentaciones'
        
    def __str__(self):
        return f"Calificación {self.rating}/5 de {self.patient} para {self.doctor}"

    def get_sentiment_display_class(self):
        """Devuelve una clase CSS según el sentimiento para mostrar en plantillas"""
        if not self.sentiment:
            return "secondary"
        
        sentiment_classes = {
            'positivo': 'success',
            'neutral': 'info',
            'negativo': 'danger'
        }
        return sentiment_classes.get(self.sentiment, 'secondary')


class FeedbackResponse(models.Model):
    """Modelo para respuestas de médicos a retroalimentaciones"""
    feedback = models.OneToOneField(
        Feedback, 
        on_delete=models.CASCADE, 
        related_name='response',
        help_text="Retroalimentación a la que se responde"
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedback_responses',
        limit_choices_to={'role': 'doctor'},
        help_text="Médico que responde"
    )
    response_text = models.TextField(
        verbose_name="Respuesta",
        help_text="Texto de respuesta a la retroalimentación del paciente"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Respuesta a retroalimentación"
        verbose_name_plural = "Respuestas a retroalimentaciones"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Respuesta del Dr. {self.doctor.get_full_name()} a retroalimentación #{self.feedback.id}"
