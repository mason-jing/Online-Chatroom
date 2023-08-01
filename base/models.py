from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=900)

    # ! null controls the validation at the database level,
    # ! and blank is used during form field validation at the application level
    description = models.TextField(null=True, blank=True)

    # ! We already have a user model, so we need to define a related name for the host field
    # ! related_name is used to define the name of the reverse relation
    participants = models.ManyToManyField(User, related_name="participants", blank=True)

    # ! auto_now automatically set the field to now every time the object is saved,
    # ! auto_now_add automatically set the field to now when the object is first created
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # ! - means descending order
        ordering = ["-updated", "-created"]

    def __str__(self):
        return self.name


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # ! - means descending order
        ordering = ["-updated", "-created"]

    def __str__(self):
        return self.body[0:50]
