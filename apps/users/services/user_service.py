from apps.core.services.users import UserServiceInterface
from apps.users.models import User
from django.core.exceptions import ValidationError

class UserService(UserServiceInterface):
    def create_user(self, tenant, data):
        required_fields = ['username', 'password', 'email']

        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            raise ValidationError(
                f'Campos obrigatórios ausentes: {", ".join(missing)}'
            )   

        user = User.objects.create_user(
            username=data['username'],
            password=data['password'],  # hash automático
            email=data.get('email'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            tenant=tenant
        )

        return user

    def update_user(self, user, data):
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)

        if 'password' in data:
            user.set_password(data['password'])

        user.save()
        return user

    def delete_user(self, user):
        user.delete()
        return True

    def list_users(self, tenant):
        return User.objects.filter(tenant=tenant)

    def get_user(self, tenant, user_id):
        return User.objects.get(tenant=tenant, id=user_id)
