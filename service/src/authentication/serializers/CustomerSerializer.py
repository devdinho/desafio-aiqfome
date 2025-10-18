from rest_framework import serializers

from authentication.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer para o modelo de usuário.

    ### Utilizado para converter objetos de usuário em JSON e vice-versa.

    Campos:
    - id: Identificador único do usuário.
    - first_name: Primeiro nome do usuário.
    - last_name: Último nome do usuário.
    - username: Nome de usuário.
    - password: Senha do usuário.
    - email: Endereço de e-mail do usuário.
    - last_login: Data e hora do último login do usuário.
    - date_joined: Data e hora de criação do usuário.
    """

    class Meta:
        model = Customer
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "password",
            "email",
            "last_login",
            "date_joined",
        )
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ("last_login", "date_joined")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance or (isinstance(self.instance, list) and not self.instance):
            self.fields["password"].required = True
        else:
            self.fields["password"].required = False

    def create(self, validated_data):
        newCustomer = Customer(
            username=validated_data.get("username", None),
            first_name=validated_data.get("first_name", None),
            last_name=validated_data.get("last_name", None),
            email=validated_data.get("email", None).lower(),
        )

        newCustomer.set_password(validated_data.get("password", None))
        try:
            newCustomer.save()
        except Exception as e:
            raise serializers.ValidationError(str(e.__cause__))

        return newCustomer

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)

        if "password" in validated_data:
            instance.set_password(validated_data["password"])

        instance.save()

        return instance
