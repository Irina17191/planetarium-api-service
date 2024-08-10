from django.shortcuts import render
from rest_framework import viewsets

from planetarium.models import (
    PlanetariumDome,
    ShowTheme,
    AstronomyShow,
    ShowSession,
    Reservation,
    Ticket,
)

from planetarium.serializers import (
    PlanetariumDomeSerializer,
    ShowThemeSerializer,
    AstronomyShowSerializer,
    AstronomyShowListSerializer,
    AstronomyShowDetailSerializer,
    ShowSessionSerializer,
    ShowSessionDetailSerializer,
    ShowSessionListSerializer,
    ReservationSerializer,
    ReservationListSerializer,
)


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.prefetch_related("description")
    serializer_class = AstronomyShowSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        if self.action == "retrieve":
            return AstronomyShowDetailSerializer
        return self.serializer_class


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.select_related("astronomy_show", "planetarium_dome")
    serializer_class = ShowSessionSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionDetailSerializer
        return self.serializer_class


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.prefetch_related(
        "tickets__show_session__astronomy_show",
        "tickets__show_session__planetarium_dome",
    )
    serializer_class = ReservationSerializer

    # def get_queryset(self):
    #     if self.action == "retrieve":
    #         return Reservation.objects.prefetch_related("tickets")
    #     return self.queryset

    def get_queryset(self):
        return self.queryset.filter(user=self.queryset.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
