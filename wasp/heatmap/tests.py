from django.test import TestCase
from django.test import Client

# Create your tests here.
def test_heatmap(self):
  response = self.client.get('/heatmap')
  self.assertEqual(response.status_code, 200)
