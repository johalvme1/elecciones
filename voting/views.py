from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Case, When, Value, IntegerField
from django.http import JsonResponse
from .models import Candidate, Vote, Station, Section, VotoKinder

ORDEN = Case(
    When(id=1, then=Value(1)),  # CAPI
    When(id=2, then=Value(2)),  # ECO
    When(id=3, then=Value(3)),  # PARE
    When(id=4, then=Value(4)),  # NEXO
    When(id=5, then=Value(5)),  # NULO — último
    output_field=IntegerField(),
)
from .forms import PartyForm, CandidateForm

@login_required
def home_view(request):
    return render(request, 'voting/home.html')

@login_required
def ballot_view(request):
    try:
        station = request.user.station
    except Station.DoesNotExist:
        if request.user.is_superuser:
            return redirect('voting:dashboard')
        return render(request, 'voting/error.html', {'message': 'Este usuario no está configurado como una Estación de Votación.'})
        
    candidates = Candidate.objects.select_related('party').all().order_by(ORDEN)
    
    voto_ok = request.session.pop('voto_ok', False)

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        if candidate_id:
            try:
                candidate = Candidate.objects.get(id=candidate_id)
                Vote.objects.create(station=station, section=station.section, candidate=candidate)
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

def dashboard_view(request):
    if not request.user.is_superuser:
        return redirect('voting:home')
    sections = Section.objects.all()
    results = {}
    candidates = Candidate.objects.all().order_by(ORDEN)
    for section in sections:
        section_results = []
        for candidate in candidates:
            count = Vote.objects.filter(section=section, candidate=candidate).count()
            section_results.append({'candidate': candidate, 'count': count})
        results[section] = section_results

    stations = Station.objects.select_related('section', 'user').all()
    station_results = []
    for station in stations:
        station_votos = []
        for candidate in candidates:
            count = Vote.objects.filter(station=station, candidate=candidate).count()
            station_votos.append({'candidate': candidate, 'count': count})
        station_results.append({
            'usuario': station.user.username,
            'seccion': station.section.name,
            'votos': station_votos,
        })
        
    global_results = Candidate.objects.annotate(total_votes=Count('vote')).order_by(ORDEN)
    total_votos = Vote.objects.count()
    total_estudiantes = sum(s.total_students for s in sections)
    pendientes = max(0, total_estudiantes - total_votos)
    porcentaje = round((total_votos / total_estudiantes * 100), 1) if total_estudiantes > 0 else 0
    
    return render(request, 'voting/dashboard.html', {
        'results': results,
        'global_results': global_results,
        'station_results': station_results,
        'total_votos': total_votos,
        'total_estudiantes': total_estudiantes,
        'pendientes': pendientes,
        'porcentaje': porcentaje,
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

# ─── KINDER (sin PIN, directo) ──────────────────────────────────────────────

def kinder_ballot_view(request):
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        if candidate_id:
            try:
                candidate = Candidate.objects.get(id=candidate_id)
                VotoKinder.objects.create(
                    candidate=candidate,
                    session_key=request.session.session_key or 'anonymous'
                )
                return render(request, 'voting/kinder_exito.html')
            except Candidate.DoesNotExist:
                pass

    candidates = Candidate.objects.select_related('party').all().order_by(ORDEN)
    return render(request, 'voting/kinder_ballot.html', {'candidates': candidates})

@user_passes_test(lambda u: u.is_superuser)
def kinder_dashboard_view(request):
    total = VotoKinder.objects.count()
    resultados = Candidate.objects.annotate(
        total_kinder=Count('votokinder')
    ).order_by(ORDEN)
    return render(request, 'voting/kinder_dashboard.html', {
        'resultados': resultados,
        'total': total,
    })
