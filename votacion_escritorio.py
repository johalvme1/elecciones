import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import json, os, sys, datetime, math, shutil

# ─── CONFIG ─────────────────────────────────────────────────────────────────
def _base_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

BASE = _base_path()
MEDIA_DIR = os.path.join(BASE, 'media')
DATA_DIR = os.path.dirname(os.path.abspath(sys.executable)) if hasattr(sys, 'frozen') else os.path.dirname(os.path.abspath(__file__))
VOTOS_FILE = os.path.join(DATA_DIR, 'votos_escritorio.json')
CANDIDATOS_FILE = os.path.join(DATA_DIR, 'candidatos.json')
ADMIN_PASSWORD = "admin2026"

# ─── COLORES (web) ──────────────────────────────────────────────────────────
BG = "#0f172a"
GOLD = "#fbbf24"
WHITE = "#f8fafc"
MUTED = "#94a3b8"
INDIGO = "#818cf8"
GREEN = "#22c55e"
RED = "#ef4444"
CARD_BG = "rgba(255, 255, 255, 0.05)"
DARK_BORDER = "rgba(255,255,255,0.1)"

# ─── CANDIDATOS ─────────────────────────────────────────────────────────────
CANDIDATOS = []

def cargar_candidatos():
    global CANDIDATOS
    db_path = os.path.join(DATA_DIR, 'db.sqlite3')
    if os.path.exists(db_path):
        import sqlite3
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('''SELECT c.id, c.name, c.photo, p.name, p.logo
                         FROM voting_candidate c
                         JOIN voting_party p ON c.party_id = p.id
                         ORDER BY c.id''')
            rows = c.fetchall()
            conn.close()
            if rows:
                CANDIDATOS = [{'id':r[0],'name':r[1],'photo':r[2],'party':r[3],'party_logo':r[4]} for r in rows]
                guardar_candidatos_json()
                return
        except:
            pass
    if os.path.exists(CANDIDATOS_FILE):
        try:
            with open(CANDIDATOS_FILE, 'r', encoding='utf-8') as f:
                CANDIDATOS = json.load(f)
            return
        except:
            pass
    CANDIDATOS = [
        {'id':1,'name':'CAPI','photo':'candidates/CAPI_D3ZnCJ6.jpeg','party':'CAPI','party_logo':'parties/CAPI_8peSV75.jpeg'},
        {'id':2,'name':'ECO','photo':'candidates/ECO_pxjk8V1.jpeg','party':'ECO','party_logo':'parties/ECO_CUPlB5x.jpeg'},
        {'id':3,'name':'PARE','photo':'candidates/PARE_AzICpcS.jpeg','party':'PARE','party_logo':'parties/PARE_QrMd4kF.jpeg'},
        {'id':4,'name':'NEXO','photo':'candidates/NEXO_2eft13v.jpeg','party':'NEXO','party_logo':'parties/NEXO_krlVUMV.jpeg'},
        {'id':5,'name':'NULO','photo':'candidates/voto-nulo_ypzw3eM.jpg','party':'NULO','party_logo':'parties/voto-nulo_bwwZjdP.jpg'},
    ]
    guardar_candidatos_json()

