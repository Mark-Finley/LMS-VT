from rest_framework import viewsets, permissions
from .models import Equipment, MaintenanceLog
from .serializers import EquipmentSerializer, MaintenanceLogSerializer

from django.db.models import Q
from common.pagination import StandardResultsSetPagination

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            words = search.split()
            q_obj = Q()
            for word in words:
                q_obj &= (
                    Q(name__icontains=word) |
                    Q(model__icontains=word) |
                    Q(serial_number__icontains=word) |
                    Q(manufacturer__icontains=word)
                )
            queryset = queryset.filter(q_obj)
        return queryset.order_by('name')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

class MaintenanceLogViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceLog.objects.all()
    serializer_class = MaintenanceLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)
