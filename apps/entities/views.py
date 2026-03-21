from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib import messages
from apps.entities.models import Entity
from apps.entities.forms import EntityForm

class EntityCreateView(CreateView):
    model = Entity
    form_class = EntityForm
    success_url = "/entidades/listar/"

    def form_valid(self, form):
        response = super().form_valid(form)

        from domain.bootstrap.service_container import get_party_service
        party_service = get_party_service()

        party_service.sync_entity_roles(
            self.object,
            form.selected_roles
        )

        messages.success(self.request, 'Entidade criada com sucesso!')
        return response

    def form_invalid(self, form):
        messages.warning(self.request, f'Erro ao criar entidade! {form.errors}')
        return super().form_invalid(form)

class EntityListView(ListView):
    model = Entity
    context_object_name = "entities"
    paginate_by = 15
    def get_queryset(self):
        return Entity.objects.filter(tenant=self.request.tenant)
    
class EntityUpdateView(UpdateView):
    model = Entity
    form_class = EntityForm
    success_url = "/entidades/listar/"

    def form_valid(self, form):
        response = super().form_valid(form)

        from domain.bootstrap.service_container import get_party_service
        party_service = get_party_service()

        party_service.sync_entity_roles(
            self.object,
            form.selected_roles
        )

        messages.success(self.request, 'Entidade atualizada com sucesso!')
        return response

    def form_invalid(self, form):
        messages.warning(self.request, f'Erro ao atualizar entidade! {form.errors}')
        return super().form_invalid(form)
        
class EntityDeleteView(DeleteView):
    model = Entity
    success_url = "/entidades/listar/"