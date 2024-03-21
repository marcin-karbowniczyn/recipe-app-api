""" URL mappings for the recipe app """
from django.urls import path, include
from rest_framework.routers import DefaultRouter  # Vid. 81
from recipe import views

app_name = 'recipe'

router = DefaultRouter()
router.register('recipes', views.RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
