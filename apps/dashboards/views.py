from django.shortcuts import render
from django.views.generic import View

class DashboardsView(View):
    template_name = 'dashboards/dashboards.html'

    def get(self, request):
        print(request.tenant, self.template_name)
        return render(request, self.template_name)
    