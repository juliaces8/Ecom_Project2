from rest_framework import serializers
from .models import Store, Product, Review

# TTranslates Product model to JSON


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'store', 'name', 'description', 'price', 'stock']

    def validate_store(self, value):
        """
        Check that the store belongs to the logged-in user.
        """
        user = self.context['request'].user
        if value.vendor != user:
            raise serializers.ValidationError("You do not own this store.")
        return value

# Translates Store model to JSON


class StoreSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    owner_name = serializers.ReadOnlyField(source='vendor.username')

    class Meta:
        model = Store
        fields = ['id', 'name', 'owner_name', 'products']

# Translates Review model to JSON


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'content', 'is_verified']
