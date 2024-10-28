from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenericModelViewSet, ProjectSettingView


router = DefaultRouter()
router.register(r'models/(?p<model>[^/.]+)', GenericModelViewSet, basename='model')


urlpatterns = [
   path('api/admin/', include(router.urls)),
   path('api/admin/settings/', ProjectSettingView.as_view(), name='project-settings'),
]



