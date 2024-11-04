from django import template

register = template.Library()

@register.filter
def get_attr(obj, attr_name):
    print("Passage dans custom filters ")
    print(f"get_attr de objet : {obj} et de attr_name : {attr_name}")
    return getattr(obj, attr_name, "None")
