from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import viewsets
from graphene_django.types import DjangoObjectType
from graphene import ObjectType, String, Schema, List, Field
import graphene


class HealthCheckView(APIView):
    """View para verificar a saúde da aplicação."""
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'message': 'Django API está funcionando!',
            'version': '1.0.0'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
def api_root(request):
    """Endpoint raiz da API."""
    return Response({
        'message': 'Bem-vindo à API do Sistema',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'graphql': '/graphql/',
            'health': '/health/',
            'docs': '/api-auth/',
        }
    })


# GraphQL Types
class Query(ObjectType):
    hello = String(name=String(default_value="World"))
    
    def resolve_hello(self, info, name):
        return f'Hello {name}!'


schema = Schema(query=Query)