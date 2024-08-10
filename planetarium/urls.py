from django.urls import path, include
from rest_framework import routers

from planetarium.views import (
    PlanetariumDomeViewSet,
    ShowThemeViewSet,
    AstronomyShowViewSet,
)

router = routers.DefaultRouter()
router.register("planetarium_domes", PlanetariumDomeViewSet)
router.register("show_theme", ShowThemeViewSet)
router.register("astronomy_show", AstronomyShowViewSet)


urlpatterns = [path("", include(router.urls))]

app_name = "planetarium"
