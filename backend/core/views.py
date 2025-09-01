from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .services import JWTService
from .serializers import UserSerializer, LoginSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Registro de novo usuário."""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = JWTService.generate_tokens(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login com email e senha."""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                tokens = JWTService.generate_tokens(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'tokens': tokens
                })
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """Renovação de access token."""
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({'error': 'Refresh token required'}, status=status.HTTP_400_BAD_REQUEST)
    
    result, error = JWTService.refresh_access_token(refresh_token)
    if error:
        return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout - adiciona tokens à blacklist."""
    access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    refresh_token = request.data.get('refresh')
    
    if access_token:
        JWTService.blacklist_token(access_token)
    
    if refresh_token:
        JWTService.blacklist_token(refresh_token)
    
    return Response({'message': 'Logged out successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Informações do usuário autenticado."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """Health check endpoint."""
    return Response({'status': 'healthy'})