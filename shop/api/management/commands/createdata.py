from faker import Faker
from django.core.management.base import BaseCommand

from tests.factories import (
    CategoryFactory,
    ProducerFactory,
    DiscountFactory,
    ProductItemFactory,
    PromocodeFactory,
    CashbackFactory,
    RegistredUserFactory
)


class Command(BaseCommand):
    help = "Command information"

    def handle(self, *args, **kwargs):
        Faker(["en_US"])

        for _ in range(5):
            CategoryFactory()
            ProducerFactory()
            DiscountFactory()
            ProductItemFactory()
            PromocodeFactory()
            CashbackFactory()
            RegistredUserFactory()
            print("Successfully added to DB!")
