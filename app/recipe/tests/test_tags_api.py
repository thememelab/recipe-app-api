""" Test for the tags API """

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal


from recipe.serializers import  TagsSerializer

from core.models import (Tag, Recipe )

TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    """Creata and return tag details url."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email="user@exmaple.com", password="testpass123"):
    """ Creat and return a user. """
    return get_user_model().objects.create_user(email=email, password=password)

class PublicTagApiTests(TestCase):
    """ test unauthenticated API requests."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ test auth is required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class privateTagsAPitest(TestCase):
    """test uthenticated API request. """
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123'
            )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_tags(self):
        """test retrieveing a list of tags"""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagsSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """ test liste of tags is limited to authenticated user """
        user2 = create_user(email="user@exmaple.com")
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name="Comfort Food")

        res = self.client.get(TAGS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK )
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """ test uodate a tag."""
        tag = Tag.objects.create(user=self.user, name='After Dinner')
        payload = {'name':'Dessert'}
        url = detail_url(tag.id)
        res = self.client.patch(url,payload)

        self. assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name,payload['name'])

    def test_delet_tag(self):
        """ Test deketing a tag. """
        tag = Tag.objects.create(user=self.user, name='Breakfast')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def filter_tags_assigned_to_recipes(self):
        """test liting tags to those assigned to recipes """

        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')

        recipe = Recipe.object.create(
            title='Green Eggs on Toast',
            time_minutes=10,
            price=Decimal('2.50'),
            user=self.user,
        )

        res = self.client.get(TAGS_URL, {'assigned_only' :1})

        s1 = TagsSerializer(tag1)
        s2 = TagsSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """ test filtred tags return a unique list"""
        tag = Tag.objects.create(user=self.user, name='Dinner')
        Tag.objects.create(user=self.user, name='Breakfast')

        recipe1 = Recipe.objects.create(
            title='Pancakes',
            time_minutes=5,
            price=Decimal('5.50'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Porridges',
            time_minutes=3,
            price=Decimal('2.00'),
            user=self.user,
        )

        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data),1)





