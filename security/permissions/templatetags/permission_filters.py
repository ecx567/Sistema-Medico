from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtiene un elemento de un diccionario por su clave"""
    if dictionary and key in dictionary:
        return dictionary.get(key)
    return None
