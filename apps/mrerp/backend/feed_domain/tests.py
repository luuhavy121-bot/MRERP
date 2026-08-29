import json

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from rest_framework.test import APITestCase

from people_domain.models import AuditEvent, Employee

from .models import Comment, Post


@override_settings(MEDIA_ROOT="test-media-feed")
class FeedApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", password="Test-only-1234!")

    def login_as(self, username):
        user = get_user_model().objects.get(username=username)
        self.client.force_authenticate(user)
        return user

    def create_post(self, **overrides):
        payload = {
            "content": "Thông tin vận hành hôm nay",
            "company_scope": "true",
            "employee_uuids": json.dumps([]),
            "team_uuids": json.dumps([]),
            "is_official": "false",
        }
        payload.update(overrides)
        return self.client.post("/api/v1/feed/posts/", payload, format="multipart")

    def test_active_staff_can_publish_company_post_and_other_staff_can_read(self):
        self.login_as("staff.demo")
        response = self.create_post()
        self.assertEqual(response.status_code, 201)
        self.login_as("other.demo")
        listed = self.client.get("/api/v1/feed/posts/")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.data["count"], 1)

    def test_team_post_does_not_leak_and_share_cannot_expand(self):
        staff = self.login_as("staff.demo")
        team_id = str(staff.employee_profile.team_id)
        post = self.create_post(company_scope="false", team_uuids=json.dumps([team_id])).data
        self.login_as("other.demo")
        self.assertEqual(self.client.get("/api/v1/feed/posts/").data["count"], 0)
        self.login_as("staff.demo")
        expanded = self.client.post(f"/api/v1/feed/posts/{post['uuid']}/share/", {"content": "share", "company_scope": True, "employee_uuids": [], "team_uuids": []}, format="json")
        self.assertEqual(expanded.status_code, 400)

    def test_author_can_manage_direct_post_without_being_in_its_audience(self):
        self.login_as("leader.demo")
        other = get_user_model().objects.get(username="other.demo").employee_profile
        post = self.create_post(
            company_scope="false",
            employee_uuids=json.dumps([str(other.pk)]),
        )
        self.assertEqual(post.status_code, 201)
        listed = self.client.get("/api/v1/feed/posts/")
        self.assertIn(post.data["uuid"], [str(item["uuid"]) for item in listed.data["results"]])

    def test_comment_reply_depth_reaction_uniqueness_and_soft_delete(self):
        self.login_as("staff.demo")
        post = self.create_post().data
        root = self.client.post(f"/api/v1/feed/posts/{post['uuid']}/comments/", {"content": "Bình luận"}, format="json").data
        reply = self.client.post(f"/api/v1/feed/posts/{post['uuid']}/comments/", {"content": "Trả lời", "parent_uuid": root["uuid"]}, format="json").data
        too_deep = self.client.post(f"/api/v1/feed/posts/{post['uuid']}/comments/", {"content": "Quá sâu", "parent_uuid": reply["uuid"]}, format="json")
        self.assertEqual(too_deep.status_code, 400)
        endpoint = f"/api/v1/feed/posts/{post['uuid']}/reaction/"
        self.assertEqual(self.client.put(endpoint, {"kind": "like"}, format="json").status_code, 200)
        self.assertEqual(self.client.put(endpoint, {"kind": "love"}, format="json").status_code, 200)
        self.assertEqual(Post.objects.get(pk=post["uuid"]).reactions.count(), 1)
        self.assertEqual(self.client.delete(f"/api/v1/feed/comments/{root['uuid']}/").status_code, 204)
        self.assertIsNotNone(Comment.objects.get(pk=root["uuid"]).deleted_at)

    def test_hr_can_publish_official_and_moderate_while_staff_cannot_mark_official(self):
        self.login_as("staff.demo")
        denied = self.create_post(is_official="true")
        self.assertEqual(denied.status_code, 403)
        self.login_as("hr.demo")
        post = self.create_post(is_official="true")
        self.assertEqual(post.status_code, 201)
        self.assertEqual(self.client.delete(f"/api/v1/feed/posts/{post.data['uuid']}/").status_code, 204)

    def test_attachment_validation_and_protected_download(self):
        self.login_as("staff.demo")
        upload = SimpleUploadedFile("tiny.png", b"\x89PNG\r\n\x1a\nvalid", content_type="image/png")
        response = self.create_post(content="", attachments=upload)
        self.assertEqual(response.status_code, 201)
        attachment = response.data["attachments"][0]
        self.assertEqual(self.client.get(attachment["download_url"]).status_code, 200)
        bad = SimpleUploadedFile("unsafe.svg", b"<svg></svg>", content_type="image/svg+xml")
        self.assertEqual(self.create_post(attachments=bad).status_code, 400)

    def test_inactive_employment_and_missing_capability_are_denied(self):
        user = self.login_as("staff.demo")
        user.employee_profile.employment_status = Employee.EmploymentStatus.PAUSED
        user.employee_profile.save(update_fields=["employment_status"])
        self.assertEqual(self.client.get("/api/v1/feed/posts/").status_code, 403)

        user.employee_profile.employment_status = Employee.EmploymentStatus.OFFICIAL
        user.employee_profile.save(update_fields=["employment_status"])
        user.groups.clear()
        self.assertEqual(self.client.get("/api/v1/feed/posts/").status_code, 403)

    def test_attachment_count_audience_projection_and_create_audit(self):
        self.login_as("staff.demo")
        too_many = [
            SimpleUploadedFile(f"note-{index}.txt", b"safe", content_type="text/plain")
            for index in range(6)
        ]
        self.assertEqual(self.create_post(attachments=too_many).status_code, 400)
        options = self.client.get("/api/v1/feed/audience-options/")
        self.assertEqual(options.status_code, 200)
        self.assertEqual(
            set(options.data["employees"][0]),
            {"uuid", "employee_code", "display_name", "team_uuid", "team_name"},
        )
        created = self.create_post()
        self.assertEqual(created.status_code, 201)
        audit = AuditEvent.objects.filter(action="feed.post.created", target_uuid=created.data["uuid"]).get()
        self.assertNotIn("content", audit.changes)

    def test_team_attachment_download_is_hidden_outside_audience(self):
        staff = self.login_as("staff.demo")
        upload = SimpleUploadedFile("note.txt", b"internal", content_type="text/plain")
        response = self.create_post(
            company_scope="false",
            team_uuids=json.dumps([str(staff.employee_profile.team_id)]),
            attachments=upload,
        )
        download_url = response.data["attachments"][0]["download_url"]
        self.login_as("other.demo")
        self.assertEqual(self.client.get(download_url).status_code, 404)
