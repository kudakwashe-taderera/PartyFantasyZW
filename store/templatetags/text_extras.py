from django import template

register = template.Library()


@register.filter
def lines(value):
    if value is None:
        return []
    text = str(value)
    return [line.strip() for line in text.splitlines() if line.strip()]
