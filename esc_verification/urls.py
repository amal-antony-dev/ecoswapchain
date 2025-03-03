from django.urls import path
from .views import EmailOtpCreateView, EmailOtpVerifyView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('create/',EmailOtpCreateView.as_view(), name='email-otp-create'),
    path('verify/', EmailOtpVerifyView.as_view(), name='email-otp-verify')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)