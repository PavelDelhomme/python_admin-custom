from core.models import CustomUser
user = CustomUser.objects.get(username="adminpavel")
user.delete()
exit()