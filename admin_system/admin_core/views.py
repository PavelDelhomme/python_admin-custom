from datetime import timedelta

from django.conf import settings
from django.apps import apps
from django.core.management import call_command
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.db import models
from django.db.models import Count

from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth import login, logout
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404, redirect, render

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from .models import ProjectSetting, User, Setting, CustomChart, LogEntry
from .forms import UserEditForm, UserGroupForm, ChartCreateForm
from .serializers import DynamicFieldsModelSerializer

from core.models import CustomUser, VersionHistory


def get_app_label():
    """Dynamically get the current app label."""
    return settings.ROOT_URLCONF.split('.')[0]  # Adjust based on project structure if needed


@login_required
def get_fields(request):
    model_name = request.GET.get('model')
    app_label = get_app_label()
    model = apps.get_model(app_label, model_name)
    fields = [
        {'name': field.name, 'verbose_name': field.verbose_name}
        for field in model._meta.fields if field.get_internal_type() in ['IntegerField', 'FloatField']
    ]
    return JsonResponse({'fields': fields})


def custom_login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'admin_core/login/login.html', {'form': form})


def custom_logout_view(request):
    logout(request)
    return redirect('login')


@staff_member_required
def dashboard_view(request):
    user_count = CustomUser.objects.count()
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    user_stats = CustomUser.objects.values('role').annotate(count=Count('id'))

    # Préparer les données pour le graphique
    dataLabels = [stat['role'] for stat in user_stats]
    dataValues = [stat['count'] for stat in user_stats]

    context = {
        'user_count': user_count,
        'recent_users': recent_users,
        'dataLabels': dataLabels,
        'dataValues': dataValues,
    }
    return render(request, 'admin_core/dashboard/dashboard.html', context)


class GenericModelViewSet(viewsets.ModelViewSet):
    serializer_class = DynamicFieldsModelSerializer

    def get_queryset(self):
        model = self.kwargs['model']
        return model.objects.all()

    def get_serializer_class(self):
        model = self.kwargs['model']
        return type(f"{model.__name__}Serializer", (DynamicFieldsModelSerializer,),
                    {'Meta': type('Meta', (), {'model': model, 'fields': '__all__'})})


class ProjectSettingView(viewsets.ModelViewSet):
    queryset = ProjectSetting.objects.all()
    serializer_class = DynamicFieldsModelSerializer
    permission_classes = [IsAdminUser]

    def list(self, request):
        settings = {setting.key: setting.value for setting in ProjectSetting.objects.all()}
        return Response(settings)

    def create(self, request, *args, **kwargs):
        for key, value in request.data.items():
            setting, created = ProjectSetting.objects.get_or_create(key=key)
            setting.value = value
            setting.save()
        return Response({'status': 'Paramètres mis à jour avec succès'}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        key = request.data.get('key')
        value = request.data.get('value')
        if key:
            setting = ProjectSetting.objects.filter(key=key).first()
            if setting:
                setting.value = value
                setting.save()
                return Response({'status': f'Paramètre {key} mis à jour avec succès'})
            return Response({'error': 'Paramètre non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Clé non spécifiée'}, status=status.HTTP_400_BAD_REQUEST)


@login_required
def manage_charts_view(request):
    charts = CustomChart.objects.filter(created_by=request.user)
    context = {
        'charts': charts
    }
    return render(request, 'admin_core/charts/manage_charts.html', context)


@login_required
def user_management_view(request):
    visible_user_fields = Setting.get_visible_fields('CustomUser')
    users = CustomUser.objects.all()
    fields_to_display = [field for field in CustomUser._meta.fields if field.name in visible_user_fields]

    # Débogage : Affiche les noms des champs récupérés
    print("Champs à afficher : ", [field.name for field in fields_to_display])

    context = {
        'users': users,
        'fields_to_display': fields_to_display
    }
    return render(request, 'admin_core/users/user_management.html', context)


@staff_member_required
def user_detail_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_management')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'admin_core/users/user_detail.html', {
        'user': user,
        'form': form,
    })


@login_required
def edit_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_management')
    else:
        form = UserEditForm(instance=user)
    context = {'form': form, 'user': user}
    return render(request, 'admin_core/users/edit_user.html', context)


