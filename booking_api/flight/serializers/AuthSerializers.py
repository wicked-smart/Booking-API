from flight.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import EmailValidator

class RegisterUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True,
                                    validators=[UniqueValidator(queryset=User.objects.all(), message="User with Email already exists!!!" )])
    username = serializers.CharField(required=True, validators=([UniqueValidator(queryset=User.objects.all(), message="User  already exists!!!" )]))
    confirmation = serializers.CharField(required=True, max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'mobile_no', 'email', 'username', 'password', 'confirmation']
        #validators = [ UniqueValidator(queryset=User.objects.all(), message="Username Not Available!")]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
            "username": {"required": True},
            "password": {"required": True, "write_only": True},
            "mobile_no": {"required": True}
        }
    
    
    def validate(self, attrs):

        if attrs["password"] != attrs["confirmation"]:
            raise serializers.ValidationError("Password and confirmation Does Not Match!")

        return attrs
        
    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")

        user = User.objects.create_user(username=username, **validated_data)

        user.set_password(password)

        user.save()
        return user



class LoginUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=100, required=True)
    
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {
            "username": {"required": True},
            "password": {"required": True},
        }


