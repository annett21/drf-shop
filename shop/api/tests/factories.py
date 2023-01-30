import factory
from api.models import (
    Category,
    Discount,
    Promocode,
    Producer,
    ProductItem,
    RegistredUser,
    Basket,
    Cashback,
)
import pytz


class CategoryFactory(factory.django.DjangoModelFactory):
    _categories = (
        "Shoes",
        "Boots",
        "Trainers",
        "Clothes",
        "Dress",
        "T-shirt",
        "Jeans",
        "Shirts",
        "PrintedShirts",
        "TankTops",
        "PoloShirt",
        "Beauty",
        "DIYTools",
        "GardenOutdoors",
        "Grocery",
        "HealthPersonalCare",
        "Lighting",
    )

    class Meta:
        model = Category

    name = factory.Faker("random_element", elements=_categories)
    description = factory.Faker("sentence", nb_words=20)


class DiscountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Discount

    name = factory.Faker("word", part_of_speech="adjective")
    percent = factory.Faker("pyint", max_value=50)
    expire_date = factory.Faker(
        "date_time_this_month",
        before_now=False,
        after_now=True,
        tzinfo=pytz.UTC,
    )


class PromocodeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Promocode

    name = factory.Faker(
        "pystr_format",
        string_format="?????####",
        letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    )
    percent = factory.Faker("pyint", max_value=35)
    expire_date = factory.Faker(
        "date_time_this_month",
        before_now=False,
        after_now=True,
        tzinfo=pytz.UTC,
    )
    is_allowed_to_sum_with_discounts = factory.Faker("pybool")


class ProducerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Producer

    name = factory.Faker("company")


class ProductItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductItem

    name = factory.Faker("word", part_of_speech="noun")
    articul = factory.Faker("random_number", digits=10)
    price = factory.Faker(
        "pyfloat", right_digits=2, positive=True, max_value=20_000
    )
    count_on_stock = factory.Faker("pyint", max_value=500)
    producer = factory.Iterator(Producer.objects.all(), cycle=True)
    category = factory.Iterator(Category.objects.all(), cycle=True)
    description = factory.Faker("text", max_nb_chars=150)
    discount = factory.Iterator(Discount.objects.all(), cycle=True)


class RegistredUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RegistredUser

    password = factory.Faker("password")
    # sex = factory.Faker("random_element", elements=["F", "M"])
    email = factory.Faker("email")
    age = factory.Faker("pyint", min_value=18, max_value=99)
    phone = factory.Faker("msisdn")
    login = factory.Faker("user_name")
    # weekly_discount_notif_required = factory.Faker("pybool")
    # cashback = factory.Faker("pyint", max_value=200)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class BasketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Basket

    user = factory.Iterator(RegistredUser.objects.all(), cycle=True)
    product = factory.Iterator(ProductItem.objects.all(), cycle=True)
    number_of_item = factory.Faker("pyint", min_value=1, max_value=5)


class CashbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cashback
        
    name = factory.Faker("word", part_of_speech="adjective")
    percent = factory.Faker("pyint", max_value=10)
    max_cashback_payment = factory.Faker("pyint", max_value=15)
