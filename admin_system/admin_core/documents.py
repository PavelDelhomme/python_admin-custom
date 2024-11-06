from django_elasticsearch_dsl import Document, Index
from django_elasticsearch_dsl.registries import registry
from .models import CustomUser

# Define the index
user_index = Index('users')

@user_index.doc_type
class UserDocument(Document):
    class Index:
        name = 'users'

    class Django:
        model = CustomUser
        fields = [
            'username',
            'email',
            # Ajouter d'autres champs à indexer
        ]
