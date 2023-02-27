from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import Category, Order, ProductItem, RegistredUser
from .tokens import account_activation_token


@shared_task()
def some_task():
    print("HELLO")
    return True


@shared_task()
def send_activation_mail(user_id, domain):
    user = RegistredUser.objects.get(id=user_id)
    mail_subject = "Activation link"
    message = render_to_string(
        "account_activation_email.html",
        {
            "user": user,
            "domain": domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
        },
    )
    to_email = user.email
    is_sent = send_mail(
        mail_subject,
        message,
        recipient_list=[to_email],
        from_email=settings.EMAIL_HOST_USER,
    )
    return is_sent


def _get_products_in_orders():
    orders = Order.objects.all()
    products_stat = dict()

    for order in orders:
        product_item = order.product_items
        for product in product_item.keys():
            product_in_stat = products_stat.get(product, None)
            if product_in_stat is None:
                products_stat[product] = 1
            else:
                products_stat[product] = products_stat[product] + 1
    
    return products_stat


@shared_task
def get_products_statistic():
    products_stat = _get_products_in_orders()

    max_value = max(products_stat.values())
    result_dict = {k: v for k, v in products_stat.items() if v == max_value}

    with open("products_statistic.txt", "w") as stat_file:
        for key, value in result_dict.items():
            product = ProductItem.objects.get(id=int(key))
            stat_text = f"The best selling product: {product.name}, it was sold {value} times.\n"
            stat_file.write(stat_text)


@shared_task()
def test_scheduled_task():
    return True


def _get_category_in_orders():
    orders = Order.objects.all()
    category_stat = dict()

    for order in orders:
        product_items = order.product_items 
        for product_id in product_items.keys():
            product = ProductItem.objects.get(id=product_id)

            if category_stat.get(product.category_id) is None:
                category_stat[product.category_id] = 1
            else:
                category_stat[product.category_id] += 1
    
    return category_stat


@shared_task
def get_category_statistic():
    category_stat = _get_category_in_orders()

    max_value = max(category_stat.values())
    result_dict = {k: v for k, v in category_stat.items() if v == max_value}

    with open("category_statistic.txt", "w") as stat_file:
        for key, value in result_dict.items():
            category = Category.objects.get(id=int(key))
            stat_text = f"The best selling product category: {category.name}, it was sold {value} times.\n"
            stat_file.write(stat_text)


@shared_task
def send_delivery_notif(order_id):
    order = Order.objects.filter(id=order_id).prefetch_related("user").first()
    mail_subject = "Delivery notification"
    message = render_to_string("delivery_notification.html", context={"order": order})
    to_email = order.user.email
    is_sent = send_mail(
        mail_subject,
        message,
        recipient_list=[to_email],
        from_email=settings.EMAIL_HOST_USER,
    )
    if is_sent:
        order.delivery_notif_sent = True
        order.save(update_fields=("delivery_notif_sent", ))
        
    return is_sent
