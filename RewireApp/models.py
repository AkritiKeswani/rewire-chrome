"""
models.py
"""
from django.db import models
from django.contrib.auth.models import User
from unixtimestampfield.fields import UnixTimeStampField


class Participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    money = models.PositiveIntegerField(default=0, null=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    class Meta:
        ordering = ["-created"]


class FriendRequest(models.Model):
    sender = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="friend_request_sender"
    )
    receiver = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="friend_request_receiver"
    )

    def __str__(self):
        return f"{self.sender.full_name}/{self.receiver.full_name}"

    class Meta:
        unique_together = ("sender_id", "receiver_id")


class Friend(models.Model):
    sender = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="friend_sender"
    )
    receiver = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="friend_receiver"
    )

    def __str__(self):
        return f"{self.sender.full_name}/{self.receiver.full_name}"

    class Meta:
        unique_together = ("sender_id", "receiver_id")


class Blocklist(models.Model):
    user = models.ForeignKey(Participant, on_delete=models.CASCADE)
    website = models.CharField(null=False, max_length=1000)

    def __str__(self):
        return f"{self.user.full_name}-{self.website}"

    class Meta:
        unique_together = ("user", "website")


class Flow(models.Model):
    user = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="flow_user"
    )
    accountable_dude = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="accountable_dude"
    )
    start_time = UnixTimeStampField(null=False)
    end_time = UnixTimeStampField(null=False)
    money = models.PositiveIntegerField(default=0, null=False)
    success = models.BooleanField(null=False)

    def __str__(self):
        return f"{self.user.full_name}/{self.accountable_dude.full_name}"
