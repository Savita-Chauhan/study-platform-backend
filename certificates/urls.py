from django.urls import path
from .views import (
    GenerateCertificateView,
    DownloadCertificateView,
    MyCertificatesView
)

urlpatterns = [
    path('', MyCertificatesView.as_view(), name='my-certificates'),
    path('generate/', GenerateCertificateView.as_view(), name='generate-certificate'),
    path('download/<uuid:certificate_id>/', DownloadCertificateView.as_view(), name='download-certificate'),
]