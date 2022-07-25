from django.test import TestCase
from django.test import Client

# Create your tests here.

class smokeTests(TestCase):
  def test_heatmap(self):
    c = Client()
    response = c.get('/heatmap/')
    self.assertEqual(response.status_code, 200)