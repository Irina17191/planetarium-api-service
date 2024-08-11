from datetime import datetime

from django.db.models import F, Count
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination

from planetarium.models import (
    PlanetariumDome,
    ShowTheme,
    AstronomyShow,
    ShowSession,
    Reservation,
    Ticket,
)
from planetarium.permissions import IsAdminAllOrIsAuthenticatedReadOnly

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
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.prefetch_related("description")
    serializer_class = AstronomyShowSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the AstronomyShow with filters"""
        title = self.request.query_params.get("title")
        show_themes = self.request.query_params.get("show_themes")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if show_themes:
            show_themes_ids = self._params_to_ints(show_themes)
            queryset = queryset.filter(description__id__in=show_themes_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        if self.action == "retrieve":
            return AstronomyShowDetailSerializer
        return self.serializer_class


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.select_related("astronomy_show", "planetarium_dome")
    serializer_class = ShowSessionSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        date = self.request.query_params.get("date")
        astronomy_show_id = self.request.query_params.get("astronomy_show")

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(show_time__date=date)

        if astronomy_show_id:
            queryset = queryset.filter(astronomy_show_id=int(astronomy_show_id))

        if self.action == "list":
            queryset = queryset.annotate(
                tickets_available=F("planetarium_dome__rows")
                * F("planetarium_dome__seats_in_row")
                - Count("tickets")
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionDetailSerializer
        return self.serializer_class


class ReservationPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.prefetch_related(
        "tickets__show_session__astronomy_show",
        "tickets__show_session__planetarium_dome",
    )
    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)
    http_method_names = ["get", "post"]

    # def get_queryset(self):
    #     if self.action == "retrieve":
    #         return Reservation.objects.prefetch_related("tickets")
    #     return self.queryset

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
