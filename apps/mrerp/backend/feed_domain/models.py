import uuid

from django.conf import settings
from django.db import models

from people_domain.models import Employee, Team, TimeStampedModel


class Post(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="feed_posts")
    content = models.TextField(blank=True)
    company_scope = models.BooleanField(default=False)
    audience_employees = models.ManyToManyField(Employee, related_name="direct_feed_posts", blank=True)
    audience_teams = models.ManyToManyField(Team, related_name="feed_posts", blank=True)
    is_official = models.BooleanField(default=False)
    shared_from = models.ForeignKey("self", on_delete=models.PROTECT, related_name="shares", null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="deleted_feed_posts", null=True, blank=True)
    deletion_mode = models.CharField(max_length=16, blank=True)

    class Meta:
        ordering = ["-created_at"]
        permissions = [
            ("share_post", "Can share feed posts"),
            ("moderate_post", "Can moderate all feed content"),
            ("publish_official_post", "Can publish official company announcements"),
        ]


class PostAttachment(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="attachments")
    original_name = models.CharField(max_length=240)
    storage_key = models.CharField(max_length=300, unique=True)
    content_type = models.CharField(max_length=160)
    size = models.PositiveBigIntegerField()
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]


class Comment(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="feed_comments")
    parent = models.ForeignKey("self", on_delete=models.PROTECT, related_name="replies", null=True, blank=True)
    content = models.TextField()
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="deleted_feed_comments", null=True, blank=True)
    deletion_mode = models.CharField(max_length=16, blank=True)

    class Meta:
        ordering = ["created_at"]


class ReactionKind(models.TextChoices):
    LIKE = "like", "Like"
    LOVE = "love", "Love"
    CELEBRATE = "celebrate", "Celebrate"
    SUPPORT = "support", "Support"
    INSIGHTFUL = "insightful", "Insightful"


class PostReaction(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")
    actor = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="post_reactions")
    kind = models.CharField(max_length=16, choices=ReactionKind.choices)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["post", "actor"], name="unique_post_reaction_actor")]


class CommentReaction(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reactions")
    actor = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="comment_reactions")
    kind = models.CharField(max_length=16, choices=ReactionKind.choices)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["comment", "actor"], name="unique_comment_reaction_actor")]
