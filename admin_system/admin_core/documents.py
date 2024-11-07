from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from core.models import CustomUser, UserProfile
from admin_core.models import ProjectSetting, CustomChart, Setting, LogEntry

# Define the index
user_index = Index('users')
profile_index = Index('user_profiles')
setting_index = Index('project_settings')
chart_index = Index('custom_charts')
log_index = Index('log_entries')

@user_index.doc_type
class UserDocument(Document):
    class Index:
        name = 'users'

    class Django:
        model = CustomUser
        fields = ['username', 'email', 'is_active', 'date_joined']

@profile_index.doc_type
class UserProfileDocument(Document):
    user = fields.ObjectField(properties={
        'username': fields.TextField(),
        'email': fields.TextField(),
    })

    class Django:
        model = UserProfile
        fields = ['bio', 'location', 'birth_date']


@setting_index.doc_type
class ProjectSettingDocument(Document):
    class Django:
        model = ProjectSetting
        fields = ['key', 'value', 'description']


@chart_index.doc_type
class CustomChartDocument(Document):
    created_by = fields.ObjectField(properties={
        'username': fields.TextField(),
        'email': fields.TextField(),
    })

    class Django:
        model = CustomChart
        fields = ['name', 'chart_type', 'data_source', 'created_at']

@log_index.doc_type
class LogEntryDocument(Document):
    user = fields.ObjectField(properties={
        'username': fields.TextField(),
        'email': fields.TextField(),
    })

    class Django:
        model = LogEntry
        fields = ['timestamp', 'level', 'message']