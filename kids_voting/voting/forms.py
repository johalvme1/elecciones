from django import forms
from .models import Party, Candidate

class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ['name', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'style': 'width: 100%; padding: 0.75rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.2); color: white; box-sizing:border-box;'}),
            'logo': forms.FileInput(attrs={'style': 'width: 100%; padding: 0.75rem; color: white;'}),
        }

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'photo', 'party']
        widgets = {
            'name': forms.TextInput(attrs={'style': 'width: 100%; padding: 0.75rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.2); color: white; box-sizing:border-box;'}),
            'photo': forms.FileInput(attrs={'style': 'width: 100%; padding: 0.75rem; color: white;'}),
            'party': forms.Select(attrs={'style': 'width: 100%; padding: 0.75rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.8); color: white; box-sizing:border-box;'}),
        }
