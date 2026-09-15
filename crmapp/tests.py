from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Lead


class ExportViewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin",
            email="admin@example.com",
            password="secret123",
        )
        self.client.force_login(self.user)
        Lead.objects.create(
            name="Test Lead",
            phone="1234567890",
            email="lead@example.com",
            course="Python",
            source="Website",
            status="New",
            priority="High",
        )

    def test_export_urls_resolve(self):
        self.assertEqual(reverse("export_leads_csv"), "/exports/leads.csv")
        self.assertEqual(reverse("export_leads_xlsx"), "/exports/leads.xlsx")
        self.assertEqual(reverse("export_leads_pdf"), "/exports/leads.pdf")

    def test_export_views_return_files(self):
        csv_response = self.client.get(reverse("export_leads_csv"))
        self.assertEqual(csv_response.status_code, 200)
        self.assertIn("text/csv", csv_response["Content-Type"])

        xlsx_response = self.client.get(reverse("export_leads_xlsx"))
        self.assertEqual(xlsx_response.status_code, 200)
        self.assertIn("openxmlformats", xlsx_response["Content-Type"])

        pdf_response = self.client.get(reverse("export_leads_pdf"))
        self.assertEqual(pdf_response.status_code, 200)
        self.assertIn("application/pdf", pdf_response["Content-Type"])
