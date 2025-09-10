from django import template
from django.contrib.messages.storage.base import Message

register = template.Library()

@register.filter
def to_list(messages):
    """
    Converts a Django messages object into a list of dictionaries.
    """
    message_list = []
    for message in messages:
        if isinstance(message, Message):
            message_list.append({
                'text': message.message,
                'tags': message.tags,
            })
    return message_list