@staff_member_required
def edit_user_groups(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = UserGroupForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_management')
    else:
        form = UserGroupForm(instance=user)
    return render(request, 'admin_core/users/edit_user_groups.html', {'form': form, 'user': user})


@staff_member_required
def reset_user_password(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_management')
    else:
        form = PasswordChangeForm(user)
    return render(request, 'admin_core/users/reset_password.html', {'form': form, 'user': user})


@staff_member_required
def group_management_view(request):
    groups = Group.objects.all()
    if request.method == "POST":
        group_name = request.POST.get("group_name")
        if group_name:
            Group.objects.get_or_create(name=group_name)
        return redirect('group_management')
    return render(request, 'admin_core/groups/group_management.html', {'groups': groups})


@staff_member_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.delete()
    return redirect('group_management')


@staff_member_required
def group_detail_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    users = group.user_set.all()
    permissions = group.permissions.all()
    return render(request, 'admin_core/groups/group_detail.html', {
        'group': group,
        'users': users,
        'permissions': permissions,
    })


@staff_member_required
def general_settings_view(request):
    print("Appel de general_settings_view")
    """Vue pour afficher et modifier les paramètres généraux du projet."""

    # Charger les valeurs actuelles de `ProjectSetting` et utiliser les valeurs par défaut de `settings.py` si non définies
    project_settings = {
        "LANGUAGE_CODE": ProjectSetting.objects.filter(key="LANGUAGE_CODE").first() or settings.LANGUAGE_CODE,
        "TIME_ZONE": ProjectSetting.objects.filter(key="TIME_ZONE").first() or settings.TIME_ZONE,
        "DEBUG": ProjectSetting.objects.filter(key="DEBUG").first() or settings.DEBUG,
        "ALLOWED_HOSTS": ProjectSetting.objects.filter(key="ALLOWED_HOSTS").first() or ','.join(settings.ALLOWED_HOSTS),

        # Database settings
        "DB_ENGINE": ProjectSetting.objects.filter(key="DB_ENGINE").first() or settings.DATABASES['default']['ENGINE'],
        "DB_NAME": ProjectSetting.objects.filter(key="DB_NAME").first() or settings.DATABASES['default']['NAME'],
        "DB_USER": ProjectSetting.objects.filter(key="DB_USER").first() or settings.DATABASES['default']['USER'],
        "DB_PASSWORD": ProjectSetting.objects.filter(key="DB_PASSWORD").first() or settings.DATABASES['default'][
            'PASSWORD'],
        "DB_HOST": ProjectSetting.objects.filter(key="DB_HOST").first() or settings.DATABASES['default']['HOST'],
        "DB_PORT": ProjectSetting.objects.filter(key="DB_PORT").first() or settings.DATABASES['default']['PORT'],

        # JWT Settings
        "ACCESS_TOKEN_LIFETIME": ProjectSetting.objects.filter(key="ACCESS_TOKEN_LIFETIME").first() or
                                 settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        "REFRESH_TOKEN_LIFETIME": ProjectSetting.objects.filter(key="REFRESH_TOKEN_LIFETIME").first() or
                                  settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
        "ROTATE_REFRESH_TOKENS": ProjectSetting.objects.filter(key="ROTATE_REFRESH_TOKENS").first() or
                                 settings.SIMPLE_JWT['ROTATE_REFRESH_TOKENS'],
    }

    if request.method == "POST":
        settings_data = request.POST

        # Sauvegarder chaque setting dans ProjectSetting
        for key, value in settings_data.items():
            ProjectSetting.objects.update_or_create(
                key=key, defaults={"value": value}
            )

        # Recharger les paramètres dynamiques
        call_command("reload_settings")
        return redirect("general_settings")

    return render(request, "admin_core/settings/general_settings.html", {"settings": project_settings})



@staff_member_required
def field_visibility_view(request):
    """Affiche et gère la visibilité des champs des modèles."""
    print("Appel de field_visibility_view")
    models = apps.get_models()
    model_fields = {}

    for model in models:
        model_name = model.__name__
        fields = [
            {'name': field.name, 'verbose_name': field.verbose_name}
            for field in model._meta.fields
        ]
        visible_fields = Setting.get_visible_fields(model_name)
        model_fields[model_name] = {
            'fields': fields,
            'visible_fields': visible_fields
        }

    return render(request, 'admin_core/settings/field_visibility.html', {'model_fields': model_fields})


@staff_member_required
def settings_view(request):
    """Affiche et gère les paramètres généraux du projet."""
    print("Appel de settings_view")
    settings = ProjectSetting.objects.all()
    context = {
        'settings': settings,
    }
    return render(request, 'admin_core/settings/general_settings.html', context)


@staff_member_required
def manage_permissions_view(request):
    permissions = Permission.objects.all()
    groups = Group.objects.all()
    return render(request, 'admin_core/settings/manage_permissions.html',
                  {'permissions': permissions, 'groups': groups})


@staff_member_required
def manage_tokens_view(request):
    tokens = OutstandingToken.objects.all()
    if request.method == "POST":
        token_id = request.POST.get("token_id")
        token = get_object_or_404(OutstandingToken, id=token_id)
        BlacklistedToken.objects.get_or_create(token=token)
        token.blacklisted = True
        token.save()
    return render(request, 'admin_core/settings/manage_tokens.html', {'tokens': tokens})


@staff_member_required
def version_history_view(request, model_name, object_id):
    content_type = ContentType.objects.get(model=model_name.lower())
    versions = VersionHistory.objects.filter(content_type=content_type, object_id=object_id).order_by('-version')
    return render(request, 'admin_core/history/version_history.html',
                  {'versions': versions, 'model_name': model_name, 'object_id': object_id})


@login_required
def manage_chart_view(request):
    charts = CustomChart.objects.filter(created_by=request.user)
    models = apps.get_models()

    if request.method == 'POST':
        form = ChartCreateForm(request.POST)
        if form.is_valid():
            chart = form.save(commit=False)
            chart.created_by = request.user
            model_name = request.POST['model']
            field_name = request.POST['field']
            app_label = get_app_label()
            model = apps.get_model(app_label, model_name)
            data = list(model.objects.values_list(field_name, flat=True))

            # Format the data for Chart.js
            chart.data_source = {'labels': list(range(len(data))), 'datasets': [{'data': data}]}
            chart.save()
            return redirect('manage_charts')
    else:
        form = ChartCreateForm()

    return render(request, 'admin_core/charts/manage_charts.html', {
        'charts': charts,
        'form': form,
        'models': [{'name': model.__name__, 'verbose_name': model._meta.verbose_name} for model in models],
    })


@login_required
@staff_member_required
def bulk_user_action(request):
    if request.method == 'POST':
        user_ids = request.POST.getlist('selected_users')
        action = request.POST.get('action')
        group_id = request.POST.get('group_id')

        if action == 'delete':
            CustomUser.objects.filter(id__in=user_ids).delete()
            messages.success(request, "Selected users have been deleted.")
        elif action == 'add_to_group' and group_id:
            group = Group.objects.get(id=group_id)
            users = CustomUser.objects.filter(id__in=user_ids)
            for user in users:
                user.groups.add(group)
            messages.success(request, f"Selected users have been added to group {group.name}.")
        else:
            messages.error(request, "Invalid action or missing group.")
        return redirect('user_management')


@login_required
def get_fields(request):
    model_name = request.GET.get('model')
    model = apps.get_model('your_app_label', model_name)
    fields = [
        {'name': field.name, 'verbose_name': field.verbose_name}
        for field in model._meta.fields if field.get_internal_type() in ['IntegerField', 'FloatField']
    ]
    return JsonResponse({'fields': fields})


@staff_member_required
def update_visible_fields(request):
    if request.method == 'POST':
        models = apps.get_models()
        for model in models:
            model_name = model.__name__
            selected_fields = request.POST.getlist(f'{model_name}_fields')
            Setting.objects.update_or_create(
                key=f'{model_name}_visible_fields',
                defaults={'value': ','.join(selected_fields)}
            )
        messages.success(request, "Field visibility settings updated successfully.")
    return redirect('settings')


@staff_member_required
def manage_logs_view(request):
    logs = LogEntry.objects.order_by("-timestamp")
    paginator = Paginator(logs, 10)
    page_number = request.GET.get("page")
    page_logs = paginator.get_page(page_number)
    return render(request, 'admin_core/settings/manage_logs.html', {"logs": page_logs})
