from rest_framework import viewsets, permissions
from django.db.models import Q
from .models import Patient
from .serializers import PatientSerializer

from common.pagination import StandardResultsSetPagination

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
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
                    Q(first_name__icontains=word) |
                    Q(last_name__icontains=word) |
                    Q(phone_number__icontains=word)
                )
            queryset = queryset.filter(q_obj)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
