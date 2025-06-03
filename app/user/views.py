""" View for the user apua"""

from rest_framework import generics,authentication,permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializer import (UserSerializer,AuhtTokenSerilzer)

class CreateUserView(generics.CreateAPIView):
    """ Create a new user in the systkem. """
    serializer_class = UserSerializer
    
class CreateTokenView(ObtainAuthToken):
    """ create a new auth token for user."""
    serializer_class = AuhtTokenSerilzer
    rendere_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user. """
    serializer_class = UserSerializer
    authentication_classes = [ authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    #permission_classes = [permissions.AllowAny]


    def get_object(self):
        """ Retirve and return the authetiated user."""
        return self.request.user

