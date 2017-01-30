from django import template
register = template.Library()


@register.filter('field_name')
def field_name(process, field):
    if field == "user":
        attr = getattr(process, field)
        attr = attr.first_name + " " + attr.last_name
    else:
        attr = getattr(process, field)

    return attr

