import json
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from people_domain.models import Team

from .models import Document


class DocumentApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", password="Local-Demo-1234!")
        cls.alpha = Team.objects.get(code="ALPHA")

    def setUp(self):
        self.client = APIClient()
        self.media = tempfile.TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.media.name)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        self.media.cleanup()

    def login(self, username):
        self.assertTrue(self.client.login(username=username, password="Local-Demo-1234!"))

    def _create_team_document(self):
        self.login("leader.demo")
        response = self.client.post("/api/v1/documents/documents/", {
            "title": "Hướng dẫn Team Alpha",
            "description": "Tài liệu vận hành",
            "category": "Hướng dẫn",
            "scope": "teams",
            "team_uuids": json.dumps([str(self.alpha.pk)]),
            "employee_uuids": "[]",
            "note": "Bản đầu",
            "attachments": SimpleUploadedFile("guide.txt", b"hello team", content_type="text/plain"),
        }, format="multipart")
        self.assertEqual(response.status_code, 201, response.data)
        return response

    def test_team_audience_and_protected_download(self):
        created = self._create_team_document()
        file_uuid = created.data["versions"][0]["files"][0]["uuid"]
        self.client.logout()
        self.login("staff.demo")
        self.assertEqual(self.client.get("/api/v1/documents/documents/").data["count"], 1)
        download = self.client.get(f"/api/v1/documents/files/{file_uuid}/download/")
        self.assertEqual(download.status_code, 200)
        download.close()
        self.client.logout()
        self.login("other.demo")
        self.assertEqual(self.client.get("/api/v1/documents/documents/").data["count"], 0)
        self.assertEqual(self.client.get(f"/api/v1/documents/files/{file_uuid}/download/").status_code, 403)

    def test_staff_cannot_upload_and_owner_can_archive_restore(self):
        created = self._create_team_document()
        uuid = created.data["uuid"]
        archived = self.client.post(f"/api/v1/documents/documents/{uuid}/archive/")
        self.assertEqual(archived.status_code, 200)
        self.assertTrue(archived.data["is_archived"])
        restored = self.client.post(f"/api/v1/documents/documents/{uuid}/restore/")
        self.assertEqual(restored.status_code, 200)
        self.assertFalse(restored.data["is_archived"])
        self.client.logout()
        self.login("staff.demo")
        denied = self.client.post("/api/v1/documents/documents/", {
            "title": "Không được phép", "scope": "company",
            "attachments": SimpleUploadedFile("x.txt", b"x", content_type="text/plain"),
        }, format="multipart")
        self.assertEqual(denied.status_code, 403)

    def test_ceo_company_read_capability_includes_team_documents(self):
        created = self._create_team_document()
        self.client.logout()
        self.login("ceo.demo")
        response = self.client.get("/api/v1/documents/documents/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(created.data["uuid"], [item["uuid"] for item in response.data["results"]])
