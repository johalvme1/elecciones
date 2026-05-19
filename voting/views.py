from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.conf import settings
from .models import Candidate, Vote, Station, Section
from .forms import PartyForm, CandidateForm

@login_required
def home_view(request):
    return render(request, 'voting/home.html')

@login_required
def ballot_view(request):
    try:
        station = request.user.station
    except Station.DoesNotExist:
        if request.user.is_staff:
            return redirect('voting:dashboard')
        return render(request, 'voting/error.html', {'message': 'Este usuario no está configurado como una Estación de Votación.'})
        
    candidates = Candidate.objects.select_related('party').all()
    
    voto_ok = request.session.pop('voto_ok', False)

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        if candidate_id:
            try:
                candidate = Candidate.objects.get(id=candidate_id)
                Vote.objects.create(section=station.section, candidate=candidate)
                request.session['voto_ok'] = True
                return redirect('voting:ballot')
            except Candidate.DoesNotExist:
                messages.error(request, 'Candidato no válido.')

    return render(request, 'voting/ballot.html', {
        'candidates': candidates,
        'station': station,
        'voto_ok': voto_ok,
    })

def vote_count_api(request):
    total = Vote.objects.count()
    return JsonResponse({'total': total})

def resultados_login(request):
    if request.method == 'POST':
        pin = request.POST.get('pin', '')
        if pin == settings.RESULTS_PIN:
            request.session['results_access'] = True
            return redirect('voting:dashboard')
        messages.error(request, 'PIN incorrecto.')
    return render(request, 'voting/resultados_login.html')

def resultados_logout(request):
    request.session.pop('results_access', None)
    return redirect('voting:home')

def can_access_results(request):
    return request.user.is_staff or request.session.get('results_access', False)

def dashboard_view(request):
    if not can_access_results(request):
        return redirect('voting:resultados_login')
    sections = Section.objects.all()
    results = {}
    candidates = Candidate.objects.all()
    for section in sections:
        section_results = []
        for candidate in candidates:
            count = Vote.objects.filter(section=section, candidate=candidate).count()
            section_results.append({'candidate': candidate, 'count': count})
        results[section] = section_results
        
    global_results = Candidate.objects.annotate(total_votes=Count('vote')).order_by('-total_votes')
    
    return render(request, 'voting/dashboard.html', {
        'results': results,
        'global_results': global_results,
    })

@user_passes_test(lambda u: u.is_staff)
def add_party_view(request):
    if request.method == 'POST':
        form = PartyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Partido guardado exitosamente.')
            return redirect('voting:dashboard')
    else:
        form = PartyForm()
    return render(request, 'voting/add_form.html', {'form': form, 'title': 'Agregar Partido'})

@user_passes_test(lambda u: u.is_staff)
def add_candidate_view(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidato guardado exitosamente.')
            return redirect('voting:dashboard')
    else:
        form = CandidateForm()
    return render(request, 'voting/add_form.html', {'form': form, 'title': 'Agregar Candidato'})
