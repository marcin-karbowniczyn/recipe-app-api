""" URL mappings for the user API """
# Remainder for me, that we use dot notation to have this code working inside Pycharm.
# In docker's container this would work as intented. App is there a root dir.
# from user import views

from django.urls import path
from . import views

# We specify this for the reverse() function to fins this url -> reverse(user:create)
app_name = 'user'

# We use as_view() because Django expects a function for this parameter, so we convert this class to function (oversimplified).
urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
]
