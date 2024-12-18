"""
Contains tests for business logic associated with heatmap page.
"""
import os
import django
from django.test import TestCase, Client

# TODO: probably change to env variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'wasp.wasp.settings'

django.setup()

class HeatmapTests(TestCase):
    """_summary_

    Args:
        TestCase (_type_): _description_
    """

    def setUp(self):
        """Set up the test client before each test."""
        self.client = Client()

    def test_render(self):
        """Test if the heatmap page was successfully rendered."""
        response = self.client.get("/heatmap/")
        self.assertEqual(response.status_code, 200)
