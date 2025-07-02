from django import forms
from .models import Feedback , FeedbackResponse
from django.core.exceptions import ValidationError

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(),
            'comment': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Comparte tu experiencia con el doctor...',
                'class': 'form-control'
            }),
        }
        labels = {
            'rating': 'Calificación',
            'comment': 'Comentario'
        }
        
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if len(comment) < 10 and comment:
            raise ValidationError("El comentario debe tener al menos 10 caracteres.")
        return comment

class FeedbackResponseForm(forms.ModelForm):
    """Formulario para que los médicos respondan a las retroalimentaciones de los pacientes"""
    class Meta:
        model = FeedbackResponse
        fields = ['response_text']
        widgets = {
            'response_text': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Escribe tu respuesta al paciente...',
                'class': 'form-control'
            }),
        }
        labels = {
            'response_text': 'Tu respuesta'
        }
        
    def clean_response_text(self):
        response_text = self.cleaned_data.get('response_text')
        if not response_text or len(response_text.strip()) < 5:
            raise ValidationError("La respuesta debe contener al menos 5 caracteres.")
        return response_text
