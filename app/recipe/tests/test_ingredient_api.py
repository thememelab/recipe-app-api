""" Test for the ingredients API """
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from decimal import Decimal

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (Ingredient, Recipe)
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """ create  amd return an ingredient details URL"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email="user@exmaple.com", password="testpass123"):
    """ Creat and return a user. """
    return get_user_model().objects.create_user(email=email, password=password)

class  PublicIngredienetsApiTest(TestCase):
    """test unauthenticated API resulsts."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ test uthenticated  is required for retrieving ingredienets."""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredienstApiTest(TestCase):
    """test unauthenticated PAI request."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """ Test retrieve a list of ingredienets"""
        Ingredient.objects.create(user=self.user, name='kale')
        Ingredient.objects.create(user=self.user, name='Vanilla')

        res  = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredienstr_limited_to_user(self):
        """test list of ingredienets is limites ti authenticated user."""
        user2 = create_user(email='úser@exmaple.com')
        ingredient =  Ingredient.objects.create(user=self.user, name='Pepper')
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """ testing aupdating and ingredienet """
        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')

        payload = {'name':'Coriander'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])
    
    def test_delete_ingredient(self):
        """ testingdeleting an ingredient """
        ingredient = Ingredient.objects.create(user=self.user, name='Lettuce')

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredient = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredient.exists())
    
    def test_filter_ingredienst_assigned_to_recipes(self):
        """test listing  ingredients to those assgine to recipes"""
        in1 = Ingredient.objects.create(user=self.user, name='Apples')
        in2 = Ingredient.objects.create(user=self.user, name='Turkey')

        recipe = Recipe.objects.create(
            title='Appe crumble',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.ingredients.add(in1)
        res = self.client.get(INGREDIENT_URL, {'assigned_only' :1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredents_unique(self):
        """test filtered ingredienets return a unique list."""
        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')

        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=60,
            price=Decimal('7.00'),
            user=self.user,
        )

        recipe2 = Recipe.objects.create(
            title='Herb Eggs',
            time_minutes=20,
            price=Decimal('4.00'),
            user=self.user,
        )

        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res  = self.client.get(INGREDIENT_URL, {'assigned_only':1})
        self.assertEqual(len(res.data),1)







    











