import jwt
import datetime
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer

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
