from django.shortcuts import render, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from .models import (
    Category,
    Producer,
    ProductItem,
    Promocode,
    Discount,
    Basket,
)
from .serializers import (
    CategorySerializer,
    DiscountSerializer,
    PromocodeSerializer,
    ProducerSerializer,
    ProductItemSerializer,
    RegistarationSerializer,
    LoginSerializer,
    BasketSerializer,
    AddProductSerializer,
    DeleteProductSerializer,
    OrderSerializer,
    ProductItemDetailSerializer,
)
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import RegistredUser


from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import send_mail

from django.db.models import F
from drf_yasg.utils import swagger_auto_schema

from .tasks import some_task


class CategoriesListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        some_task.delay()
        return super().get(request, *args, **kwargs)


class DiscountsListView(ListAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = (AllowAny,)


class PromocodesListView(ListAPIView):
    queryset = Promocode.objects.all()
    serializer_class = PromocodeSerializer
    permission_classes = (AllowAny,)


class ProducersListView(ListAPIView):
    queryset = Producer.objects.all()
    serializer_class = ProducerSerializer
    permission_classes = (AllowAny,)


class ProductItemsListView(ListAPIView):
    queryset = ProductItem.objects.all()
    serializer_class = ProductItemSerializer
    permission_classes = (AllowAny,)


class SingleProductItemView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, product_id):
        product_item = (
            ProductItem.objects.prefetch_related("comment_set")
            .filter(id=product_id).first()
        )
        serializer = ProductItemDetailSerializer(product_item)
        return Response(serializer.data)


class CategoryProductsView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, cat_id):
        products = ProductItem.objects.filter(category__id=cat_id)
        serializer = ProductItemSerializer(products, many=True)
        return Response(serializer.data)


class ProducerProductsView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, producer_id):
        products = ProductItem.objects.filter(producer__id=producer_id)
        serializer = ProductItemSerializer(products, many=True)
        return Response(serializer.data)


class DiscountProductsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, discount_id):
        products = ProductItem.objects.filter(discount__id=discount_id)
        serializer = ProductItemSerializer(products, many=True)
        return Response(serializer.data)


class RegistartionView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistarationSerializer

    def send_mail(self, user_id, domain):
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
        send_mail(
            mail_subject,
            message,
            recipient_list=[to_email],
            from_email=settings.EMAIL_HOST_USER,
        )

    def post(self, request):
        user = request.data.get("user")
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        current_site = get_current_site(request)
        self.send_mail(user.id, current_site)

        return Response(serializer.data)


class ActivateAccountView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = RegistredUser.objects.get(id=uid)
        except Exception as e:
            user = None
        if user is not None and account_activation_token.check_token(
            user, token
        ):
            user.is_active = True
            user.save()
            return Response("Thank you for email confirmation!")
        return Response("Something Wrong with your account", status=403)


class LoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        request_body=LoginSerializer,
        request_method='POST',
        responses={
            200: LoginSerializer
        }
    )
    def post(self, request):
        user = request.data.get("user", {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)


class BasketView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        basket = (
            ProductItem.objects.prefetch_related("basket_set")
            .filter(basket__user=user)
            .values(
                "name",
                "price",
                "discount",
                number_of_item=F("basket__number_of_item"),
                discount_percent=F("discount__percent"),
                discount_expire_date=F("discount__expire_date"),
            )
        )
        serializer = BasketSerializer({"products": basket})

        return Response(serializer.data)

    def post(self, request):
        input_serializer = AddProductSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        product = get_object_or_404(
            ProductItem, id=input_serializer.data.get("product_id")
        )
        if product.count_on_stock >= input_serializer.data.get(
            "number_of_item"
        ):
            object, created = Basket.objects.get_or_create(
                user=request.user, product=product
            )
            is_deleted = False

            if object.number_of_item:
                object.number_of_item += input_serializer.data.get(
                    "number_of_item"
                )

                if object.number_of_item <= 0:
                    is_deleted = True
                    object.delete()
            else:
                object.number_of_item = input_serializer.data.get(
                    "number_of_item"
                )

            if not is_deleted:
                object.save()

            return Response(status=200)

        return Response("Not enought products on a stock", status=409)

    @swagger_auto_schema(
        request_body=DeleteProductSerializer,
        request_method='DELETE',
        responses={
            200: ""
        }
    )
    def delete(self, request):
        input_serializer = DeleteProductSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        product = get_object_or_404(
            ProductItem, id=input_serializer.data.get("product_id")
        )
        Basket.objects.get(user=request.user, product=product).delete()

        return Response(status=200)


class CreateOrderView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        input_serializer = OrderSerializer(
            data=request.data, context={"request": request}
        )
        input_serializer.is_valid(raise_exception=True)

        order = input_serializer.save()

        return Response(input_serializer.data)
