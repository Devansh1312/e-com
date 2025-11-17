from rest_framework import serializers
from reward_admin.models import *
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Q, Max, Prefetch


class UserSerializer(serializers.ModelSerializer):    
    presidencyclub_balance = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    
    def get_presidencyclub_balance(self, obj):
        """Return parent's balance if user is a child, otherwise return own balance"""
        if obj.parent:
            # If this is a child user, return parent's balance
            return obj.parent.presidencyclub_balance
        else:
            # If this is a parent user, return own balance
            return obj.presidencyclub_balance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Return only relative path instead of absolute URL
        if instance.profile_picture:
            representation['profile_picture'] = instance.profile_picture.url

        # Only include the first city ID if cities are available
        city_ids = list(instance.cities.values_list('id', flat=True))
        representation['city'] = city_ids[0] if city_ids else None
        representation.pop('cities', None)  # Remove full M2M field if you don't want it

        # Add child users array if user has children
        child_users = instance.children.all()
        if child_users.exists():
            representation['child_users'] = [
                {
                    'name': child.name if child.name else f"{child.first_name} {child.last_name}".strip(),
                    'membership_id': child.membership_id,
                    'presidencyclub_balance': instance.presidencyclub_balance  # Parent's balance for all children
                }
                for child in child_users
            ]
        else:
            representation['child_users'] = []

        return representation
 
class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'created_at']

    def to_representation(self, instance):
        """
        Convert the created_at field to a more readable format
        """
        ret = super().to_representation(instance)
        ret['created_at'] = instance.created_at.strftime("%Y-%m-%d %H:%M") if instance.created_at else None
        return ret


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = '__all__'

class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for maintenance records"""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'membership_id',
            'name',
            'full_name',
            'email',
            'phone'
        ]
    
    def get_full_name(self, obj):
        """Get user's full name"""
        if obj.name:
            return obj.name
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username
