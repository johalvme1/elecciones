#!/usr/bin/env python3
import os, sys, webbrowser, threading, time, shutil

def base_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def data_path():
    if hasattr(sys, 'frozen'):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

BASE = base_path()
DATA = data_path()
os.chdir(BASE)

def setup_database():
    import django
    from django.conf import settings
    from django.core.management import call_command

    call_command('makemigrations', 'voting', verbosity=0)
    call_command('migrate', verbosity=0)

    from django.contrib.auth.models import User
    from voting.models import Party, Candidate, Section, Station
    from django.core.files import File

    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@kids.local', 'admin')

    sec, _ = Section.objects.get_or_create(name='Preescolar', total_students=100)
    admin_user = User.objects.get(username='admin')
    Station.objects.get_or_create(section=sec, user=admin_user)

    # Unico usuario de votacion
    if not User.objects.filter(username='votante').exists():
        u = User.objects.create_user(username='votante', password='1234')
        Station.objects.get_or_create(section=sec, user=u)

    if Party.objects.count() == 0:
        media_dir = os.path.join(BASE, 'media')
        partidos_data = [
            ('CAPI', 'parties/CAPI_8peSV75.jpeg'),
            ('ECO', 'parties/ECO_CUPlB5x.jpeg'),
            ('PARE', 'parties/PARE_QrMd4kF.jpeg'),
            ('NEXO', 'parties/NEXO_krlVUMV.jpeg'),
            ('NULO', 'parties/voto-nulo_bwwZjdP.jpg'),
        ]
        candidatos_data = [
            ('CAPI', 'candidates/CAPI_D3ZnCJ6.jpeg', 'CAPI'),
            ('ECO', 'candidates/ECO_pxjk8V1.jpeg', 'ECO'),
            ('PARE', 'candidates/PARE_AzICpcS.jpeg', 'PARE'),
            ('NEXO', 'candidates/NEXO_2eft13v.jpeg', 'NEXO'),
            ('NULO', 'candidates/voto-nulo_ypzw3eM.jpg', 'NULO'),
        ]

        party_map = {}
        for pname, plogo in partidos_data:
            logo_path = os.path.join(media_dir, plogo)
            party = Party(name=pname)
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as f:
                    party.logo.save(os.path.basename(plogo), File(f))
            party.save()
            party_map[pname] = party

        for cname, cphoto, pname in candidatos_data:
            photo_path = os.path.join(media_dir, cphoto)
            candidate = Candidate(name=cname, party=party_map[pname])
            if os.path.exists(photo_path):
                with open(photo_path, 'rb') as f:
                    candidate.photo.save(os.path.basename(cphoto), File(f))
            candidate.save()

def copiar_media_a_data():
    """Copy media dir next to exe so Django can serve files from there"""
    src_media = os.path.join(BASE, 'media')
    dst_media = os.path.join(DATA, 'media')
    if not os.path.exists(dst_media) and os.path.exists(src_media):
        shutil.copytree(src_media, dst_media, ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))

def open_browser():
    time.sleep(2)
    webbrowser.open('http://localhost:8080')

def main():
    # Ensure stdout/stderr exist (for --windowed mode)
    if sys.stdout is None:
        sys.stdout = open(os.devnull, 'w')
    if sys.stderr is None:
        sys.stderr = open(os.devnull, 'w')

    # Django setup
    sys.path.insert(0, BASE)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    import django
    django.setup()

    # Override DB path to be next to exe
    from django.conf import settings
    settings.DATABASES['default']['NAME'] = os.path.join(DATA, 'db_kids.sqlite3')

    # Override MEDIA_ROOT to be next to exe
    settings.MEDIA_ROOT = os.path.join(DATA, 'media')

    # Fix paths (in PyInstaller, settings.py is at _MEIPASS/core/)
    settings.TEMPLATES[0]['DIRS'] = [os.path.join(BASE, 'templates')]
    settings.STATICFILES_DIRS = [os.path.join(BASE, 'static')]

    # Copy media out of bundle
    copiar_media_a_data()

    # Setup DB
    print("Configurando base de datos...")
    setup_database()
    print("¡Listo!")

    # Open browser
    threading.Thread(target=open_browser, daemon=True).start()

    print("\n" + "="*55)
    print("  🗳  VOTACIONES PREESCOLAR - ELE2026")
    print("  Abriendo navegador en http://localhost:8080")
    print("  Admin: http://localhost:8080/admin/")
    print("  Usuario: admin  |  Contraseña: admin")
    print("  Presiona Ctrl+C o cierra esta ventana para salir")
    print("="*55 + "\n")

    from django.core.management import execute_from_command_line
    execute_from_command_line([sys.argv[0], 'runserver', '8080', '--noreload'])

if __name__ == '__main__':
    main()
