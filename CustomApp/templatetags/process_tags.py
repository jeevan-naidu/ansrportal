from django import template
register = template.Library()


@register.filter('field_name')
def field_name(process, field):
    if field == "user":
        attr = getattr(process, field)
        attr = attr.first_name + " " + attr.last_name
    elif field == "attachment":
        attr = getattr(process, field)
        if attr:
            attr = attr.url
        else:
            attr = None
    else:
        attr = getattr(process, field)

    return attr


@register.filter('transaction_name_split')
def transaction_name_split(name):
    name_list = name.split("_")
    return reduce(lambda x, y: x.title() + " " + y.title(), name_list)
