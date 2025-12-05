from rest_framework import serializers
from reward_admin.models import User, FAQ, SystemSettings, cart, wishlist, product


class UserSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    gender_name = serializers.SerializerMethodField()
    state_name = serializers.SerializerMethodField()
    cart_items = serializers.SerializerMethodField()
    wishlist_items = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'name',
            'email',
            'phone',
            'date_of_birth',
            'gender',
            'gender_name',
            'country',
            'state',
            'state_name',
            'city',
            'address',
            'pincode',
            'profile_picture',
            'profile_picture_url',
            'device_type',
            'device_token',
            'register_type',
            'is_active',
            'created_at',
            'updated_at',
            'cart_items',
            'wishlist_items',
        ]
        read_only_fields = (
            'username',
            'register_type',
            'created_at',
            'updated_at',
        )

    def get_city(self, obj):
        city = obj.cities.first()
        return city.id if city else None

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            url = obj.profile_picture.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_gender_name(self, obj):
        return obj.gender.name if obj.gender else None

    def get_state_name(self, obj):
        return obj.state.name if obj.state else None

    def get_cart_items(self, obj):
        return cart.objects.filter(customer=obj).count()

    def get_wishlist_items(self, obj):
        return wishlist.objects.filter(customer=obj).count()
 

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'created_at']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['created_at'] = instance.created_at.strftime("%Y-%m-%d %H:%M") if instance.created_at else None
        return ret


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = '__all__'


class UserBasicSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'name',
            'full_name',
            'email',
            'phone',
        ]

    def get_full_name(self, obj):
        if obj.name:
            return obj.name
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name or obj.username
