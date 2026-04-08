import json
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import (Avg, Count, DurationField, ExpressionWrapper, F,
                              Max, Min, Q)
from django.db.models.functions import (TruncDate, TruncDay, TruncMonth,
                                        TruncWeek)
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView
from django.views.decorators.http import require_POST

from apps.entities.models import Party
from apps.logistics.exceptions import (PackageAlreadyReadError,
                                       PackageNotFoundError)
# from domain.schemas.conference_table import ConferenceTableSchema
from domain.bootstrap.service_container import (
    get_conference_application_service)

from .forms import ConferenceCreateForm
from .models import Conference, ConferenceItem, ConferenceSession


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
        conference_application_service = get_conference_application_service()
        conference = Conference.objects.get(id=conference_id)
        session = conference.sessions.filter(user=request.user).first()
        if not session:
            session = conference_application_service.start_conference(
                tenant=request.tenant,
                conference_id=conference_id,
                user=request.user,
            )
        
        return render(request, self.template_name, {"conference": conference, "session": session})

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
            status="finished",
        )

        return JsonResponse({"status": "finished"})

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
    def get(self, request, session_id):
        conference_application_service = get_conference_application_service()
        conference_items = conference_application_service.get_conference_items_by_session(
            tenant=request.tenant,
            session_id=session_id,
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
    def post(self, request, session_id):
        conference_application_service = get_conference_application_service()
        conference_application_service.finish_conference_by_session(
            tenant=request.tenant,
            session_id=session_id,
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

@require_POST
def conference_session_event(request, session_id):
    session = ConferenceSession.objects.get(id=session_id)
    data = json.loads(request.body)
    event_type = data.get("event_type")
    now = timezone.now()

    if event_type == "pause":
        if not session.paused and session.last_start:
            session.total_seconds += int((now - session.last_start).total_seconds())
            session.last_start = None
            session.paused = True

    elif event_type == "resume":
        if session.paused:
            session.last_start = now
            session.paused = False

    elif event_type == "finish":
        if not session.paused and session.last_start:
            session.total_seconds += int((now - session.last_start).total_seconds())
        session.last_start = None
        session.finished = True
        session.paused = True

    elif event_type == "heartbeat":
        pass

    session.save()

    return JsonResponse({
        "ok": True,
        "total_seconds": session.total_time_actual()
    })

@login_required
def dashboards(request):
    return render(request, "dashboards/index.html")
    
def _conference_total_seconds_from_sessions(conference):
    total = 0
    for session in conference.sessions.all():
        total += session.total_time_actual()
    return total


def _conference_total_seconds_finished(conference):
    total = 0
    for session in conference.sessions.all():
        total += session.total_seconds or 0
    return total

def _days_param(request, default=30):
    try:
        return int(request.GET.get("days", default))
    except (TypeError, ValueError):
        return default


def _date_range(days):
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days - 1)
    return start_date, end_date


def _seconds_from_duration(avg_duration):
    if not avg_duration:
        return 0
    return round(avg_duration.total_seconds(), 2)


def _party_label(party):
    return str(party) if party else "-"


def _user_label(user):
    return str(user) if user else "-"


def _conference_problem_type(conference):
    if conference.faulty_items > 0:
        return _("Faulty items")
    if conference.pending_items > 0:
        return _("Pending items")
    return _("Divergence without flagged item")


def _event_type_label(value):
    return dict(Conference.EVENT_TYPE_CHOICES).get(value, value)


def _conference_status_label(value):
    return dict(Conference.STATUS_CHOICES).get(value, value)


def _conference_item_status_label(value):
    return dict(ConferenceItem.STATUS_CHOICES).get(value, value)


@login_required
def conferences_in_progress(request):
    qs = (
        Conference.objects
        .filter(status="in_progress")
        .annotate(
            total_items=Count("items", distinct=True),
            read_items=Count("items", filter=Q(items__read_at__isnull=False), distinct=True),
        )
        .select_related("origin", "destination", "started_by")
        .prefetch_related("sessions")
        .order_by("start_date")
    )

    data = []

    for conference in qs:
        elapsed_seconds = _conference_total_seconds_from_sessions(conference)

        data.append({
            "id": conference.id,
            "origin": _party_label(conference.origin),
            "destination": _party_label(conference.destination),
            "started_by": _user_label(conference.started_by),
            "start_date": conference.start_date.strftime("%d/%m/%Y %H:%M") if conference.start_date else "-",
            "elapsed_seconds": elapsed_seconds,
            "read_items": conference.read_items,
            "total_items": conference.total_items,
            "event_type": conference.get_event_type_display(),
            "status": conference.get_status_display(),
            "document_type": conference.get_document_type_display(),
            "mode": conference.get_mode_display(),
        })

    return JsonResponse({"results": data})


@login_required
def average_conference_time(request):
    qs = (
        ConferenceSession.objects
        .filter(
            finished=True,
            conference__status="finished",
        )
        .select_related("conference", "conference__origin", "conference__destination", "user")
    )

    by_user = []
    user_qs = (
        qs.values("user__id", "user__username")
        .annotate(
            avg_seconds=Avg("total_seconds"),
            total=Count("id"),
        )
        .order_by("avg_seconds")
    )
    for row in user_qs:
        by_user.append({
            "label": row["user__username"] or _("No user"),
            "avg_seconds": round(row["avg_seconds"] or 0, 2),
            "total": row["total"],
        })

    by_event_type = []
    type_qs = (
        qs.values("conference__event_type")
        .annotate(
            avg_seconds=Avg("total_seconds"),
            total=Count("id"),
        )
        .order_by("avg_seconds")
    )
    for row in type_qs:
        by_event_type.append({
            "label": _event_type_label(row["conference__event_type"]),
            "avg_seconds": round(row["avg_seconds"] or 0, 2),
            "total": row["total"],
        })

    by_route = []
    route_qs = (
        qs.values("conference__origin__entity__name", "conference__destination__entity__name")
        .annotate(
            avg_seconds=Avg("total_seconds"),
            total=Count("id"),
        )
        .order_by("avg_seconds")[:20]
    )
    for row in route_qs:
        by_route.append({
            "label": f'{row["conference__origin__entity__name"]} → {row["conference__destination__entity__name"]}',
            "avg_seconds": round(row["avg_seconds"] or 0, 2),
            "total": row["total"],
        })

    return JsonResponse({
        "by_user": by_user,
        "by_event_type": by_event_type,
        "by_route": by_route,
    })


@login_required
def conferences_with_problem(request):
    qs = (
        Conference.objects
        .filter(has_problem=True)
        .annotate(
            total_items=Count("items", distinct=True),
            faulty_items=Count("items", filter=Q(items__status="faulty"), distinct=True),
            pending_items=Count("items", filter=Q(items__status="pending"), distinct=True),
            ok_items=Count("items", filter=Q(items__status="ok"), distinct=True),
        )
        .select_related("origin", "destination")
        .order_by("-created_at")
    )

    results = []
    for c in qs:
        total = c.total_items or 0
        error_rate = round((c.faulty_items / total) * 100, 2) if total else 0

        results.append({
            "id": c.id,
            "origin": _party_label(c.origin),
            "destination": _party_label(c.destination),
            "status": c.get_status_display(),
            "event_type": c.get_event_type_display(),
            "document_type": c.get_document_type_display(),
            "mode": c.get_mode_display(),
            "problem_type": _conference_problem_type(c),
            "faulty_items": c.faulty_items,
            "pending_items": c.pending_items,
            "ok_items": c.ok_items,
            "total_items": total,
            "error_rate": error_rate,
        })

    return JsonResponse({"results": results})


@login_required
def pending_items_by_conference(request):
    qs = (
        Conference.objects
        .annotate(
            total_items=Count("items", distinct=True),
            pending_items=Count("items", filter=Q(items__status="pending"), distinct=True),
            last_read_at=Max("items__read_at"),
        )
        .filter(pending_items__gt=0)
        .select_related("origin", "destination", "started_by")
        .order_by("-pending_items", "start_date")
    )

    results = []
    for c in qs:
        results.append({
            "id": c.id,
            "origin": _party_label(c.origin),
            "destination": _party_label(c.destination),
            "status": c.get_status_display(),
            "event_type": c.get_event_type_display(),
            "started_by": _user_label(c.started_by),
            "pending_items": c.pending_items,
            "total_items": c.total_items,
            "last_read_at": c.last_read_at.strftime("%d/%m/%Y %H:%M") if c.last_read_at else "-",
        })

    return JsonResponse({"results": results})


@login_required
def faulty_items_grouped(request):
    by_package = (
        ConferenceItem.objects
        .filter(status="faulty")
        .values("package__id")
        .annotate(
            total=Count("id"),
            label=Min("package__id"),
        )
        .order_by("-total")[:20]
    )

    by_origin = (
        ConferenceItem.objects
        .filter(status="faulty")
        .values("conference__origin__entity__name")
        .annotate(total=Count("id"))
        .order_by("-total")[:20]
    )

    by_destination = (
        ConferenceItem.objects
        .filter(status="faulty")
        .values("conference__destination__entity__name")
        .annotate(total=Count("id"))
        .order_by("-total")[:20]
    )

    return JsonResponse({
        "by_package": [
            {"label": _("Package #%(id)s") % {"id": row["package__id"]}, "total": row["total"]}
            for row in by_package
        ],
        "by_origin": [
            {"label": row["conference__origin__entity__name"], "total": row["total"]}
            for row in by_origin
        ],
        "by_destination": [
            {"label": row["conference__destination__entity__name"], "total": row["total"]}
            for row in by_destination
        ],
    })


@login_required
def error_rate_rankings(request):
    base = (
        Conference.objects
        .annotate(
            total_items=Count("items", distinct=True),
            faulty_items=Count("items", filter=Q(items__status="faulty"), distinct=True),
        )
        .filter(total_items__gt=0)
    )

    by_user = []
    user_qs = (
        base.values("started_by__username")
        .annotate(
            conferences=Count("id"),
            total_faulty=Count("items", filter=Q(items__status="faulty")),
            total_all=Count("items"),
        )
        .order_by("-total_faulty")
    )
    for row in user_qs:
        total_all = row["total_all"] or 0
        rate = round((row["total_faulty"] / total_all) * 100, 2) if total_all else 0
        by_user.append({
            "label": row["started_by__username"] or _("No user"),
            "conferences": row["conferences"],
            "error_rate": rate,
        })

    by_origin = []
    origin_qs = (
        base.values("origin__entity__name")
        .annotate(
            conferences=Count("id"),
            total_faulty=Count("items", filter=Q(items__status="faulty")),
            total_all=Count("items"),
        )
        .order_by("-total_faulty")
    )
    for row in origin_qs:
        total_all = row["total_all"] or 0
        rate = round((row["total_faulty"] / total_all) * 100, 2) if total_all else 0
        by_origin.append({
            "label": row["origin__entity__name"],
            "conferences": row["conferences"],
            "error_rate": rate,
        })

    by_destination = []
    destination_qs = (
        base.values("destination__entity__name")
        .annotate(
            conferences=Count("id"),
            total_faulty=Count("items", filter=Q(items__status="faulty")),
            total_all=Count("items"),
        )
        .order_by("-total_faulty")
    )
    for row in destination_qs:
        total_all = row["total_all"] or 0
        rate = round((row["total_faulty"] / total_all) * 100, 2) if total_all else 0
        by_destination.append({
            "label": row["destination__entity__name"],
            "conferences": row["conferences"],
            "error_rate": rate,
        })

    return JsonResponse({
        "by_user": by_user[:20],
        "by_origin": by_origin[:20],
        "by_destination": by_destination[:20],
    })


@login_required
def operator_performance(request):
    qs = (
        ConferenceSession.objects
        .filter(
            finished=True,
            conference__status="finished",
        )
        .values("user__username")
        .annotate(
            conferences=Count("conference", distinct=True),
            avg_seconds=Avg("total_seconds"),
            total_faulty=Count("conference__items", filter=Q(conference__items__status="faulty")),
            total_items=Count("conference__items"),
        )
        .order_by("-conferences")
    )
    print(qs)

    results = []
    for row in qs:
        total_items = row["total_items"] or 0
        error_rate = round((row["total_faulty"] / total_items) * 100, 2) if total_items else 0
        results.append({
            "operator": row["user__username"] or _("No user"),
            "conferences": row["conferences"],
            "avg_seconds": round(row["avg_seconds"] or 0, 2),
            "error_rate": error_rate,
        })

    return JsonResponse({"results": results})


@login_required
def volume_by_operation_type(request):
    days = _days_param(request, 30)
    start_date, end_date = _date_range(days)

    qs = (
        Conference.objects
        .filter(created_at__date__gte=start_date.date(), created_at__date__lte=end_date.date())
        .values("event_type")
        .annotate(total=Count("id"))
        .order_by("event_type")
    )

    labels = []
    data = []
    raw_labels = []

    for row in qs:
        raw_labels.append(row["event_type"])
        labels.append(_event_type_label(row["event_type"]))
        data.append(row["total"])

    return JsonResponse({
        "labels": labels,
        "raw_labels": raw_labels,
        "data": data,
        "days": days,
    })


@login_required
def conferences_by_period(request):
    days = _days_param(request, 90)
    period = request.GET.get("period", "day")

    start_date, end_date = _date_range(days)
    qs = Conference.objects.filter(created_at__gte=start_date, created_at__lte=end_date)

    if period == "week":
        trunc = TruncWeek("created_at")
        period_label = _("Week")
    elif period == "month":
        trunc = TruncMonth("created_at")
        period_label = _("Month")
    else:
        trunc = TruncDate("created_at")
        period_label = _("Day")

    grouped = (
        qs.annotate(period_ref=trunc)
        .values("period_ref")
        .annotate(total=Count("id"))
        .order_by("period_ref")
    )

    labels = []
    data = []

    for row in grouped:
        ref = row["period_ref"]
        if period == "month":
            label = ref.strftime("%m/%Y")
        elif period == "week":
            label = _("Week %(date)s") % {"date": ref.strftime("%d/%m")}
        else:
            label = ref.strftime("%d/%m")
        labels.append(label)
        data.append(row["total"])

    return JsonResponse({
        "labels": labels,
        "data": data,
        "period": period,
        "period_label": period_label,
        "days": days,
    })


@login_required
def derived_conferences(request):
    qs = (
        Conference.objects
        .filter(parent_conference__isnull=False)
        .select_related("parent_conference", "origin", "destination")
        .annotate(total_items=Count("items", distinct=True))
        .order_by("-created_at")[:50]
    )

    results = []
    for c in qs:
        results.append({
            "id": c.id,
            "parent_id": c.parent_conference_id,
            "origin": _party_label(c.origin),
            "destination": _party_label(c.destination),
            "event_type": c.get_event_type_display(),
            "status": c.get_status_display(),
            "total_items": c.total_items,
            "created_at": c.created_at.strftime("%d/%m/%Y %H:%M"),
        })

    return JsonResponse({"results": results})


@login_required
def problematic_suppliers(request):
    qs = (
        Conference.objects
        .annotate(
            total_items=Count("items", distinct=True),
            faulty_items=Count("items", filter=Q(items__status="faulty"), distinct=True),
        )
        .filter(total_items__gt=0)
        .values("origin__entity__name")
        .annotate(
            total_faulty=Count("items", filter=Q(items__status="faulty")),
            total_all=Count("items"),
            conferences=Count("id"),
        )
        .order_by("-total_faulty")
    )

    results = []
    for row in qs:
        total_all = row["total_all"] or 0
        faulty_rate = round((row["total_faulty"] / total_all) * 100, 2) if total_all else 0
        results.append({
            "supplier": row["origin__entity__name"],
            "conferences": row["conferences"],
            "faulty_rate": faulty_rate,
            "faulty_items": row["total_faulty"],
        })

    return JsonResponse({"results": results[:20]})


@login_required
def products_with_divergence(request):
    qs = (
        ConferenceItem.objects
        .filter(status="faulty")
        .values("package__id")
        .annotate(total_faulty=Count("id"))
        .order_by("-total_faulty")[:20]
    )

    return JsonResponse({
        "results": [
            {
                "package": _("Package #%(id)s") % {"id": row["package__id"]},
                "total_faulty": row["total_faulty"],
            }
            for row in qs
        ]
    })


@login_required
def idle_time_conferences(request):
    qs = (
        Conference.objects
        .filter(status="in_progress", start_date__isnull=False)
        .annotate(
            total_items=Count("items", distinct=True),
            unread_items=Count("items", filter=Q(items__read_at__isnull=True), distinct=True),
            last_read_at=Max("items__read_at"),
        )
        .select_related("origin", "destination", "started_by")
        .order_by("start_date")
    )

    now = timezone.now()
    results = []

    for c in qs:
        if c.last_read_at:
            idle_seconds = int((now - c.last_read_at).total_seconds())
        else:
            idle_seconds = int((now - c.start_date).total_seconds())

        results.append({
            "id": c.id,
            "origin": _party_label(c.origin),
            "destination": _party_label(c.destination),
            "started_by": _user_label(c.started_by),
            "status": c.get_status_display(),
            "event_type": c.get_event_type_display(),
            "unread_items": c.unread_items,
            "total_items": c.total_items,
            "last_read_at": c.last_read_at.strftime("%d/%m/%Y %H:%M") if c.last_read_at else "-",
            "idle_seconds": idle_seconds,
        })

    results.sort(key=lambda x: x["idle_seconds"], reverse=True)
    return JsonResponse({"results": results[:30]})


@login_required
def full_flow_load_unload(request):
    parents = (
        Conference.objects
        .filter(parent_conference__isnull=True)
        .prefetch_related("derived_conferences")
        .annotate(total_items=Count("items", distinct=True))
        .order_by("-created_at")[:50]
    )

    results = []
    for parent in parents:
        children = parent.derived_conferences.all()
        unloads = [c for c in children if c.event_type == "unload"]
        loads = [c for c in children if c.event_type == "load"]

        results.append({
            "parent_id": parent.id,
            "origin": _party_label(parent.origin),
            "destination": _party_label(parent.destination),
            "parent_event_type": parent.get_event_type_display(),
            "parent_status": parent.get_status_display(),
            "loads": len(loads),
            "unloads": len(unloads),
            "derived_total": len(children),
            "created_at": parent.created_at.strftime("%d/%m/%Y %H:%M"),
        })

    return JsonResponse({"results": results})


@login_required
def cancelled_conferences(request):
    qs = (
        Conference.objects
        .filter(status="cancelled")
        .select_related("origin", "destination", "created_by")
        .order_by("-created_at")[:100]
    )

    results = []
    for c in qs:
        results.append({
            "id": c.id,
            "origin": _party_label(c.origin),
            "destination": _party_label(c.destination),
            "status": c.get_status_display(),
            "created_by": _user_label(c.created_by),
            "created_at": c.created_at.strftime("%d/%m/%Y %H:%M"),
            "updated_at": c.updated_at.strftime("%d/%m/%Y %H:%M"),
        })

    return JsonResponse({"results": results})


@login_required
def conference_sla(request):
    qs = (
        Conference.objects
        .filter(status="finished")
        .select_related("origin", "destination")
        .prefetch_related("sessions")
        .order_by("-created_at")[:200]
    )

    results = []
    for c in qs:
        real_seconds = _conference_total_seconds_finished(c)
        expected_seconds = 1800 if c.event_type == "load" else 2700
        within_sla = real_seconds <= expected_seconds

        results.append({
            "id": c.id,
            "origin": _party_label(c.origin),
            "destination": _party_label(c.destination),
            "event_type": c.get_event_type_display(),
            "real_seconds": real_seconds,
            "expected_seconds": expected_seconds,
            "within_sla": within_sla,
            "within_sla_label": _("Within SLA") if within_sla else _("Out of SLA"),
        })

    return JsonResponse({"results": results})

@login_required
def full_audit(request):
    qs = (
        ConferenceItem.objects
        .filter(read_at__isnull=False)
        .select_related("conference", "package", "read_by", "conference__origin", "conference__destination")
        .order_by("-read_at")[:100]
    )

    results = []
    for item in qs:
        results.append({
            "conference_id": item.conference_id,
            "package_id": item.package_id,
            "package_label": _("Package #%(id)s") % {"id": item.package_id},
            "read_by": _user_label(item.read_by),
            "read_at": item.read_at.strftime("%d/%m/%Y %H:%M:%S") if item.read_at else "-",
            "status": item.get_status_display(),
            "origin": _party_label(item.conference.origin),
            "destination": _party_label(item.conference.destination),
        })

    return JsonResponse({"results": results})


@login_required
def errors_heatmap(request):
    qs = (
        ConferenceItem.objects
        .filter(status="faulty", read_at__isnull=False)
        .values(
            "read_at__hour",
            "read_by__username",
            "conference__origin__entity__name",
        )
        .annotate(total=Count("id"))
        .order_by("-total")[:100]
    )

    return JsonResponse({
        "results": [
            {
                "hour": row["read_at__hour"],
                "hour_label": _("%(hour)s h") % {"hour": row["read_at__hour"]},
                "operator": row["read_by__username"] or _("No user"),
                "origin": row["conference__origin__entity__name"],
                "total": row["total"],
            }
            for row in qs
        ]
    })