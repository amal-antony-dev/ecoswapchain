from django.urls import path
from .views import TraderRegistrationView, TraderLoginView, TraderRetrieveView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('register/', TraderRegistrationView.as_view(), name='trader-register'),
    path('login/', TraderLoginView.as_view(), name='trader-login'),
    path('retrieve/', TraderRetrieveView.as_view(), name="trader-retrieve"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)