from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .forms import CustomAuthenticationForm
from apps.users.models import User
from apps.users.forms import UserForm
from apps.entities.models import Entity

class UserLoginView(LoginView):
    template_name = "auth/login.html"
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        self.request.session["entity_id"] = form.cleaned_data["entity"].id
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Login realizado com sucesso!')
        if self.request.session.get("entity_id"):
            self.request.user.entity = Entity.objects.get(id=self.request.session.get("entity_id"))
            self.request.user.save()
            return reverse_lazy("users:home")
        else:
            return reverse_lazy("users:login")
            
class UserLogoutView(LogoutView):
    next_page = reverse_lazy("users:login")

    def dispatch(self, request, *args, **kwargs):
        request.session.pop("entity_id", None)
        return super().dispatch(request, *args, **kwargs)

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