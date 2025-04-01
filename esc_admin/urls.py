from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import AdminLoginView, HubCreateView, AdminHubListView, AdminRouteAddView, AdminRouteListView

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="admin-login"),
    path("hub/create/", HubCreateView.as_view(), name="hub-create"),
    path("hub/list/", AdminHubListView.as_view(), name="hub-list"),
    path("route/add/", AdminRouteAddView.as_view(), name="route-create"),
    path("route/list/", AdminRouteListView.as_view(), name="route-list")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
