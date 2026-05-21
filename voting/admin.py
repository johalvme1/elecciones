from django.contrib import admin
from .models import Section, Station, Party, Candidate, Vote

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_students')

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('user', 'section')

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'party')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'section', 'station', 'timestamp')
    list_filter = ('section', 'candidate')
    date_hierarchy = 'timestamp'
