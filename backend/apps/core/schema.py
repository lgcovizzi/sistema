import graphene
from graphene_django.types import DjangoObjectType


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="World"))
    
    def resolve_hello(self, info, name):
        return f'Hello {name}!'


schema = graphene.Schema(query=Query)