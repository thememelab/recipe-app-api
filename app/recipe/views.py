
# Create your views here.
""" View for the recipet Api's"""
from rest_framework import generics, permissions

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import ( mixins, viewsets, status)
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (Recipe, Tag, Ingredient)
from recipe import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
             OpenApiParameter(
                 'assigned_only',
            OpenApiTypes.INT,
            description='Filter by items assigne to recipes',
             ),
             OpenApiParameter(
            'ingredients',
            OpenApiTypes.STR,
            description='Comman seperated list of Ingredienst IDS to filter',
             )
         ]
        )
    )
class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                mixins.UpdateModelMixin,
                mixins.ListModelMixin,
                viewsets.GenericViewSet):
    """ baseview set for redipe attribute """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Filter queryset to authenticated user. """
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only',0))
        )

        queryset =  self.queryset

        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        return queryset.filter(user=self.request.user).order_by('-name').distinct()

class RecipeViewSet(viewsets.ModelViewSet):
    """ View for managing recipe APIS """
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def _params_to_ints(self,qs):
        """Converst a list of strings to integer."""
        return [ int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """ Retrive recipes from authenticated user."""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients:
            ingredients_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients_ids)

        return queryset.filter(user=self.request.user).order_by('-id').distinct()
    
    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        
        return self.serializer_class
    def perform_create(self,serializer):
        """Creata a new recipe """
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True,url_path='upload-image')
    def upload_image(self,request, pk=None):
        """ Upload an image to recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
class TagViewSet(BaseRecipeAttrViewSet):
    """manage tags in the database """
    serializer_class = serializers.TagsSerializer
    queryset = Tag.objects.all()
    
    
class IngredientViewSet(BaseRecipeAttrViewSet):
    """manage Ingredienst in the database """
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
   

    