def guardar_candidatos_json():
    with open(CANDIDATOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(CANDIDATOS, f, ensure_ascii=False, indent=2)

# ─── IMÁGENES ───────────────────────────────────────────────────────────────
_cache_fotos = {}

def cargar_imagen(ruta, size):
    key = (ruta, size)
    if key in _cache_fotos:
        return _cache_fotos[key]
    full = os.path.join(MEDIA_DIR, ruta) if os.path.dirname(ruta) else os.path.join(MEDIA_DIR, ruta)
    if not os.path.exists(full):
        placeholder = Image.new('RGBA', size, (26,26,46,255))
        _cache_fotos[key] = ImageTk.PhotoImage(placeholder)
        return _cache_fotos[key]
    try:
        img = Image.open(full).convert('RGBA')
        img.thumbnail(size, Image.LANCZOS)
        bg = Image.new('RGBA', size, (26,26,46,255))
        x = (size[0] - img.width) // 2
        y = (size[1] - img.height) // 2
        bg.paste(img, (x, y), img)
        _cache_fotos[key] = ImageTk.PhotoImage(bg)
    except:
        bg = Image.new('RGBA', size, (26,26,46,255))
        _cache_fotos[key] = ImageTk.PhotoImage(bg)
    return _cache_fotos[key]

# ─── VOTOS ──────────────────────────────────────────────────────────────────
def guardar_voto(candidato):
    votos = []
    if os.path.exists(VOTOS_FILE):
        try:
            with open(VOTOS_FILE, 'r', encoding='utf-8') as f:
                votos = json.load(f)
        except:
            votos = []
    votos.append({
        'candidato_id': candidato['id'],
        'candidato': candidato['name'],
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    with open(VOTOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(votos, f, indent=2, ensure_ascii=False)

def contar_votos():
    if not os.path.exists(VOTOS_FILE):
        return {}, 0
    try:
        with open(VOTOS_FILE, 'r', encoding='utf-8') as f:
            votos = json.load(f)
    except:
        return {}, 0
    conteo = {}
    for v in votos:
        nom = v.get('candidato', '?')
        conteo[nom] = conteo.get(nom, 0) + 1
    return conteo, len(votos)

def borrar_todos_votos():
    if os.path.exists(VOTOS_FILE):
        with open(VOTOS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

# ─── CLASE BASE ─────────────────────────────────────────────────────────────
class EleccionesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Elecciones Estudiantiles 2026")
        self.root.configure(bg=BG)
        try:
            self.root.state('zoomed')
        except:
            self.root.geometry("1200x800")
        self.root.focus_set()
        self._refs = []
        self.mostrar_inicio()

    def limpiar(self):
        for w in self.root.winfo_children():
            w.destroy()
        self._refs.clear()
        _cache_fotos.clear()

    def header(self, parent):
        h = tk.Frame(parent, bg="#0f172a", padx=20, pady=10)
        h.pack(fill=tk.X)

        logo_path = os.path.join(MEDIA_DIR, 'logoEscuela.jpg')
        if os.path.exists(logo_path):
            logo_img = cargar_imagen('logoEscuela.jpg', (80, 80))
            lbl = tk.Label(h, image=logo_img, bg="#0f172a")
            lbl.image = logo_img
            lbl.pack(side=tk.LEFT, padx=(0, 15))
            self._refs.append(logo_img)

        c = tk.Frame(h, bg="#0f172a")
        c.pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Label(c, text="ESCUELA JOAQUÍN L SANCHO QUESADA",
                 font=('Segoe UI', 18, 'bold'), fg=GOLD, bg="#0f172a",
                 anchor='center').pack()
        tk.Label(c, text="Elecciones Estudiantiles 2026",
                 font=('Segoe UI', 14), fg=INDIGO, bg="#0f172a",
                 anchor='center').pack()

        total_v = tk.Label(h, text="Votos: 0", font=('Segoe UI', 11),
                           fg=MUTED, bg="#0f172a")
        total_v.pack(side=tk.RIGHT, padx=(15,0))
        self._actualizar_votos_btn = total_v

        def refresh_votos():
            _, t = contar_votos()
            total_v.config(text=f"Votos: {t}")
            self.root.after(5000, refresh_votos)
        self.root.after(5000, refresh_votos)

        return h

    def floating_icons(self, parent):
        f = tk.Frame(parent, bg=BG, highlightthickness=0)
        f.place(relx=0, rely=0, relwidth=1, relheight=1)
        f.lower()
        for x, y, sym, delay in [
            (0.02, 0.10, "✓", 0), (0.01, 0.30, "🗳", 0.5),
            (0.03, 0.55, "✓", 1), (0.01, 0.75, "🗳", 1.5),
            (0.97, 0.15, "✓", 0.3), (0.98, 0.40, "🗳", 0.8),
            (0.97, 0.60, "✓", 1.2), (0.98, 0.85, "🗳", 1.8),
        ]:
            lbl = tk.Label(f, text=sym, font=('Segoe UI', 40),
                           fg=MUTED, bg=BG)
            lbl.place(relx=x, rely=y, anchor='center')

    def mostrar_inicio(self):
        self.limpiar()
        self.floating_icons(self.root)

        # Logo fondo
        logo_path = os.path.join(MEDIA_DIR, 'logoEscuela.jpg')
        if os.path.exists(logo_path):
            logo_img = cargar_imagen('logoEscuela.jpg', (600, 600))

        m = tk.Frame(self.root, bg=BG)
        m.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(m, text="ESCUELA JOAQUÍN L SANCHO QUESADA",
                 font=('Segoe UI', 28, 'bold'), fg=GOLD, bg=BG).pack()
        tk.Label(m, text="Elecciones Estudiantiles 2026",
                 font=('Segoe UI', 20), fg=INDIGO, bg=BG).pack(pady=(0, 40))

        _, total = contar_votos()
        self._votos_label = tk.Label(m, text=f"Votos Registrados: {total}",
                                      font=('Segoe UI', 14), fg=MUTED, bg=BG)
        self._votos_label.pack(pady=(0, 20))

        tk.Button(m, text="🗳  VOTAR",
                  font=('Segoe UI', 22, 'bold'), bg=GREEN, fg='white',
                  width=18, height=2, relief=tk.FLAT, bd=0, cursor='hand2',
                  command=self.mostrar_boleta).pack(pady=8)
        tk.Button(m, text="🔒  Resultados",
                  font=('Segoe UI', 22, 'bold'), bg='#1e293b', fg=GOLD,
                  width=18, height=2, relief=tk.FLAT, bd=0, cursor='hand2',
                  highlightbackground=GOLD, highlightthickness=1,
                  command=self.pedir_password_resultados).pack(pady=8)
        tk.Button(m, text="⚙  Administrar",
                  font=('Segoe UI', 14), bg='#1e293b', fg=MUTED,
                  width=14, height=1, relief=tk.FLAT, bd=0, cursor='hand2',
                  command=self.pedir_password_admin).pack(pady=(20, 0))

    def pedir_password_resultados(self):
        self._pedir_password("Resultados", self.mostrar_resultados)

    def pedir_password_admin(self):
        self._pedir_password("Administrar", self.mostrar_admin)

    def _pedir_password(self, titulo, callback):
        pw = tk.Toplevel(self.root, bg=BG)
        pw.title(titulo)
        pw.geometry("350x200")
        pw.transient(self.root)
        pw.grab_set()

        tk.Label(pw, text="Contraseña", font=('Segoe UI', 16, 'bold'),
                 fg=GOLD, bg=BG).pack(pady=20)
        entry = tk.Entry(pw, font=('Segoe UI', 14), show='*', width=20)
        entry.pack(pady=10)
        entry.focus_set()

        def verificar():
            if entry.get() == ADMIN_PASSWORD:
                pw.destroy()
                callback()
            else:
                messagebox.showerror("Error", "Contraseña incorrecta")
                pw.destroy()

        entry.bind('<Return>', lambda e: verificar())
        tk.Button(pw, text="Ingresar", font=('Segoe UI', 14, 'bold'),
                  bg=GREEN, fg='white', relief=tk.FLAT, width=12,
                  command=verificar).pack(pady=10)

    # ─── BOLETA ──────────────────────────────────────────────────────────────
    def mostrar_boleta(self):
        self.limpiar()
        self.floating_icons(self.root)
        h = self.header(self.root)

        content = tk.Frame(self.root, bg=BG)
        content.pack(expand=True, fill=tk.BOTH, padx=20)

        tk.Label(content, text="Papeleta de Votación",
                 font=('Segoe UI', 24, 'bold'), fg=WHITE, bg=BG).pack(pady=(20,5))
        tk.Label(content, text="Haz clic en la foto del candidato para votar",
                 font=('Segoe UI', 13), fg=MUTED, bg=BG).pack(pady=(0,15))

        row = tk.Frame(content, bg=BG)
        row.pack(expand=True)

        for c in CANDIDATOS:
            self._crear_tarjeta(row, c)

    def _crear_tarjeta(self, parent, candidato):
        wrap = tk.Frame(parent, bg=BG, padx=8, pady=5)
        wrap.pack(side=tk.LEFT)

        card = tk.Frame(wrap, bg="#1e293b", bd=0, highlightthickness=0,
                        cursor='hand2')
        card.pack()

        foto = cargar_imagen(candidato['photo'], (200, 220))
        lbl = tk.Label(card, image=foto, bg="#1a1a2e", bd=0)
        lbl.image = foto
        lbl.pack()

        card.bind('<Button-1>', lambda e, c=candidato: self._abrir_modal(c))
        lbl.bind('<Button-1>', lambda e, c=candidato: self._abrir_modal(c))

        def on_enter(e):
            card.configure(bg="#2d3a50")
        def on_leave(e):
            card.configure(bg="#1e293b")

        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)

        self._refs.append(foto)
        return wrap

    def _abrir_modal(self, candidato):
        modal = tk.Toplevel(self.root, bg=BG)
        modal.title("Confirmar Voto")
        modal.attributes('-fullscreen', True)
        modal.transient(self.root)
        modal.grab_set()
        modal.focus_set()
        modal.configure(bg=BG)

        overlay = tk.Frame(modal, bg=BG)
        overlay.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(overlay, text="¿Confirmas tu voto?",
                 font=('Segoe UI', 28, 'bold'), fg=GOLD, bg=BG).pack(pady=(0,15))

        foto = cargar_imagen(candidato['photo'], (300, 350))
        lbl_f = tk.Label(overlay, image=foto, bg="#0f172a", bd=0)
        lbl_f.image = foto
        lbl_f.pack(pady=5)

        if candidato.get('party_logo'):
            pimg = cargar_imagen(candidato['party_logo'], (80, 80))
            lbl_p = tk.Label(overlay, image=pimg, bg=BG)
            lbl_p.image = pimg
            lbl_p.pack(pady=3)

        tk.Label(overlay, text=candidato['name'],
                 font=('Segoe UI', 22, 'bold'), fg=WHITE, bg=BG).pack(pady=5)
        tk.Label(overlay, text=candidato['party'],
                 font=('Segoe UI', 16), fg=INDIGO, bg=BG).pack()

        btns = tk.Frame(overlay, bg=BG)
        btns.pack(pady=20)

        tk.Button(btns, text="✓  Confirmar Voto",
                  font=('Segoe UI', 18, 'bold'), bg=GREEN, fg='white',
                  width=14, height=2, relief=tk.FLAT, bd=0, cursor='hand2',
                  command=lambda: self._confirmar_voto(modal, candidato)
                  ).pack(side=tk.LEFT, padx=10)
        tk.Button(btns, text="✕  Cancelar",
                  font=('Segoe UI', 18, 'bold'), bg="rgba(255,255,255,0.1)",
                  fg=MUTED, width=14, height=2, relief=tk.FLAT, bd=0,
                  cursor='hand2',
                  command=modal.destroy).pack(side=tk.LEFT, padx=10)

    def _confirmar_voto(self, modal, candidato):
        guardar_voto(candidato)
        modal.destroy()
        self._mostrar_exito()

    def _mostrar_exito(self):
        exito = tk.Toplevel(self.root, bg=BG)
        exito.title("Voto Registrado")
        exito.attributes('-fullscreen', True)
        exito.transient(self.root)
        exito.grab_set()

        f = tk.Frame(exito, bg=BG)
        f.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(f, text="✓", font=('Segoe UI', 72), fg=GREEN, bg=BG).pack()
        tk.Label(f, text="¡Voto Registrado!",
                 font=('Segoe UI', 32, 'bold'), fg=GREEN, bg=BG).pack(pady=10)
        tk.Label(f, text="Gracias por participar",
                 font=('Segoe UI', 18), fg=MUTED, bg=BG).pack()

        def volver():
            exito.destroy()
            self.mostrar_inicio()

        exito.after(2000, volver)

    # ─── RESULTADOS ──────────────────────────────────────────────────────────
    def mostrar_resultados(self):
        self.limpiar()
        self.header(self.root)

        conteo, total = contar_votos()

        f = tk.Frame(self.root, bg=BG, padx=40, pady=20)
        f.pack(expand=True, fill=tk.BOTH)

        tk.Label(f, text="RESULTADOS", font=('Segoe UI', 26, 'bold'),
                 fg=WHITE, bg=BG).pack(pady=(0, 20))

        if total == 0:
            tk.Label(f, text="No hay votos registrados aún",
                     font=('Segoe UI', 18), fg=MUTED, bg=BG).pack(pady=40)
        else:
            cards = tk.Frame(f, bg=BG)
            cards.pack(pady=(0,20))

            for label, val, color in [
                ("Votaron", total, GREEN),
                ("Participación", f"{round(total/len(CANDIDATOS)*10,1)}%" if total > 0 else "0%", INDIGO)
            ]:
                box = tk.Frame(cards, bg="#1e293b", bd=1, relief=tk.SOLID,
                               highlightbackground=DARK_BORDER, padx=30, pady=15)
                box.pack(side=tk.LEFT, padx=10)
                tk.Label(box, text=label, font=('Segoe UI', 11), fg=MUTED,
                         bg="#1e293b").pack()
                tk.Label(box, text=str(val), font=('Segoe UI', 28, 'bold'),
                         fg=color, bg="#1e293b").pack()

            tbl = tk.Frame(f, bg="#1e293b", bd=1, relief=tk.SOLID,
                           highlightbackground=DARK_BORDER, padx=20, pady=15)
            tbl.pack(fill=tk.X, pady=10)

            max_v = max(conteo.values()) if conteo else 1
            for c in CANDIDATOS:
                nom = c['name']
                v = conteo.get(nom, 0)
                pct = round(v / total * 100, 1) if total > 0 else 0
                fila = tk.Frame(tbl, bg="#1e293b")
                fila.pack(fill=tk.X, pady=4)
                tk.Label(fila, text=nom, font=('Segoe UI', 14, 'bold'),
                         width=10, anchor='w', bg="#1e293b", fg=WHITE).pack(side=tk.LEFT)
                bar_bg = tk.Frame(fila, bg="#334155", height=28, width=250)
                bar_bg.pack(side=tk.LEFT, padx=10)
                bar_bg.pack_propagate(False)
                bar = tk.Frame(bar_bg, bg=GREEN, height=28,
                               width=int(250 * v / max_v))
                bar.pack(side=tk.LEFT)
                tk.Label(fila, text=f"{v} ({pct}%)", font=('Segoe UI', 14),
                         bg="#1e293b", fg=MUTED).pack(side=tk.LEFT)

        tk.Button(f, text="Volver al Inicio", font=('Segoe UI', 14, 'bold'),
                  bg=BG, fg=WHITE, relief=tk.FLAT, bd=0, cursor='hand2',
                  highlightbackground=MUTED, highlightthickness=1, width=18,
                  command=self.mostrar_inicio).pack(pady=20)

    # ─── ADMIN ────────────────────────────────────────────────────────────────
    def mostrar_admin(self):
        self.limpiar()
        self.header(self.root)

        f = tk.Frame(self.root, bg=BG, padx=40, pady=20)
        f.pack(expand=True, fill=tk.BOTH)

        tk.Label(f, text="Panel de Administración",
                 font=('Segoe UI', 26, 'bold'), fg=WHITE, bg=BG).pack(pady=(0,20))
        tk.Label(f, text="Configuración local (solo para pruebas)",
                 font=('Segoe UI', 13), fg=MUTED, bg=BG).pack(pady=(0,20))

        btns = tk.Frame(f, bg=BG)
        btns.pack()

        for texto, color, cmd in [
            ("🗑  Borrar todos los votos", RED, self._borrar_votos),
            ("🔄  Recargar candidatos desde DB", INDIGO, self._recargar_db),
            ("📋  Ver candidatos actuales", MUTED, self._ver_candidatos),
            ("🏠  Volver al Inicio", MUTED, self.mostrar_inicio),
        ]:
            tk.Button(btns, text=texto, font=('Segoe UI', 14, 'bold'),
                      bg="#1e293b", fg=color, width=28, height=2,
                      relief=tk.FLAT, bd=0, cursor='hand2',
                      highlightbackground=color, highlightthickness=1,
                      command=cmd).pack(pady=6)

    def _borrar_votos(self):
        if messagebox.askyesno("Confirmar", "¿Borrar todos los votos de prueba?"):
            borrar_todos_votos()
            messagebox.showinfo("OK", "Votos borrados")
            self.mostrar_admin()

    def _recargar_db(self):
        cargar_candidatos()
        messagebox.showinfo("OK", f"Candidatos recargados: {len(CANDIDATOS)}")
        self.mostrar_admin()

    def _ver_candidatos(self):
        info = "\n".join([f"  {c['id']}. {c['name']} ({c['party']})" for c in CANDIDATOS])
        messagebox.showinfo("Candidatos", f"Candidatos actuales:\n{info}")

# ─── MAIN ───────────────────────────────────────────────────────────────────
def main():
    cargar_candidatos()
    root = tk.Tk()
    app = EleccionesApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
