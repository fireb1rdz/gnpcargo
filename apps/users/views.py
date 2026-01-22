from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .forms import CustomAuthenticationForm
from apps.users.models import User
from apps.users.forms import UserForm

class UserLoginView(LoginView):
    template_name = "auth/login.html"
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        messages.success(self.request, 'Login realizado com sucesso!')
        return reverse_lazy("users:home")

class UserLogoutView(LogoutView):
    next_page = reverse_lazy("users:login")

class UserCreateView(CreateView):
    model = User
    form_class = UserForm
    success_url = "/usuarios/listar/"
    def form_valid(self, form):
        messages.success(self.request, 'Usuário criado com sucesso!')
        return super().form_valid(form)
    
class UserListView(ListView):
    model = User
    context_object_name = "users"
    paginate_by = 10
    
class UserUpdateView(UpdateView):
    model = User
    form_class = UserForm
    success_url = "/usuarios/listar/"
    def form_valid(self, form):
        messages.success(self.request, 'Usuário atualizado com sucesso!')
        return super().form_valid(form)    
        
class UserDeleteView(DeleteView):
    model = User
    success_url = "/usuarios/listar/"

class HomeView(TemplateView):
    template_name = "auth/home.html"