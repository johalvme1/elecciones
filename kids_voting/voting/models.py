from django.db import models
from django.contrib.auth.models import User

class Party(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='parties/')
    def __str__(self): return self.name

class Candidate(models.Model):
    name = models.CharField(max_length=150)
    photo = models.ImageField(upload_to='candidates/')
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    def __str__(self): return self.name

class Section(models.Model):
    name = models.CharField(max_length=100)
    total_students = models.IntegerField(default=0)
    def __str__(self): return self.name

class Station(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self): return self.user.username

class Vote(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.candidate.name} - {self.section.name}"
