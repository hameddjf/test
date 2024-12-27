from rest_framework import serializers

from django.core.mail import send_mail
from django.conf import settings

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username','password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True},
        }

    def create(self, validated_data):
        user = CustomUser(**validated_data)
        # Set the password correctly
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("کاربری با این ایمیل وجود دارد.")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "کاربری با این نام کاربری وجود دارد.")
        return value

    # def validate_phone_number(self, value):
    #     if CustomUser.objects.filter(phone_number=value).exists():
    #         raise serializers.ValidationError(
    #             "کاربری با این شماره تلفن وجود دارد.")
    #     return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                "نام کاربری یا رمز عبور اشتباه است.")

        if not user.check_password(password):
            raise serializers.ValidationError(
                "نام کاربری یا رمز عبور اشتباه است.")

        attrs['user'] = user
        return attrs


class CustomUserChangeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    username = serializers.CharField(required=False)

    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):

        if 'old_password' in attrs and ('new_password' not in attrs or 'confirm_password' not in attrs):
            raise serializers.ValidationError(
                {"new_password": "New password and confirmation are required."})

        if 'new_password' in attrs and attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {"new_password": "New passwords must match."})

        return attrs

    def update(self, instance, validated_data):

        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get(
            'phone_number', instance.phone_number)
        instance.username = validated_data.get('username', instance.username)

        if 'new_password' in validated_data:
            instance.set_password(validated_data['new_password'])

        instance.save()
        return instance


# contact
class ContactSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=32)
    title = serializers.CharField(max_length=192)
    message = serializers.CharField()
    phone = serializers.CharField(max_length=11)

    def validate_phone(self, value):
        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "شماره تلفن باید فقط شامل اعداد باشد")

        if len(value) != 11:
            raise serializers.ValidationError("شماره تلفن باید 11 رقم باشد")

        if not value.startswith('09'):
            raise serializers.ValidationError("شماره تلفن باید با 09 شروع شود")

        return value

    def send_email(self):
        full_name = self.validated_data['full_name']
        title = self.validated_data['title']
        message = self.validated_data['message']
        phone = self.validated_data['phone']

        email_message = f"""
        پیام جدید از فرم تماس:

        نام و نام خانوادگی: {full_name}
        شماره تماس: {phone}
        عنوان: {title}

        پیام:
        {message}
        """

        send_mail(
            subject=f'پیام جدید از {full_name}',
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
