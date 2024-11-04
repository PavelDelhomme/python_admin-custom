from django.db import models
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import ProjectSetting, User
from rest_framework import viewsets, status
from .serializers import DynamicFieldsModelSerializer
from django.contrib.admin.views.decorators import staff_member_required

from core.models import CustomUser
from .models import CustomChart
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404, redirect, render
from .forms import UserEditForm

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
    return render(request, 'admin_core/dashboard.html', context)

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
    return render(request, 'admin_core/manage_charts.html', context)


@login_required
def user_management_view(request):
    users = User.objects.all()
    context = {'users': users}
    return render(request, 'admin_core/user_management.html', context)

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
    return render(request, 'admin_core/edit_user.html', context)
