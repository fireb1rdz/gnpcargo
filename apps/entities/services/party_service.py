from domain.contracts.entity import PartyServiceInterface
from apps.entities.models import Entity, PartyRole, Party

class PartyService(PartyServiceInterface):
    @staticmethod
    def create_party(tenant, entity: Entity, role: PartyRole):
        party = Party.objects.create(
            tenant=tenant,
            entity=entity,
            role=role,
        )
        return party

    def can_be(self, entity: Entity, role: str):
        """
        Verifica se a entity pode ser um party.
        """
        return True

    def get_existing_roles(self):
        return PartyRole.choices

    def sync_entity_roles(self, entity, selected_roles):
        """
        Sincroniza papéis de uma entidade com base nos selecionados no formulário.
        """

        current_roles = set(
            Party.objects.filter(entity=entity)
            .values_list("role", flat=True)
        )

        selected_roles = set(selected_roles)

        # Criar novos papéis
        to_create = selected_roles - current_roles
        for role in to_create:
            Party.objects.create(
                entity=entity,
                role=role
            )

        # Remover papéis desmarcados
        to_remove = current_roles - selected_roles
        Party.objects.filter(
            entity=entity,
            role__in=to_remove
        ).delete()

    def get_roles_for_entity(self, entity):
        return Party.objects.filter(entity=entity).values_list("role", flat=True)

    def party_is_system(self, party):
        return party.entity.is_system
