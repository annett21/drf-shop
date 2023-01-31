from django.urls import path, re_path
from .views import (
    CategoriesListView,
    DiscountsListView,
    ProducersListView,
    PromocodesListView,
    ProductItemsListView,
    CategoryProductsView,
    ProducerProductsView,
    DiscountProductsView,
    RegistartionView,
    ActivateAccountView,
    LoginView,
    BasketView,
    CreateOrderView,
    SingleProductItemView,
    GetStatisticView,

)


urlpatterns = [
    path("categories-all/", CategoriesListView.as_view(), name="categories-all"),
    path("discounts-all/", DiscountsListView.as_view(), name="discounts-all"),
    path("producers-all/", ProducersListView.as_view(), name="producers-all"),
    path("promocodes-all/", PromocodesListView.as_view(), name="promocodes-all"),
    path("products-all/", ProductItemsListView.as_view(), name="products-all"),
    path("category/<int:cat_id>/", CategoryProductsView.as_view(), name="category-by-id"),
    path("producer/<int:producer_id>/", ProducerProductsView.as_view(), name="producer-by-id"),
    path("discount/<int:discount_id>/", DiscountProductsView.as_view(), name="discount-by-id"),
    path("product/<int:product_id>/", SingleProductItemView.as_view()),
    path("register/", RegistartionView.as_view(), name="registration"),
    path("login/", LoginView.as_view(), name="login"),
    path("basket/", BasketView.as_view(), name="basket"),
    path("create_order/", CreateOrderView.as_view(), name="create-order"),
    path("get-statistic/", GetStatisticView.as_view()),

    path("activate/<slug:uidb64>/<slug:token>/", ActivateAccountView.as_view(), name="activate"),
   
]
