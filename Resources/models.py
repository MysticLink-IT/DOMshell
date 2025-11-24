from django.db import models

# Create your models here.
osProfiles = [
    ("windows","Windows NT"),
    ("debian","Debian Linux"),
    ("redhat","RedHat Linux"),
    ]

class Computer(models.Model):
    osProfile = models.CharField(max_length=32, choices=osProfiles)
    hostname = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hostname
