from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenericModelViewSet, ProjectSettingView, dashboard_view, edit_user_view, user_management_view, \
    manage_charts_view, edit_user_groups, reset_user_password, user_detail_view, delete_group, manage_permissions_view, \
    group_management_view, settings_view, custom_login_view, custom_logout_view, version_history_view, \
    group_detail_view, manage_tokens_view, bulk_user_action, get_fields, update_visible_fields, general_settings_view, \
    field_visibility_view, manage_logs_view, list_routes_view, update_group_permissions, update_field_visibility, \
    jwt_and_db_settings_view

router = DefaultRouter()
router.register(r'models/(?P<model>[^/.]+)', GenericModelViewSet, basename='model')
router.register(r'settings', ProjectSettingView, basename='projectsetting')

urlpatterns = [
    path('api/admin/', include(router.urls)),
    path('api/get_fields/', get_fields, name='get_fields'),

    path('manage_charts/', manage_charts_view, name='manage_charts'),
    path('user_management/', user_management_view, name='user_management'),

    # User management URLs
    path('user_management/edit/<int:user_id>/', edit_user_view, name='edit_user'),
    path('user_management/edit/<int:user_id>/groups/', edit_user_groups, name='edit_user_groups'),
    path('user_management/edit/<int:user_id>/password/', reset_user_password, name='reset_user_password'),
    path('user_management/<int:user_id>/', user_detail_view, name='user_detail'),
    path('user_management/bulk_action/', bulk_user_action, name='bulk_user_action'),

    path("jwt_and_db_settings/", jwt_and_db_settings_view, name="jwt_and_db_settings"),

    # Group management URLs
    path('group_management/', group_management_view, name="group_management"),
    path('group_management/<int:group_id>/', group_detail_view, name="group_detail"),
    path('group_management/delete/<int:group_id>/', delete_group, name='delete_group'),

    # Settings URLs
    path("settings/", settings_view, name="settings"),  # Pour settings.html
    path("general_settings/", general_settings_view, name="general_settings"),  # Pour general_settings.html
    path("settings_visibility/", field_visibility_view, name="settings_visibility"),
    path('settings/update_visible_fields/', update_visible_fields, name='update_visible_fields'),
    path('permissions/', manage_permissions_view, name="manage_permissions"),
    path('update_group_permissions/<int:group_id>/', update_group_permissions, name='update_group_permissions'),
    path('update_field_visibility/', update_field_visibility, name='update_field_visibility'),

    path('manage_tokens/', manage_tokens_view, name="manage_tokens"),
    path('<str:model_name>/<int:object_id>/versions/', version_history_view, name='version_history'),
    path('manage_logs/', manage_logs_view, name="manage_logs"),
    path('list_routes/', list_routes_view, name="list_routes"),  # Ajout pour afficher les routes

    # Dashboard, login, and logout
    path('dashboard/', dashboard_view, name="dashboard"),
    path("login/", custom_login_view, name="login"),
    path("logout/", custom_logout_view, name="logout"),
]
