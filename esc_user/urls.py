from django.urls import path
from .views import CheckUser, TokenUpdateView, LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('check/', CheckUser.as_view(), name='check-user'),
    path('token/update/', TokenUpdateView.as_view(), name="update-token"),
    path('logout/', LogoutView.as_view(), name="logout-view")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)