from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Mood(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=10, blank=True)  # np. emoji

    def __str__(self):
        return self.name

class DayEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='day_entries')
    date = models.DateField()
    mood = models.ForeignKey(Mood, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

class TodoItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos')
    day_entry = models.ForeignKey(DayEntry, on_delete=models.CASCADE, related_name='todos', null=True, blank=True)
    content = models.CharField(max_length=255)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return self.content

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        default='avatars/default-avatar-icon.jpg',
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.profile_picture or self.profile_picture.name == '':
            self.profile_picture = 'avatars/default-avatar-icon.jpg'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username