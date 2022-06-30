from rest_framework import serializers
from .models import Category
from django.utils.translation import gettext_lazy as _


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    tn_parent = serializers.SlugRelatedField(queryset=Category.objects.all(), slug_field='id', required=False)
    tn_level = serializers.CharField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "tn_parent", "name", 'tn_level']
        # fields = "__all__"

    def validate(self, attrs):
        parent = attrs.get("tn_parent")
        if parent.tn_level > 1:
            raise serializers.ValidationError({'category': _("Only two level deep allowed!")})
        return attrs
