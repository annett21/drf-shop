from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import (
    Category,
    Discount,
    Promocode,
    Producer,
    ProductItem,
    RegistredUser,
    Order,
    Cashback,
    Comment,
)
from django.contrib.auth import authenticate
import datetime


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class DiscountSerializer(ModelSerializer):
    class Meta:
        model = Discount
        fields = "__all__"


class ProducerSerializer(ModelSerializer):
    class Meta:
        model = Producer
        fields = "__all__"


class PromocodeSerializer(ModelSerializer):
    class Meta:
        model = Promocode
        fields = "__all__"


class CommentSerializer(ModelSerializer):
    author = serializers.CharField(source="user.email")
    text = serializers.CharField(source="comment")

    class Meta:
        model = Comment
        fields = ["author", "text"]


class ProductItemDetailSerializer(ModelSerializer):
    category_name = serializers.CharField(source="category.name")
    discount_name = serializers.CharField(source="discount.name")
    discount_percent = serializers.IntegerField(source="discount.percent")
    producer_name = serializers.CharField(source="producer.name")
    comments = CommentSerializer(many=True, source="comment_set")

    class Meta:
        model = ProductItem
        fields = [
            "id",
            "name",
            "description",
            "producer_name",
            "category_name",
            "discount_name",
            "discount_percent",
            "price",
            "articul",
            "count_on_stock",
            "comments",
        ]


class ProductItemSerializer(ModelSerializer):
    producer = ProducerSerializer()
    category = CategorySerializer()
    discount = DiscountSerializer()

    class Meta:
        model = ProductItem
        fields = [
            "id",
            "name",
            "discount",
            "description",
            "producer",
            "category",
            "price",
            "articul",
            "count_on_stock",
        ]


class RegistarationSerializer(ModelSerializer):
    password = serializers.CharField(
        max_length=100, min_length=8, write_only=True
    )

    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = RegistredUser
        fields = ["phone", "email", "password", "login", "token", "age"]

    def create(self, validated_data):
        return RegistredUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=13)
    password = serializers.CharField(max_length=100, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        phone = data.get("phone", None)
        password = data.get("password", None)

        if phone is None:
            raise serializers.ValidationError(
                "Phone number is required to log in"
            )

        if password is None:
            raise serializers.ValidationError("Password is required to log in")

        user = authenticate(username=phone, password=password)

        if user is None:
            raise serializers.ValidationError(
                "A user with this password and phone was not found"
            )

        if not user.is_active:
            raise serializers.ValidationError("This account was not verified")

        return {"phone": user.phone, "token": user.token}


class ProductInBasketSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    number_of_item = serializers.IntegerField()


class BasketSerializer(serializers.Serializer):
    products = ProductInBasketSerializer(many=True)
    result_price = serializers.SerializerMethodField()

    def get_result_price(self, data):
        result_price = 0

        for item in data.get("products"):
            if item.get("discount"):
                percent = item.get("discount_percent")
                expire_date = item.get("discount_expire_date")
                delta = expire_date - datetime.datetime.now(
                    datetime.timezone.utc
                )
                if delta.days >= 0 and delta.seconds > 0:
                    result_price += (
                        float(item.get("price"))
                        * ((100 - percent) / 100)
                        * item.get("number_of_item")
                    )
                else:
                    result_price += item.get("price") * item.get(
                        "number_of_item"
                    )
            else:
                result_price += item.get("price") * item.get("number_of_item")

        return result_price


class AddProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    number_of_item = serializers.IntegerField()


class DeleteProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class OrderSerializer(serializers.ModelSerializer):
    def run_validation(self, data=None):
        return data

    class Meta:
        model = Order
        fields = "__all__"

    def calculate_result_price(self, data):
        product_items_dict = data.get("product_items")
        product_items_ids = product_items_dict.keys()
        product_items = ProductItem.objects.filter(
            id__in=product_items_ids
        ).values("id", "price", "discount__percent", "discount__expire_date")
        promocode_name = data.get("promocode")
        promocode = Promocode.objects.filter(name=promocode_name).first()

        result_price = 0
        result_price_with_discounts = 0

        for item in product_items:
            number_of_items = product_items_dict.get(str(item.get("id")))
            discount_percent = item.get("discount__percent")
            price = float(item.get("price"))
            result_price += price * number_of_items

            if discount_percent:
                discount_expire = item.get("discount__expire_date")
                delta = discount_expire - datetime.datetime.now(
                    datetime.timezone.utc
                )
                if delta.days >= 0 and delta.seconds > 0:
                    result_price_with_discounts += (
                        price
                        * (100 - discount_percent)
                        / 100
                        * number_of_items
                    )
                else:
                    result_price_with_discounts += price * number_of_items
            else:
                result_price_with_discounts += price * number_of_items

        if promocode:
            delta = promocode.expire_date - datetime.datetime.now(
                datetime.timezone.utc
            )
            if delta.days >= 0 and delta.seconds > 0:
                if promocode.is_allowed_to_sum_with_discounts:
                    result_price = (
                        result_price_with_discounts
                        * (100 - promocode.percent)
                        / 100
                    )
                else:
                    result_price = (
                        result_price * (100 - discount_percent) / 100
                    )
            else:
                result_price = result_price_with_discounts
        else:
            result_price = result_price_with_discounts

        cashback = Cashback.objects.all().first()
        add_cashback_points = result_price * (cashback.percent / 100)
        user = self.context.get("request").user

        if data.get("use_cashback"):
            if user.cashback <= cashback.max_cashback_payment:
                result_price -= user.cashback
                user.cashback = 0
            else:
                result_price -= cashback.max_cashback_payment
                user.cashback -= cashback.max_cashback_payment

        user.cashback += add_cashback_points
        user.save()

        return result_price

    def result_number_of_items(self, data):
        return sum(data.get("product_items").values())

    def get_user(self):
        request = self.context.get("request")
        return request.user

    def create(self, validated_data):
        validated_data["result_price"] = self.calculate_result_price(
            validated_data
        )
        validated_data["result_number_of_items"] = self.result_number_of_items(
            validated_data
        )
        validated_data["user"] = self.get_user()

        if validated_data.get("promocode"):
            validated_data.pop("promocode")

        validated_data.pop("use_cashback")

        return Order.objects.create(**validated_data)
