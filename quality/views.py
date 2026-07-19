from rest_framework import viewsets, permissions
from .models import QCControl, QCRun, NonConformance
from .serializers import QCControlSerializer, QCRunSerializer, NonConformanceSerializer

class QCControlViewSet(viewsets.ModelViewSet):
    queryset = QCControl.objects.all()
    serializer_class = QCControlSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

class QCRunViewSet(viewsets.ModelViewSet):
    queryset = QCRun.objects.all()
    serializer_class = QCRunSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

class NonConformanceViewSet(viewsets.ModelViewSet):
    queryset = NonConformance.objects.all()
    serializer_class = NonConformanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)
