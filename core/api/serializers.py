from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from core.models import (
    User,
    )

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    class Meta:
        model = get_user_model()
        fields = ('id','email', 'password', 'name', 'is_staff')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 4}}
        read_only_Fields = ('id',)

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)
    def update(self, instance, validated_data):
        # Update a user, setting the password correctly and return it
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )

        print(attrs)
       
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')
        
        attrs['user'] = user
        return attrs

class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UserPictureSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ("id", "image",)
        read_only_Fields = ('id',)


class UserListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = get_user_model()
        fields = ('id','email', 'password', 'name', 'is_staff', 'image','created',)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 4, 'required':False}}
        read_only_Fields = ('id',)

        def create(self, validated_data):
            return User.objects.create(**validated_data)

        def update(self, instance, validated_data):
            # password = validated_data.pop('password')
            # Unless the application properly enforces that this field is
            # always set, the following could raise a `DoesNotExist`, which
            # would need to be handled.
            print(instance)

            instance.email = validated_data.get('email', instance.email)
            instance.name = validated_data.get('name', instance.name)
            instance.password = validated_data.get('password', instance.password)
            instance.is_staff = validated_data.get('is_staff', instance.is_staff)
            instance.save()
            return instance