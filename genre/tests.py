from django.test import TestCase
from genre.models import Genre

# Create your tests here.
class GenreModelTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name='Fiction')

    def test_genre_creation(self):
        self.assertEqual(self.genre.name, 'Fiction')
        self.assertTrue(isinstance(self.genre, Genre))

    def test_genre_delection(self):
        self.genre.delete()
        self.assertEqual(Genre.objects.count(), 0)