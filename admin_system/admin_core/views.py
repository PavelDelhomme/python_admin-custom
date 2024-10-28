from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import ProjectSetting
from rest_framework import viewsets, status
from .serializers import DynamicFieldsModelSerializer


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
