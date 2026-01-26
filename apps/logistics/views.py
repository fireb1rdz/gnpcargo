from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction

from .forms import ConferenceCreateForm
from .services import ConferenceService


class ConferenceCreateView(View):
    template_name = "logistics/conference/create.html"

    def get(self, request):
        form = ConferenceCreateForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        logged_entity = request.user.entity

        form = ConferenceCreateForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        creation_mode = form.cleaned_data["creation_mode"]
        cte_files = form.cleaned_data["cte_files"]

        try:
            with transaction.atomic():
                if creation_mode == "cte":
                    ConferenceService.create_from_cte(
                        tenant=request.tenant,
                        user=request.user,
                        carrier_entity=logged_entity,
                        cte_files=cte_files,
                    )
                else:
                    ConferenceService.create_manual(
                        tenant=request.tenant,
                        user=request.user,
                        carrier_entity=logged_entity,
                        document_type=form.cleaned_data["document_type"],
                        document_number=form.cleaned_data["document_number"],
                    )

            messages.success(request, "Conferência criada com sucesso.")
            return redirect("conference:list")

        except Exception as e:
            messages.error(request, str(e))
            return render(request, self.template_name, {"form": form})
