from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration according to API specification.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'confirmed_password')

    def validate(self, attrs):
        if attrs['password'] != attrs['confirmed_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    
    def validate_email(self, value):
        """
        Check if email already exists.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def create(self, validated_data):
        validated_data.pop('confirmed_password')
        validated_data['username'] = validated_data['email']
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data['username'],
            is_active=False
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login according to API specification.
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('Account not activated')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Email and password required')


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    """
    email = serializers.EmailField()
    
    def validate_email(self, value):
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    """
    new_password = serializers.CharField(validators=[validate_password])
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'date_joined', 'username')