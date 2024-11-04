from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenericModelViewSet, ProjectSettingView, dashboard_view, edit_user_view, user_management_view, \
    manage_charts_view, edit_user_groups, reset_user_password, user_detail_view

router = DefaultRouter()
router.register(r'models/(?P<model>[^/.]+)', GenericModelViewSet, basename='model')
router.register(r'settings', ProjectSettingView, basename='projectsetting')

urlpatterns = [
    path('api/admin/', include(router.urls)),

    path('manage_charts/', manage_charts_view, name='manage_charts'),
    path('user_management/', user_management_view, name='user_management'),
    path('user_management/edit/<int:user_id>/', edit_user_view, name='edit_user'),
    path('user_management/edit/<int:user_id>/groups/', edit_user_groups, name='edit_user_groups'),
    path('user_management/edit/<int:user_id>/password/', reset_user_password, name='reset_user_password'),
    path('user_management/<int:user_id>/', user_detail_view, name='user_detail'),

    path('dashboard/', dashboard_view, name="dashboard"),
]
