from datetime import datetime

from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.conf import settings
from django.db.models import Q


class PostManager(models.Manager):
    def list(self):
        return super().filter(draft=False)

    def search(self, text):
        return super().filter(
            Q(title__icontains=text) |
            Q(content__icontains=text) |
            Q(user__username__icontains=text)
        )


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    title = models.CharField(max_length=120)
    content = models.TextField()
    draft = models.BooleanField(default=False)
    slug = models.SlugField(unique=True)
    image = models.ImageField(null=True, blank=True, upload_to="img")
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    objects = PostManager()

    def get_absolute_path(self):
        return reverse("posts:detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("-timestamp",)


@receiver(pre_save, sender=Post)
def pre_save_slug(sender, instance, *args, **kwargs):
    slug = slugify(instance.title, allow_unicode=True)
    if instance.timestamp:
        num = int(instance.timestamp.timestamp())
    else:
        num = int(datetime.now().timestamp())
    instance.slug = "{}-{}".format(num, slug)
