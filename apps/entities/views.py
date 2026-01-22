from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib import messages
from apps.entities.models import Entity
from apps.entities.forms import EntityForm

class EntityCreateView(CreateView):
    model = Entity
    form_class = EntityForm
    success_url = "/entidades/listar/"
    def form_valid(self, form):
        messages.success(self.request, 'Entidade criada com sucesso!')
        return super().form_valid(form)
    
class EntityListView(ListView):
    model = Entity
    context_object_name = "entities"
    paginate_by = 2
    
class EntityUpdateView(UpdateView):
    model = Entity
    form_class = EntityForm
    success_url = "/entidades/listar/"
    def form_valid(self, form):
        messages.success(self.request, 'Entidade atualizada com sucesso!')
        return super().form_valid(form)    
        
class EntityDeleteView(DeleteView):
    model = Entity
    success_url = "/entidades/listar/"