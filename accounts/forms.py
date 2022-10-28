from django import forms
from orders.models import CategoryOffer, BrandOffer, ProductOffer 
from django.forms import ModelForm

class CategoryOfferForm(ModelForm):
    class Meta:
        model = CategoryOffer
        fields = [
            "category",
            "category_offer",
            "status",
        ]
        readonly_fields = [
            "created_at",
            "updated_at",
        ]


class BrandOfferForm(ModelForm):
    class Meta:
        model = BrandOffer
        fields = [
            "brand",
            "brand_offer",
            "status",
        ]
        readonly_fields = [
            "created_at",
            "updated_at",
        ]


class ProductOfferForm(ModelForm):
    class Meta:
        model = ProductOffer
        fields = [
            "product",
            "product_offer",
            "status",
        ]
        readonly_fields = [
            "created_at",
            "updated_at",
        ]
