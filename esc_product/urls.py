from django.urls import path
from .views import CategoryRetrieveView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("cat/get/all", CategoryRetrieveView.as_view(), name="retrieve-cat"),  # Create NFT
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)