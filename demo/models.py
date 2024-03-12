from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
# Create your models here.


class STATUS(models.TextChoices):
    DRAFT = "0", _("Draft")
    PUBLISH = "1", _("Publish")
    ARCHIVE = "2", _("Archive")
    


class Category(models.Model):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    author = models.ForeignKey(
        User, related_name="blog_post", on_delete=models.CASCADE)
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200)
    summary = models.CharField(max_length=200, null=True, blank=True)
    content = models.TextField()
    status = models.CharField(
        max_length=1, choices=STATUS.choices, default=STATUS.DRAFT)
    image = models.ImageField(upload_to="post", default="post/sample.jpg")
    category = models.ManyToManyField(Category, related_name="posts")
    views = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(
        User, related_name="comments", on_delete=models.CASCADE)
    text = models.TextField()
    approved_comment = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    update_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class Like(models.Model):
    user = models.ForeignKey(User, related_name="likes",
                             on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="likes",
                             on_delete=models.CASCADE)
