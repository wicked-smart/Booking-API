from django import template
register = template.Library()


@register.filter(name='multiply')
def multiply(value, arg):

    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value


@register.simple_tag
def calculate_gst_total(adults, children, infants, base_fare, gst_rate):
    total_base_fare = adults * base_fare + children * base_fare + infants * 550
    gst_amount = total_base_fare * gst_rate
    return gst_amount