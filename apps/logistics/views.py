from apps.entities.models import Party
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.views.generic import ListView
from .models import Conference
# from domain.schemas.conference_table import ConferenceTableSchema
from domain.bootstrap.service_container import get_conference_application_service, get_package_service
from .forms import ConferenceCreateForm
from django.http import JsonResponse
import json

class ConferenceCreateView(View):
    template_name = "logistics/conference_create.html"

    def get(self, request):
        form = ConferenceCreateForm()
        logged_entity = request.user.entity
        if Party.objects.filter(entity=logged_entity, role="carrier").exists():
            form.fields["destination"].initial = Party.objects.get(entity=logged_entity, role="carrier")
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        logged_entity = request.user.entity

        form = ConferenceCreateForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        creation_mode = form.cleaned_data["creation_mode"]
        cte_files = form.cleaned_data["cte_files"]
        nfe_files = form.cleaned_data["nfe_files"]
        origin = form.cleaned_data["origin"]
        destination = form.cleaned_data["destination"]
        event_type = form.cleaned_data["event_type"]
        access_keys = form.cleaned_data["access_keys"]

        try:
            with transaction.atomic():
                if creation_mode == "access_key":
                    conference_application_service = get_conference_application_service()
                    for key in access_keys:
                        conference_application_service.create_conference_by_access_key(
                            access_key=key,
                            origin=origin,
                            destination=destination,
                            event_type=event_type,
                            tenant=request.tenant,
                            user=request.user
                        )
            messages.success(request, "Conferência criada com sucesso.")
            return redirect("logistics:conference_list")

        except Exception as e:
            messages.error(request, str(e))
            return render(request, self.template_name, {"form": form})

class ConferenceListView(ListView):
    model = Conference
    context_object_name = "conferences"
    paginate_by = 10

    def get_queryset(self):
        return Conference.objects.filter(tenant=self.request.tenant).order_by("-created_at")

class ConferenceActionView(View):
    template_name = "logistics/conference_action.html"

    def get(self, request, conference_id):
        conference = Conference.objects.get(id=conference_id)
        return render(request, self.template_name, {"conference": conference})

class ConferenceAddPackageView(View):
    def post(self, request, conference_id):

        try:
            data = json.loads(request.body)
            package_code = data.get("package_code")
        except Exception:
            package_code = None

        if not package_code:
            return JsonResponse({"error": "package_code vazio"}, status=400)

        conference_application_service = get_conference_application_service()

        conference_application_service.add_package_to_conference(
            tenant=request.tenant,
            user=request.user,
            conference_id=conference_id,
            package_code=package_code,
            status="ok",
        )

        return JsonResponse({"status": "ok"})

class ConferenceRemovePackageView(View):
    def post(self, request, conference_id):
        conference_application_service = get_conference_application_service()
        data = json.loads(request.body)
        package_code = data.get("package_code")
        conference_application_service.remove_package_from_conference(
            tenant=request.tenant,
            conference_id=conference_id,
            package_code=package_code,
        )
        return JsonResponse({"status": "ok"})

class GetConferenceItemsView(View):
    def get(self, request, conference_id):
        conference_application_service = get_conference_application_service()
        conference_items = conference_application_service.get_conference_items(
            tenant=request.tenant,
            conference_id=conference_id,
        )
        result = [
            {
                "id": item.id,
                "package_code": item.package.tracking_code,
                "status": item.status
            }
            for item in conference_items
        ]

        return JsonResponse(result, safe=False)