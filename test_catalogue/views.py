from rest_framework import viewsets, permissions
from .models import Test, TestCategory, TestParameter
from .serializers import TestSerializer, TestCategorySerializer, TestParameterSerializer

class TestCategoryViewSet(viewsets.ModelViewSet):
    queryset = TestCategory.objects.all()
    serializer_class = TestCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

from django.db.models import Q
from common.pagination import StandardResultsSetPagination

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
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
                    Q(code__icontains=word)
                )
            queryset = queryset.filter(q_obj)
        return queryset.order_by('name')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class TestParameterViewSet(viewsets.ModelViewSet):
    queryset = TestParameter.objects.all()
    serializer_class = TestParameterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
