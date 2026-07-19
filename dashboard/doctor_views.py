from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from requests.models import TestRequest, RequestedTest
from requests.serializers import TestRequestSerializer
from test_catalogue.models import Test
from encounters.models import Encounter

class DoctorRequestListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Limit access to Doctor users
        if request.user.role != 'doctor' and request.user.role != 'administrator':
            return Response(
                {"detail": "Access restricted to doctors only."},
                status=status.HTTP_403_FORBIDDEN
            )
        # Filter requests where ordered by this user, or where referring doctor's name matches
        name_match = f"{request.user.first_name} {request.user.last_name}".strip()
        requests = TestRequest.objects.filter(
            models.Q(ordered_by=request.user) |
            models.Q(encounter__referring_physician__icontains=name_match)
        ).distinct()
        serializer = TestRequestSerializer(requests, many=True)
        return Response(serializer.data)

from django.db import models

class DoctorCreateRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.role != 'doctor' and request.user.role != 'administrator':
            return Response(
                {"detail": "Access restricted to doctors only."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        encounter_id = request.data.get('encounter')
        test_ids = request.data.get('test_ids', [])
        priority = request.data.get('priority', 'routine')

        if not encounter_id:
            return Response(
                {"detail": "Encounter field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not test_ids:
            return Response(
                {"detail": "Please select at least one test."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            encounter = Encounter.objects.get(id=encounter_id)
        except Encounter.DoesNotExist:
            return Response(
                {"detail": "Invalid encounter ID."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create Test Request
        test_request = TestRequest.objects.create(
            encounter=encounter,
            priority=priority,
            ordered_by=request.user
        )

        for tid in test_ids:
            try:
                test_obj = Test.objects.get(id=tid)
                RequestedTest.objects.create(
                    request=test_request,
                    test=test_obj,
                    status='pending_payment' # default workflow
                )
            except Test.DoesNotExist:
                continue

        serializer = TestRequestSerializer(test_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
