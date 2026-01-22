from django.urls import path
from .views import UserCreateView, UserListView, UserUpdateView, UserDeleteView, UserLoginView, UserLogoutView, HomeView

app_name = 'users'
urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path('usuarios/criar/', UserCreateView.as_view(), name='user_create'),
    path('usuarios/listar/', UserListView.as_view(), name='user_list'),
    path('usuarios/editar/<int:pk>/', UserUpdateView.as_view(), name='user_update'),
    path('usuarios/excluir/<int:pk>/', UserDeleteView.as_view(), name='user_delete'),
    path('', HomeView.as_view(), name='home'),
]