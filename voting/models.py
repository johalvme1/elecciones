from django.db import models
from django.contrib.auth.models import User

class Section(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre de Sección")
    total_students = models.IntegerField(default=0, verbose_name="Total de Estudiantes")
    
    def __str__(self):
        return self.name

class Station(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="station")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, verbose_name="Sección")
    
    def __str__(self):
        return f"Estación: {self.user.username} - {self.section.name}"

class Party(models.Model):
    name = models.CharField(max_length=100, verbose_name="Partido Político")
    logo = models.ImageField(upload_to='parties/', verbose_name="Logo del Partido")
    
    def __str__(self):
        return self.name

class Candidate(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nombre del Candidato")
    photo = models.ImageField(upload_to='candidates/', verbose_name="Foto del Candidato")
    party = models.ForeignKey(Party, on_delete=models.CASCADE, verbose_name="Partido")
    
    def __str__(self):
        return self.name

class Vote(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, null=True, blank=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Voto para {self.candidate.name} en {self.section.name}"

class PinKinder(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código PIN")
    used = models.BooleanField(default=False, verbose_name="Usado")
    def __str__(self):
        estado = "✓ usado" if self.used else "○ disponible"
        return f"{self.code} - {estado}"

class VotoKinder(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, verbose_name="Candidato")
    pin = models.CharField(max_length=20, verbose_name="PIN usado")
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Kinder: {self.candidate.name} (PIN: {self.pin})"
