"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from graphene_django.views import GraphQLView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # REST API
    path('api/', include('apps.core.urls')),
    path('api/auth/token/', obtain_auth_token, name='api-token'),
    
    # GraphQL
    path('graphql/', GraphQLView.as_view(graphiql=settings.DEBUG)),
    
    # REST Framework Auth
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Debug Toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
