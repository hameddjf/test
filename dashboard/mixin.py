from rest_framework import views
from orders.views import AddressCreateView, AddressDetailView

class DashboardAddressMixin:
    pass

class DashboardAddressCreateView(DashboardAddressMixin, AddressCreateView):
    pass

class DashboardAddressDetailView(DashboardAddressMixin, AddressDetailView):
    pass