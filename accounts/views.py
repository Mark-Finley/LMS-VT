import jwt
import datetime
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import UserSerializer, UserWriteSerializer

User = get_user_model()

class IsAdministrator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or request.user.role == 'administrator'
        )

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def obtain_jwt_token(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }
        # JWT encode returning string
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        # Check type of token just in case (PyJWT returns string in newer versions, bytes in older)
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        return Response({
            'token': token,
            'user': UserSerializer(user).data
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


from django.db.models import Q
from common.pagination import StandardResultsSetPagination

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    pagination_class = StandardResultsSetPagination
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserWriteSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'me':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAdministrator()]

    def get_queryset(self):
        queryset = User.objects.all().order_by('username')
        
        search_query = self.request.query_params.get('search', '').strip()
        role_filter = self.request.query_params.get('role', '').strip()
        
        if role_filter:
            queryset = queryset.filter(role=role_filter)
            
        if search_query:
            words = search_query.split()
            q_objects = Q()
            for word in words:
                q_objects &= (
                    Q(username__icontains=word) |
                    Q(first_name__icontains=word) |
                    Q(last_name__icontains=word) |
                    Q(email__icontains=word)
                )
            queryset = queryset.filter(q_objects)
            
        return queryset

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)
        elif request.method in ['PUT', 'PATCH']:
            serializer = UserWriteSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(UserSerializer(user).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
