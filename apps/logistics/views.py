from apps.entities.models import Party
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.views.generic import ListView
from .models import Conference, ConferenceItem
# from domain.schemas.conference_table import ConferenceTableSchema
from domain.bootstrap.service_container import get_conference_application_service, get_package_service
from .forms import ConferenceCreateForm
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDay
from datetime import datetime
from datetime import timedelta
import json
from apps.logistics.exceptions import PackageNotFoundError, PackageAlreadyReadError

class ConferenceCreateView(View):
    template_name = "logistics/conference_create.html"

    def get(self, request):
        form = ConferenceCreateForm()
        logged_entity = request.user.entity
        if Party.objects.filter(entity=logged_entity, role="carrier").exists():
            form.fields["destination"].initial = Party.objects.get(entity=logged_entity, role="carrier")
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ConferenceCreateForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        origin = form.cleaned_data["origin"]
        destination = form.cleaned_data["destination"]
        event_type = form.cleaned_data["event_type"]
        access_keys = form.cleaned_data["access_keys"]

        try:
            conference_application_service = get_conference_application_service()
            conference_application_service.create_conference_by_access_key(
                tenant=request.tenant,
                user=request.user,
                origin=origin,
                destination=destination,
                event_type=event_type,
                access_keys=access_keys,
            )

            messages.success(request, "Conferência criada com sucesso.")
            return redirect("logistics:conference_list")

        except Exception as e:
            messages.error(request, str(e))
            return render(request, self.template_name, {"form": form})

class ConferenceListView(ListView):
    model = Conference
    context_object_name = "conferences"
    paginate_by = 15

    def get_queryset(self): 
        return Conference.objects.filter(
            tenant=self.request.tenant
        ).filter(
            (
                Q(origin__entity=self.request.user.entity) & Q(mode="write")
            ) |
            (
                Q(origin__entity=self.request.user.entity) & Q(mode="read")
            ) |
            (
                Q(destination__entity=self.request.user.entity) & Q(mode="read")
            ) |
            (
                Q(destination__entity=self.request.user.entity) & Q(mode="write")
            )
        ).order_by("-created_at")

class ConferenceActionView(View):
    template_name = "logistics/conference_action.html"

    def get(self, request, conference_id):
        conference = Conference.objects.get(id=conference_id)
        conference.start_date = timezone.now()
        conference.started_by = request.user
        conference.save()
        
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
            status="pending",
        )

        return JsonResponse({"status": "pending"})

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

class FinishConferenceView(View):
    def post(self, request, conference_id):
        conference_application_service = get_conference_application_service()
        conference_application_service.finish_conference(
            tenant=request.tenant,
            conference_id=conference_id,
            user=request.user,
        )
        messages.success(request, "Conferência finalizada com sucesso.")
        return redirect("logistics:conference_list")

class ConferenceReadPackageView(View):
    def post(self, request, conference_id):
        conference_application_service = get_conference_application_service()
        data = json.loads(request.body)
        package_code = data.get("package_code")
        try:
            conference_application_service.read_package_from_conference(
                tenant=request.tenant,
                conference_id=conference_id,
                package_code=package_code,
                user=request.user,
            )
            return JsonResponse({"status": "ok"})
        except PackageNotFoundError as e:
            return JsonResponse({"status": "not_found", "message": str(e)}, status=400)
        except PackageAlreadyReadError as e:
            return JsonResponse({"status": "already_read", "message": str(e)}, status=400)


class AmountPackagesByDayView(View):

    def get(self, request):
        tenant = request.tenant

        try:
            days = int(request.GET.get("days", 30))
        except ValueError:
            return JsonResponse({"error": "Invalid days parameter"}, status=400)

        if days <= 0 or days > 365:
            return JsonResponse({"error": "Days must be between 1 and 365"}, status=400)

        today = timezone.now()
        start_date = today - timedelta(days=days)

        qs = (
            ConferenceItem.objects
            .filter(
                tenant=tenant,
                read_at__gte=start_date,
                read_at__lte=today,
                status="ok"
            )
            .annotate(day=TruncDay("read_at"))
            .values("day")
            .annotate(total=Count("id"))
            .order_by("day")
        )

        data_dict = {item["day"].date(): item["total"] for item in qs}

        labels = []
        data = []

        for i in range(days):
            day = (start_date + timedelta(days=i)).date()
            labels.append(day.strftime("%d/%m"))
            data.append(data_dict.get(day, 0))

        return JsonResponse({
            "labels": labels,
            "data": data,
            "days": days
        })