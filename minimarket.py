from flask import Flask, render_template_string, redirect, url_for, request, session, flash
from functools import wraps
import uuid
import json
import os

app = Flask(__name__)
app.secret_key = 'clave_minimarket_2026'

# ------------------------------------------------------------
# PERSISTENCIA DE USUARIOS (JSON)
# ------------------------------------------------------------
USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    default_users = {
        "admin":   {"password": "admin123",   "role": "admin",   "email": "admin@minimarket.com"},
        "cliente": {"password": "cliente123", "role": "cliente", "email": "cliente@minimarket.com"},
    }
    save_users(default_users)
    return default_users

def save_users(users_dict):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_dict, f, indent=4, ensure_ascii=False)

USERS = load_users()

# ------------------------------------------------------------
# PRODUCTOS (en memoria)
# ------------------------------------------------------------
PRODUCTOS = [
    {"id": 1, "nombre": "Galleta soda",      "peso": "6 und (222 gr)", "precio": 3.30,
     "img": "https://plazavea.vteximg.com.br/arquivos/ids/25835356-1000-1000/502139.jpg",
     "stock": 100, "categoria": "Galletas"},
    {"id": 2, "nombre": "Coca Cola",          "peso": "500 ml",         "precio": 3.50,
     "img": "https://yopo.pe/wp-content/uploads/2023/12/COCA-500-ORIGINAL-RAPPI.jpg",
     "stock": 80,  "categoria": "Bebidas"},
    {"id": 3, "nombre": "Leche Gloria",       "peso": "390 gr",         "precio": 4.20,
     "img": "https://www.gloria.com.pe/images/lataa.png",
     "stock": 60,  "categoria": "Lácteos"},
    {"id": 4, "nombre": "Yogurt Laive",       "peso": "1000 gr",        "precio": 6.50,
     "img": "https://wongfood.vtexassets.com/arquivos/ids/809652-1200-auto?v=639023674094630000&width=1200&height=auto&aspect=true",
     "stock": 40,  "categoria": "Lácteos"},
    {"id": 5, "nombre": "Pan en bolsa",       "peso": "500 gr",         "precio": 8.50,
     "img": "https://media.istockphoto.com/id/518733512/es/foto/pan-en-bolsa-de-pl%C3%A1stico.jpg?s=612x612&w=0&k=20&c=UPaAZgdhKw7Rq-1KMJtAHLEl4ioz8Q6DVMm0AY1gRcs=",
     "stock": 30,  "categoria": "Panadería"},
    {"id": 6, "nombre": "Galletas de vainilla",   "peso": "6 und (222 gr)","precio": 4.70,
     "img": "https://vegaperu.vtexassets.com/arquivos/ids/157311/7622300279776.jpg?v=637618918678400000",
     "stock": 90,  "categoria": "Galletas"},
     {"id": 7, "nombre": "Queso Fundido Cheddar GLORIA", "peso": "136 g", "precio": 7.20,
     "img": "https://images.rappi.pe/products/1779873513340_1779873511466_1779873508195.png", 
     "stock": 2, "categoria": "Lácteos"},
]

# ------------------------------------------------------------
# DECORADORES
# ------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            flash("Debes iniciar sesión.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Acceso restringido a administradores.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated

# ------------------------------------------------------------
# HOJA DE ESTILOS GLOBAL (una sola vez)
# ------------------------------------------------------------
GLOBAL_CSS = """
<style>
  :root {
    --dark:  #4a2c0a;
    --mid:   #6b3f10;
    --light: #8a5320;
    --gold:  #c89a3e;
    --bg:    #faf6ee;
    --card:  #ffffff;
    --text:  #2c1a06;
    --muted: #7a5c38;
    --border:#e0d0b8;
    --r:     10px;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; display: flex; flex-direction: column; }

  /* HEADER */
  header {
    background: linear-gradient(135deg, var(--dark), var(--mid));
    padding: 0 1.5rem;
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: .5rem;
    position: sticky; top: 0; z-index: 100;
    box-shadow: 0 3px 12px rgba(0,0,0,.3);
  }
  .brand { display: flex; align-items: center; gap: .6rem; padding: .75rem 0; color: #e8d18a; font-size: 1.15rem; font-weight: 700; text-decoration: none; }
  nav { display: flex; flex-wrap: wrap; gap: .25rem; padding: .5rem 0; }
  nav a { color: #e8dfd0; font-size: .85rem; padding: .35rem .85rem; border-radius: 20px; text-decoration: none; transition: background .2s; }
  nav a:hover { background: rgba(200,154,62,.25); }

  /* CONTAINER */
  .container { max-width: 1280px; margin: 1.5rem auto; padding: 0 1.25rem; flex: 1; }

  /* ALERTS */
  .alert { padding: .75rem 1rem; border-radius: var(--r); margin-bottom: .75rem; font-size: .875rem; border-left: 4px solid; }
  .alert-success { background: #f0faf2; color: #1e6e35; border-color: #2e7d32; }
  .alert-danger  { background: #fff2f2; color: #b71c1c; border-color: #c62828; }
  .alert-warning { background: #fffbec; color: #8a6000; border-color: #f0a500; }
  .alert-info    { background: #f0f6ff; color: #1a4a8a; border-color: #2979ff; }

  /* BUTTONS */
  .btn { display: inline-block; padding: .45rem 1.1rem; border: none; border-radius: 7px; font-size: .875rem; font-weight: 600; cursor: pointer; text-decoration: none; transition: filter .15s, transform .1s; font-family: inherit; }
  .btn:hover { filter: brightness(1.08); transform: translateY(-1px); }
  .btn-primary { background: linear-gradient(135deg, var(--mid), var(--light)); color: #fff; }
  .btn-danger  { background: linear-gradient(135deg, #c62828, #e53935); color: #fff; }
  .btn-ghost   { background: #f0ebe3; color: var(--mid); border: 1px solid var(--border); }
  .btn-block   { width: 100%; padding: .7rem; font-size: .95rem; }

  /* CARD */
  .card { background: var(--card); border-radius: var(--r); padding: 1.5rem; box-shadow: 0 4px 16px rgba(74,44,10,.12); border: 1px solid var(--border); }

  /* FORMS */
  .form-group  { margin-bottom: 1rem; }
  .form-row    { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
  label        { display: block; font-size: .8rem; font-weight: 600; color: var(--muted); margin-bottom: .3rem; }
  input, select { width: 100%; padding: .55rem .85rem; border: 1.5px solid var(--border); border-radius: 7px; font-size: .875rem; font-family: inherit; background: #fdfbf7; color: var(--text); transition: border-color .2s; }
  input:focus, select:focus { outline: none; border-color: var(--gold); box-shadow: 0 0 0 3px rgba(200,154,62,.18); }
  .form-actions { display: flex; gap: .6rem; margin-top: .5rem; }

  /* TABLE */
  table { width: 100%; border-collapse: collapse; background: var(--card); border-radius: var(--r); overflow: hidden; box-shadow: 0 4px 16px rgba(74,44,10,.12); }
  th { background: linear-gradient(135deg, var(--dark), var(--mid)); color: #e8d18a; padding: .75rem 1rem; text-align: left; font-size: .78rem; text-transform: uppercase; letter-spacing: .5px; }
  td { padding: .7rem 1rem; border-bottom: 1px solid #f0ebe3; font-size: .875rem; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #fdf8f2; }
  .actions { display: flex; gap: .5rem; }

  /* AUTH */
  .auth-wrap { max-width: 400px; margin: 2rem auto; }
  .auth-wrap h2 { text-align: center; color: var(--dark); margin-bottom: 1.25rem; font-size: 1.4rem; }

  /* FOOTER */
  footer { background: var(--dark); color: #9e8060; text-align: center; padding: 1rem; margin-top: auto; font-size: .8rem; }
  footer strong { color: var(--gold); }

  /* BADGES */
  .badge { display: inline-block; font-size: .75rem; font-weight: 700; padding: .2rem .65rem; border-radius: 20px; }
  .badge-admin   { background: #fff3e0; color: #e65100; }
  .badge-cliente { background: #e8f5e9; color: #2e7d32; }
  .badge-cat     { background: #f0e8d6; color: var(--light); }
  .badge-stock-ok  { background: #e8f5e9; color: #2e7d32; }
  .badge-stock-low { background: #fff0f0; color: #c62828; }

  @media (max-width: 600px) { .form-row { grid-template-columns: 1fr; } }
</style>
"""

BASE = GLOBAL_CSS + """
<header>
  <a class="brand" href="/">Minimarket <span style="color:var(--gold)">&nbsp;Nelly</span></a>
  <nav>
    <a href="/">Inicio</a>
    <a href="/productos">Productos</a>
    <a href="/contacto">Contacto</a>
    {% if session.username %}
      {% if session.role == 'admin' %}
        <a href="/admin">Admin</a>
        <a href="/admin/clientes">Clientes</a>
      {% endif %}
      <a href="/perfil">Mi Perfil</a>
      <a href="/logout">Salir ({{ session.username }})</a>
    {% else %}
      <a href="/login">Iniciar sesión</a>
      <a href="/register">Registrarse</a>
    {% endif %}
  </nav>
</header>
{% with messages = get_flashed_messages(with_categories=true) %}
  <div style="max-width:1280px;margin:.75rem auto;padding:0 1.25rem">
    {% for cat, msg in messages %}<div class="alert alert-{{ cat }}">{{ msg }}</div>{% endfor %}
  </div>
{% endwith %}
<div class="container">{{ content }}</div>
<footer>&copy; 2026 <strong>Minimarket Nelly</strong>. Todos los derechos reservados.</footer>
"""

def render_base(content_html, **ctx):
    tpl = BASE.replace("{{ content }}", content_html)
    return render_template_string(tpl, **ctx)


INDEX_CONTENT = """
<style>
  .hero { display:flex; gap:2rem; align-items:center; background:#f2e9d8; padding:2.5rem; border-radius:var(--r); flex-wrap:wrap; margin-bottom:2rem; }
  .hero-text { flex:1; min-width:220px; }
  .hero-text h2 { font-size:2rem; color:var(--dark); margin-bottom:.75rem; }
  .hero-text p  { color:var(--muted); line-height:1.65; margin-bottom:1.25rem; }
  .hero img     { flex:1; min-width:220px; max-width:420px; border-radius:var(--r); object-fit:cover; }
  .features { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:1rem; }
  .feat { background:var(--card); border-radius:var(--r); padding:1.25rem; text-align:center; border:1px solid var(--border); }
  .feat .icon { font-size:2rem; margin-bottom:.5rem; }
  .feat h3 { font-size:.95rem; color:var(--dark); margin-bottom:.3rem; }
  .feat p  { font-size:.8rem; color:var(--muted); }
</style>
<div class="hero">
  <div class="hero-text">
    <h2>Siempre a tu disposición</h2>
    <p>Productos de calidad para tu hogar, frescos y a precios competitivos. Tu bodega de confianza en el barrio.</p>
    <a href="/productos" class="btn btn-primary">Ver Productos →</a>
  </div>
  <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRmrN-Sgy3YWNqUsjVziPRu9zKMV46mrh57sQ&s" alt="Minimarket">
</div>
<div class="features">
  <div class="feat">
    <h3>Horario</h3>
    <p>Lun–Sáb 7:00–22:00 · Dom 8:00–14:00</p>
  </div>
  <div class="feat">
    <h3>Precios Justos</h3>
    <p>Productos de buena calidad.</p>
  </div>
  <div class="feat">
    <h3>Ubicación</h3>
    <p>c.8 Bayovar, SJL — ven a conocernos.</p>
  </div>
</div>
"""

CONTACTO_CONTENT = """
<div style="max-width:500px;margin:0 auto">
  <h2 style="color:var(--dark);margin-bottom:1.25rem">Encuéntranos</h2>
  <div class="card" style="display:grid;gap:.85rem">
    <p><strong>Ubicación:</strong> c.8 Bayovar, SJL, Lima, Perú</p>
    <p><strong>Horario:</strong> Lun–Sáb 7:00–22:00 · Dom 8:00–14:00</p>
    <p><strong>Teléfono:</strong> +51 935 206 954</p>
  </div>
</div>
"""

PRODUCTOS_TEMPLATE = GLOBAL_CSS + """
<header>
  <a class="brand" href="/"> Minimarket <span style="color:var(--gold)">&nbsp;Nelly</span></a>
  <nav><a href="/">← Inicio</a></nav>
</header>
<div class="container">
  <div style="display:flex;gap:1.5rem;align-items:flex-start;flex-wrap:wrap">

    <!-- GRILLA PRODUCTOS -->
    <div style="flex:1;min-width:0">
      <h2 style="color:var(--dark);margin-bottom:1rem">🛍 Nuestros Productos</h2>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem">
        {% for p in productos %}
        <div class="card" style="display:flex;flex-direction:column;padding:1rem">
          <img src="{{ p.img }}" alt="{{ p.nombre }}"
               style="width:100%;height:110px;object-fit:contain;border-radius:6px;background:#faf6ee;margin-bottom:.6rem">
          <strong style="font-size:.875rem">{{ p.nombre }}</strong>
          <span style="font-size:.75rem;color:var(--muted);margin:.2rem 0 .5rem">{{ p.peso }}</span>
          <span style="font-size:1.1rem;font-weight:800;color:var(--dark);margin-top:auto;margin-bottom:.65rem">S/ {{ "%.2f"|format(p.precio) }}</span>
          <form method="POST" action="/agregar">
            <input type="hidden" name="nombre_producto" value="{{ p.nombre }}">
            <button type="submit" class="btn btn-primary btn-block" style="font-size:.8rem"> Añadir</button>
          </form>
        </div>
        {% endfor %}
      </div>
    </div>

    <!-- CARRITO -->
    <aside style="width:280px;flex-shrink:0;position:sticky;top:70px">
      <div class="card">
        <h3 style="color:var(--dark);margin-bottom:1rem;padding-bottom:.6rem;border-bottom:2px solid var(--border)"> Tu Carrito</h3>
        {% if session.get('carrito') %}
          {% for item_id, item in session['carrito'].items() %}
          <div style="display:flex;justify-content:space-between;align-items:center;padding:.4rem 0;border-bottom:1px dashed var(--border);font-size:.8rem;gap:.4rem">
            <span style="flex:1">{{ item.nombre }} <em style="color:var(--muted)">×{{ item.cantidad }}</em></span>
            <span style="font-weight:700;white-space:nowrap">S/{{ "%.2f"|format(item.precio * item.cantidad) }}</span>
            <form method="POST" action="/quitar/{{ item_id }}">
              <button type="submit" style="background:none;border:none;color:#c0392b;cursor:pointer">✕</button>
            </form>
          </div>
          {% endfor %}
          <div style="display:flex;justify-content:space-between;font-weight:800;font-size:1rem;margin:.75rem 0;padding-top:.6rem;border-top:2px solid var(--dark)">
            <span>Total</span><span style="color:#2e7d32">S/{{ "%.2f"|format(total) }}</span>
          </div>
          <form method="POST" action="/vaciar">
            <button type="submit" class="btn btn-block" style="background:linear-gradient(135deg,#2e7d32,#43a047);color:#fff"> Confirmar compra</button>
          </form>
        {% else %}
          <p style="text-align:center;color:var(--muted);padding:1.5rem 0;font-size:.875rem">Tu carrito está vacío.</p>
        {% endif %}
      </div>
    </aside>

  </div>
</div>
<style>
  @media (max-width: 700px) {
    .container > div > div:first-child > div { grid-template-columns: repeat(2, 1fr) !important; }
  }
  @media (max-width: 480px) {
    .container > div > div:first-child > div { grid-template-columns: 1fr !important; }
  }
</style>
<footer>&copy; 2026 <strong>Minimarket Nelly</strong>. Todos los derechos reservados.</footer>
"""

AUTH_TEMPLATE = """
<div class="auth-wrap">
  <div class="card">
    <h2>{{ title }}</h2>
    <form method="post">
      {% for field in fields %}
        <div class="form-group">
          <label>{{ field.label }}</label>
          <input type="{{ field.type }}" name="{{ field.name }}" placeholder="{{ field.placeholder }}" {{ 'required' if field.required else '' }}>
        </div>
      {% endfor %}
      <button type="submit" class="btn btn-primary btn-block">{{ submit }}</button>
    </form>
    <p style="text-align:center;margin-top:1rem;font-size:.875rem;color:var(--muted)">{{ footer_text | safe }}</p>
  </div>
</div>
"""

LOGIN_CONTENT = """
<div class="auth-wrap">
  <div class="card">
    <h2> Iniciar Sesión</h2>
    <form method="post">
      <div class="form-group"><label>Usuario</label><input name="username" required placeholder="Tu nombre de usuario"></div>
      <div class="form-group"><label>Contraseña</label><input type="password" name="password" required placeholder="••••••••"></div>
      <button type="submit" class="btn btn-primary btn-block">Ingresar</button>
    </form>
    <p style="text-align:center;margin-top:1rem;font-size:.875rem;color:var(--muted)">¿No tienes cuenta? <a href="/register" style="color:var(--light);font-weight:600">Regístrate</a></p>
  </div>
</div>
"""

REGISTER_CONTENT = """
<div class="auth-wrap">
  <div class="card">
    <h2> Crear Cuenta</h2>
    <form method="post">
      <div class="form-group"><label>Usuario</label><input name="username" required placeholder="Elige un nombre de usuario"></div>
      <div class="form-group"><label>Correo Electrónico</label><input type="email" name="email" required placeholder="tucorreo@ejemplo.com"></div>
      <div class="form-group"><label>Contraseña</label><input type="password" name="password" required placeholder="Mínimo 6 caracteres"></div>
      <button type="submit" class="btn btn-primary btn-block">Registrarse</button>
    </form>
    <p style="text-align:center;margin-top:1rem;font-size:.875rem;color:var(--muted)">¿Ya tienes cuenta? <a href="/login" style="color:var(--light);font-weight:600">Inicia sesión</a></p>
  </div>
</div>
"""

ADMIN_PANEL_CONTENT = """
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.25rem">
  <h2 style="color:var(--dark)">🗂 Panel de Administración</h2>
  <a href="/admin/add" class="btn btn-primary">+ Nuevo Producto</a>
</div>
<table>
  <thead>
    <tr><th>ID</th><th>Nombre</th><th>Precio</th><th>Stock</th><th>Categoría</th><th>Acciones</th></tr>
  </thead>
  <tbody>
    {% for p in productos %}
    <tr>
      <td style="color:var(--muted);font-weight:700">#{{ p.id }}</td>
      <td><strong>{{ p.nombre }}</strong></td>
      <td style="color:#2e7d32;font-weight:700">S/{{ "%.2f"|format(p.precio) }}</td>
      <td><span class="badge {{ 'badge-stock-ok' if p.stock >= 20 else 'badge-stock-low' }}">{{ p.stock }}</span></td>
      <td><span class="badge badge-cat">{{ p.categoria }}</span></td>
      <td class="actions">
        <a href="/admin/edit/{{ p.id }}" class="btn btn-ghost">✏ Editar</a>
        <a href="/admin/delete/{{ p.id }}" class="btn btn-danger" onclick="return confirm('¿Eliminar?')">🗑</a>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>
"""

ADMIN_CLIENTES_CONTENT = """
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.25rem">
  <h2 style="color:var(--dark)">Gestión de Clientes</h2>
  <a href="/admin/clientes/add" class="btn btn-primary">+ Nuevo Cliente</a>
</div>
<table>
  <thead>
    <tr><th>Usuario</th><th>Correo</th><th>Rol</th><th>Acciones</th></tr>
  </thead>
  <tbody>
    {% for username, data in usuarios.items() %}
      {% if username != session.username %}
      <tr>
        <td><strong>{{ username }}</strong></td>
        <td>{{ data.email }}</td>
        <td><span class="badge badge-{{ data.role }}">{{ data.role }}</span></td>
        <td class="actions">
          <a href="/admin/clientes/edit/{{ username }}" class="btn btn-ghost">✏ Editar</a>
          <a href="/admin/clientes/delete/{{ username }}" class="btn btn-danger" onclick="return confirm('¿Eliminar?')">🗑</a>
        </td>
      </tr>
      {% endif %}
    {% endfor %}
  </tbody>
</table>
"""

FORM_PRODUCTO_CONTENT = """
<div style="max-width:520px;margin:0 auto">
  <div class="card">
    <h2 style="color:var(--dark);margin-bottom:1.25rem">{{ '✏ Editar' if producto else ' Nuevo' }} Producto</h2>
    <form method="post">
      <div class="form-group"><label>Nombre</label><input name="nombre" value="{{ producto.nombre if producto else '' }}" required placeholder="Ej: Leche Gloria"></div>
      <div class="form-row">
        <div class="form-group"><label>Precio (S/)</label><input name="precio" type="number" step="0.01" value="{{ producto.precio if producto else '' }}" required placeholder="0.00"></div>
        <div class="form-group"><label>Stock</label><input name="stock" type="number" value="{{ producto.stock if producto else '' }}" required placeholder="0"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Categoría</label><input name="categoria" value="{{ producto.categoria if producto else '' }}" placeholder="Ej: Lácteos"></div>
        <div class="form-group"><label>Peso / Descripción</label><input name="peso" value="{{ producto.peso if producto else '' }}" placeholder="Ej: 390 gr"></div>
      </div>
      <div class="form-group"><label>URL de Imagen</label><input name="img" value="{{ producto.img if producto else '' }}" placeholder="https://..."></div>
      <div class="form-actions">
        <button type="submit" class="btn btn-primary"> Guardar</button>
        <a href="/admin" class="btn btn-ghost">Cancelar</a>
      </div>
    </form>
  </div>
</div>
"""

FORM_CLIENTE_CONTENT = """
<div style="max-width:460px;margin:0 auto">
  <div class="card">
    <h2 style="color:var(--dark);margin-bottom:1.25rem">{{ '✏ Editar Cliente' if cliente else '👤 Nuevo Cliente' }}</h2>
    <form method="post">
      {% if not cliente %}
      <div class="form-group"><label>Usuario</label><input name="username" required placeholder="Nombre de usuario"></div>
      {% endif %}
      <div class="form-group"><label>Correo Electrónico</label><input type="email" name="email" value="{{ cliente.email if cliente else '' }}" required placeholder="correo@ejemplo.com"></div>
      <div class="form-group"><label>Contraseña</label><input type="password" name="password" {% if cliente %}placeholder="Dejar en blanco para no cambiar"{% else %}required{% endif %}></div>
      <div class="form-group">
        <label>Rol</label>
        <select name="role">
          <option value="cliente" {{ 'selected' if cliente and cliente.role == 'cliente' }}>Cliente</option>
          <option value="admin"   {{ 'selected' if cliente and cliente.role == 'admin' }}>Admin</option>
        </select>
      </div>
      <div class="form-actions">
        <button type="submit" class="btn btn-primary"> Guardar</button>
        <a href="/admin/clientes" class="btn btn-ghost">Cancelar</a>
      </div>
    </form>
  </div>
</div>
"""

PERFIL_CONTENT = """
<div style="max-width:460px;margin:0 auto">
  <div class="card">
    <h2 style="color:var(--dark);margin-bottom:1rem"> Editar Perfil</h2>
    <div style="background:#fefaf2;padding:.85rem 1rem;border-radius:8px;border:1px solid var(--border);margin-bottom:1.25rem;font-size:.875rem">
      <p><strong style="color:var(--muted)">Usuario:</strong> {{ session.username }}</p>
      <p style="margin-top:.3rem"><strong style="color:var(--muted)">Correo:</strong> {{ current_email }}</p>
    </div>
    <form method="post">
      <div class="form-group"><label>Nuevo nombre de usuario</label><input type="text" name="new_username" value="{{ session.username }}"></div>
      <div class="form-group"><label>Correo electrónico</label><input type="email" name="email" value="{{ current_email }}" required></div>
      <div class="form-actions">
        <button type="submit" class="btn btn-primary"> Guardar</button>
        <a href="/" class="btn btn-ghost">Cancelar</a>
      </div>
    </form>
  </div>
</div>
"""

# ------------------------------------------------------------
# RUTAS
# ------------------------------------------------------------
@app.route('/')
def index():
    return render_base(INDEX_CONTENT)

@app.route('/contacto')
def contacto():
    return render_base(CONTACTO_CONTENT)

@app.route('/productos')
def productos():
    carrito = session.get('carrito', {})
    total = sum(i['precio'] * i['cantidad'] for i in carrito.values())
    return render_template_string(PRODUCTOS_TEMPLATE, productos=PRODUCTOS, total=total)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = USERS.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            flash(f'Bienvenido {username}', 'success')
            return redirect(url_for('admin_panel') if user['role'] == 'admin' else url_for('productos'))
        flash('Usuario o contraseña incorrectos', 'danger')
    return render_base(LOGIN_CONTENT)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip()
        password = request.form['password'].strip()
        if not username or not email or not password:
            flash('Todos los campos son obligatorios', 'danger')
        elif username in USERS:
            flash('El nombre de usuario ya existe', 'danger')
        else:
            USERS[username] = {'password': password, 'role': 'cliente', 'email': email}
            save_users(USERS)
            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
    return render_base(REGISTER_CONTENT)

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'warning')
    return redirect(url_for('index'))

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    username_actual = session['username']
    usuario_data = USERS.get(username_actual)
    if not usuario_data:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('logout'))
    if request.method == 'POST':
        new_username = request.form.get('new_username', '').strip()
        new_email    = request.form.get('email', '').strip()
        if not new_email:
            flash('El correo es obligatorio', 'danger')
            return redirect(url_for('perfil'))
        if new_username and new_username != username_actual:
            if new_username in USERS:
                flash('El nuevo nombre de usuario ya está en uso', 'danger')
                return redirect(url_for('perfil'))
            USERS[new_username] = USERS.pop(username_actual)
            USERS[new_username]['email'] = new_email
            session['username'] = new_username
            flash('Nombre de usuario actualizado', 'success')
        else:
            USERS[username_actual]['email'] = new_email
            flash('Correo actualizado', 'success')
        save_users(USERS)
        return redirect(url_for('perfil'))
    return render_base(PERFIL_CONTENT, current_email=usuario_data.get('email', ''))

# CARRITO
@app.route('/agregar', methods=['POST'])
def agregar():
    nombre   = request.form.get('nombre_producto')
    producto = next((p for p in PRODUCTOS if p['nombre'] == nombre), None)
    if not producto:
        flash('Producto no disponible', 'danger')
        return redirect(url_for('productos'))
    carrito = session.get('carrito', {})
    for item in carrito.values():
        if item['nombre'] == nombre:
            item['cantidad'] += 1
            break
    else:
        carrito[str(uuid.uuid4())] = {'nombre': nombre, 'precio': producto['precio'], 'cantidad': 1}
    session['carrito'] = carrito
    session.modified = True
    flash(f'{nombre} añadido al carrito', 'success')
    return redirect(url_for('productos'))

@app.route('/quitar/<item_id>', methods=['POST'])
def quitar(item_id):
    carrito = session.get('carrito', {})
    carrito.pop(item_id, None)
    session['carrito'] = carrito
    flash('Producto eliminado del carrito', 'info')
    return redirect(url_for('productos'))

@app.route('/vaciar', methods=['POST'])
def vaciar():
    session.pop('carrito', None)
    flash('¡Compra realizada! Gracias.', 'success')
    return redirect(url_for('productos'))

# ADMIN — PRODUCTOS
@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    return render_base(ADMIN_PANEL_CONTENT, productos=PRODUCTOS)

@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add():
    if request.method == 'POST':
        nuevo_id = max((p['id'] for p in PRODUCTOS), default=0) + 1
        PRODUCTOS.append({
            'id':       nuevo_id,
            'nombre':   request.form['nombre'].strip(),
            'precio':   float(request.form['precio']),
            'stock':    int(request.form['stock']),
            'categoria':request.form['categoria'],
            'peso':     request.form.get('peso', ''),
            'img':      request.form.get('img', 'https://via.placeholder.com/150'),
        })
        flash('Producto agregado', 'success')
        return redirect(url_for('admin_panel'))
    return render_base(FORM_PRODUCTO_CONTENT, producto=None)

@app.route('/admin/edit/<int:pid>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit(pid):
    producto = next((p for p in PRODUCTOS if p['id'] == pid), None)
    if not producto:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('admin_panel'))
    if request.method == 'POST':
        producto.update({
            'nombre':   request.form['nombre'].strip(),
            'precio':   float(request.form['precio']),
            'stock':    int(request.form['stock']),
            'categoria':request.form['categoria'],
            'peso':     request.form.get('peso', producto.get('peso', '')),
            'img':      request.form.get('img',  producto.get('img', '')),
        })
        flash('Producto actualizado', 'success')
        return redirect(url_for('admin_panel'))
    return render_base(FORM_PRODUCTO_CONTENT, producto=producto)

@app.route('/admin/delete/<int:pid>')
@login_required
@admin_required
def admin_delete(pid):
    global PRODUCTOS
    PRODUCTOS = [p for p in PRODUCTOS if p['id'] != pid]
    flash('Producto eliminado', 'success')
    return redirect(url_for('admin_panel'))

# ADMIN — CLIENTES
@app.route('/admin/clientes')
@login_required
@admin_required
def admin_clientes():
    return render_base(ADMIN_CLIENTES_CONTENT, usuarios=USERS)

@app.route('/admin/clientes/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_cliente_add():from flask import Flask, render_template_string, redirect, url_for, request, session, flash
from functools import wraps
import uuid
import json
import os

app = Flask(__name__)
app.secret_key = 'clave_minimarket_2026'

# ------------------------------------------------------------
# PERSISTENCIA DE USUARIOS (JSON)
# ------------------------------------------------------------
USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    default_users = {
        "admin":   {"password": "admin123",   "role": "admin",   "email": "admin@minimarket.com"},
        "cliente": {"password": "cliente123", "role": "cliente", "email": "cliente@minimarket.com"},
    }
    save_users(default_users)
    return default_users

def save_users(users_dict):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_dict, f, indent=4, ensure_ascii=False)

USERS = load_users()

# ------------------------------------------------------------
# PRODUCTOS (en memoria)
# ------------------------------------------------------------
PRODUCTOS = [
    {"id": 1, "nombre": "Galleta soda",      "peso": "6 und (222 gr)", "precio": 3.30,
     "img": "https://plazavea.vteximg.com.br/arquivos/ids/25835356-1000-1000/502139.jpg",
     "stock": 100, "categoria": "Galletas"},
    {"id": 2, "nombre": "Coca Cola",          "peso": "500 ml",         "precio": 3.50,
     "img": "https://yopo.pe/wp-content/uploads/2023/12/COCA-500-ORIGINAL-RAPPI.jpg",
     "stock": 80,  "categoria": "Bebidas"},
    {"id": 3, "nombre": "Leche Gloria",       "peso": "390 gr",         "precio": 4.20,
     "img": "https://www.gloria.com.pe/images/lataa.png",
     "stock": 60,  "categoria": "Lácteos"},
    {"id": 4, "nombre": "Yogurt Laive",       "peso": "1000 gr",        "precio": 6.50,
     "img": "https://wongfood.vtexassets.com/arquivos/ids/809652-1200-auto?v=639023674094630000&width=1200&height=auto&aspect=true",
     "stock": 40,  "categoria": "Lácteos"},
    {"id": 5, "nombre": "Pan en bolsa",       "peso": "500 gr",         "precio": 8.50,
     "img": "https://media.istockphoto.com/id/518733512/es/foto/pan-en-bolsa-de-pl%C3%A1stico.jpg?s=612x612&w=0&k=20&c=UPaAZgdhKw7Rq-1KMJtAHLEl4ioz8Q6DVMm0AY1gRcs=",
     "stock": 30,  "categoria": "Panadería"},
    {"id": 6, "nombre": "Galletas de vainilla",   "peso": "6 und (222 gr)","precio": 4.70,
     "img": "https://vegaperu.vtexassets.com/arquivos/ids/157311/7622300279776.jpg?v=637618918678400000",
     "stock": 90,  "categoria": "Galletas"},
     {"id": 7, "nombre": "Queso Fundido Cheddar GLORIA", "peso": "136 g", "precio": 7.20,
     "img": "https://images.rappi.pe/products/1779873513340_1779873511466_1779873508195.png", 
     "stock": 2, "categoria": "Lácteos"},
]

# ------------------------------------------------------------
# DECORADORES
# ------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            flash("Debes iniciar sesión.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Acceso restringido a administradores.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated

# ------------------------------------------------------------
# HOJA DE ESTILOS GLOBAL (una sola vez)
# ------------------------------------------------------------
GLOBAL_CSS = """
<style>
  :root {
    --dark:  #4a2c0a;
    --mid:   #6b3f10;
    --light: #8a5320;
    --gold:  #c89a3e;
    --bg:    #faf6ee;
    --card:  #ffffff;
    --text:  #2c1a06;
    --muted: #7a5c38;
    --border:#e0d0b8;
    --r:     10px;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; display: flex; flex-direction: column; }

  /* HEADER */
  header {
    background: linear-gradient(135deg, var(--dark), var(--mid));
    padding: 0 1.5rem;
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: .5rem;
    position: sticky; top: 0; z-index: 100;
    box-shadow: 0 3px 12px rgba(0,0,0,.3);
  }
  .brand { display: flex; align-items: center; gap: .6rem; padding: .75rem 0; color: #e8d18a; font-size: 1.15rem; font-weight: 700; text-decoration: none; }
  nav { display: flex; flex-wrap: wrap; gap: .25rem; padding: .5rem 0; }
  nav a { color: #e8dfd0; font-size: .85rem; padding: .35rem .85rem; border-radius: 20px; text-decoration: none; transition: background .2s; }
  nav a:hover { background: rgba(200,154,62,.25); }

  /* CONTAINER */
  .container { max-width: 1280px; margin: 1.5rem auto; padding: 0 1.25rem; flex: 1; }

  /* ALERTS */
  .alert { padding: .75rem 1rem; border-radius: var(--r); margin-bottom: .75rem; font-size: .875rem; border-left: 4px solid; }
  .alert-success { background: #f0faf2; color: #1e6e35; border-color: #2e7d32; }
  .alert-danger  { background: #fff2f2; color: #b71c1c; border-color: #c62828; }
  .alert-warning { background: #fffbec; color: #8a6000; border-color: #f0a500; }
  .alert-info    { background: #f0f6ff; color: #1a4a8a; border-color: #2979ff; }

  /* BUTTONS */
  .btn { display: inline-block; padding: .45rem 1.1rem; border: none; border-radius: 7px; font-size: .875rem; font-weight: 600; cursor: pointer; text-decoration: none; transition: filter .15s, transform .1s; font-family: inherit; }
  .btn:hover { filter: brightness(1.08); transform: translateY(-1px); }
  .btn-primary { background: linear-gradient(135deg, var(--mid), var(--light)); color: #fff; }
  .btn-danger  { background: linear-gradient(135deg, #c62828, #e53935); color: #fff; }
  .btn-ghost   { background: #f0ebe3; color: var(--mid); border: 1px solid var(--border); }
  .btn-block   { width: 100%; padding: .7rem; font-size: .95rem; }

  /* CARD */
  .card { background: var(--card); border-radius: var(--r); padding: 1.5rem; box-shadow: 0 4px 16px rgba(74,44,10,.12); border: 1px solid var(--border); }

  /* FORMS */
  .form-group  { margin-bottom: 1rem; }
  .form-row    { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
  label        { display: block; font-size: .8rem; font-weight: 600; color: var(--muted); margin-bottom: .3rem; }
  input, select { width: 100%; padding: .55rem .85rem; border: 1.5px solid var(--border); border-radius: 7px; font-size: .875rem; font-family: inherit; background: #fdfbf7; color: var(--text); transition: border-color .2s; }
  input:focus, select:focus { outline: none; border-color: var(--gold); box-shadow: 0 0 0 3px rgba(200,154,62,.18); }
  .form-actions { display: flex; gap: .6rem; margin-top: .5rem; }

  /* TABLE */
  table { width: 100%; border-collapse: collapse; background: var(--card); border-radius: var(--r); overflow: hidden; box-shadow: 0 4px 16px rgba(74,44,10,.12); }
  th { background: linear-gradient(135deg, var(--dark), var(--mid)); color: #e8d18a; padding: .75rem 1rem; text-align: left; font-size: .78rem; text-transform: uppercase; letter-spacing: .5px; }
  td { padding: .7rem 1rem; border-bottom: 1px solid #f0ebe3; font-size: .875rem; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #fdf8f2; }
  .actions { display: flex; gap: .5rem; }

  /* AUTH */
  .auth-wrap { max-width: 400px; margin: 2rem auto; }
  .auth-wrap h2 { text-align: center; color: var(--dark); margin-bottom: 1.25rem; font-size: 1.4rem; }

  /* FOOTER */
  footer { background: var(--dark); color: #9e8060; text-align: center; padding: 1rem; margin-top: auto; font-size: .8rem; }
  footer strong { color: var(--gold); }

  /* BADGES */
  .badge { display: inline-block; font-size: .75rem; font-weight: 700; padding: .2rem .65rem; border-radius: 20px; }
  .badge-admin   { background: #fff3e0; color: #e65100; }
  .badge-cliente { background: #e8f5e9; color: #2e7d32; }
  .badge-cat     { background: #f0e8d6; color: var(--light); }
  .badge-stock-ok  { background: #e8f5e9; color: #2e7d32; }
  .badge-stock-low { background: #fff0f0; color: #c62828; }

  @media (max-width: 600px) { .form-row { grid-template-columns: 1fr; } }
</style>
"""

BASE = GLOBAL_CSS + """
<header>
  <a class="brand" href="/">Minimarket <span style="color:var(--gold)">&nbsp;Nelly</span></a>
  <nav>
    <a href="/">Inicio</a>
    <a href="/productos">Productos</a>
    <a href="/contacto">Contacto</a>
    {% if session.username %}
      {% if session.role == 'admin' %}
        <a href="/admin">Admin</a>
        <a href="/admin/clientes">Clientes</a>
      {% endif %}
      <a href="/perfil">Mi Perfil</a>
      <a href="/logout">Salir ({{ session.username }})</a>
    {% else %}
      <a href="/login">Iniciar sesión</a>
      <a href="/register">Registrarse</a>
    {% endif %}
  </nav>
</header>
{% with messages = get_flashed_messages(with_categories=true) %}
  <div style="max-width:1280px;margin:.75rem auto;padding:0 1.25rem">
    {% for cat, msg in messages %}<div class="alert alert-{{ cat }}">{{ msg }}</div>{% endfor %}
  </div>
{% endwith %}
<div class="container">{{ content }}</div>
<footer>&copy; 2026 <strong>Minimarket Nelly</strong>. Todos los derechos reservados.</footer>
"""

def render_base(content_html, **ctx):
    tpl = BASE.replace("{{ content }}", content_html)
    return render_template_string(tpl, **ctx)


INDEX_CONTENT = """
<style>
  .hero { display:flex; gap:2rem; align-items:center; background:#f2e9d8; padding:2.5rem; border-radius:var(--r); flex-wrap:wrap; margin-bottom:2rem; }
  .hero-text { flex:1; min-width:220px; }
  .hero-text h2 { font-size:2rem; color:var(--dark); margin-bottom:.75rem; }
  .hero-text p  { color:var(--muted); line-height:1.65; margin-bottom:1.25rem; }
  .hero img     { flex:1; min-width:220px; max-width:420px; border-radius:var(--r); object-fit:cover; }
  .features { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:1rem; }
  .feat { background:var(--card); border-radius:var(--r); padding:1.25rem; text-align:center; border:1px solid var(--border); }
  .feat .icon { font-size:2rem; margin-bottom:.5rem; }
  .feat h3 { font-size:.95rem; color:var(--dark); margin-bottom:.3rem; }
  .feat p  { font-size:.8rem; color:var(--muted); }
</style>
<div class="hero">
  <div class="hero-text">
    <h2>Siempre a tu disposición</h2>
    <p>Productos de calidad para tu hogar, frescos y a precios competitivos. Tu bodega de confianza en el barrio.</p>
    <a href="/productos" class="btn btn-primary">Ver Productos →</a>
  </div>
  <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRmrN-Sgy3YWNqUsjVziPRu9zKMV46mrh57sQ&s" alt="Minimarket">
</div>
<div class="features">
  <div class="feat">
    <h3>Horario</h3>
    <p>Lun–Sáb 7:00–22:00 · Dom 8:00–14:00</p>
  </div>
  <div class="feat">
    <h3>Precios Justos</h3>
    <p>Productos de buena calidad.</p>
  </div>
  <div class="feat">
    <h3>Ubicación</h3>
    <p>c.8 Bayovar, SJL — ven a conocernos.</p>
  </div>
</div>
"""

CONTACTO_CONTENT = """
<div style="max-width:500px;margin:0 auto">
  <h2 style="color:var(--dark);margin-bottom:1.25rem">Encuéntranos</h2>
  <div class="card" style="display:grid;gap:.85rem">
    <p><strong>Ubicación:</strong> c.8 Bayovar, SJL, Lima, Perú</p>
    <p><strong>Horario:</strong> Lun–Sáb 7:00–22:00 · Dom 8:00–14:00</p>
    <p><strong>Teléfono:</strong> +51 935 206 954</p>
  </div>
</div>
"""

PRODUCTOS_TEMPLATE = GLOBAL_CSS + """
<header>
  <a class="brand" href="/"> Minimarket <span style="color:var(--gold)">&nbsp;Nelly</span></a>
  <nav><a href="/">← Inicio</a></nav>
</header>
<div class="container">
  <div style="display:flex;gap:1.5rem;align-items:flex-start;flex-wrap:wrap">

    <!-- GRILLA PRODUCTOS -->
    <div style="flex:1;min-width:0">
      <h2 style="color:var(--dark);margin-bottom:1rem">🛍 Nuestros Productos</h2>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem">
        {% for p in productos %}
        <div class="card" style="display:flex;flex-direction:column;padding:1rem">
          <img src="{{ p.img }}" alt="{{ p.nombre }}"
               style="width:100%;height:110px;object-fit:contain;border-radius:6px;background:#faf6ee;margin-bottom:.6rem">
          <strong style="font-size:.875rem">{{ p.nombre }}</strong>
          <span style="font-size:.75rem;color:var(--muted);margin:.2rem 0 .5rem">{{ p.peso }}</span>
          <span style="font-size:1.1rem;font-weight:800;color:var(--dark);margin-top:auto;margin-bottom:.65rem">S/ {{ "%.2f"|format(p.precio) }}</span>
          <form method="POST" action="/agregar">
            <input type="hidden" name="nombre_producto" value="{{ p.nombre }}">
            <button type="submit" class="btn btn-primary btn-block" style="font-size:.8rem"> Añadir</button>
          </form>
        </div>
        {% endfor %}
      </div>
    </div>

    <!-- CARRITO -->
    <aside style="width:280px;flex-shrink:0;position:sticky;top:70px">
      <div class="card">
        <h3 style="color:var(--dark);margin-bottom:1rem;padding-bottom:.6rem;border-bottom:2px solid var(--border)"> Tu Carrito</h3>
        {% if session.get('carrito') %}
          {% for item_id, item in session['carrito'].items() %}
          <div style="display:flex;justify-content:space-between;align-items:center;padding:.4rem 0;border-bottom:1px dashed var(--border);font-size:.8rem;gap:.4rem">
            <span style="flex:1">{{ item.nombre }} <em style="color:var(--muted)">×{{ item.cantidad }}</em></span>
            <span style="font-weight:700;white-space:nowrap">S/{{ "%.2f"|format(item.precio * item.cantidad) }}</span>
            <form method="POST" action="/quitar/{{ item_id }}">
              <button type="submit" style="background:none;border:none;color:#c0392b;cursor:pointer">✕</button>
            </form>
          </div>
          {% endfor %}
          <div style="display:flex;justify-content:space-between;font-weight:800;font-size:1rem;margin:.75rem 0;padding-top:.6rem;border-top:2px solid var(--dark)">
            <span>Total</span><span style="color:#2e7d32">S/{{ "%.2f"|format(total) }}</span>
          </div>
          <form method="POST" action="/vaciar">
            <button type="submit" class="btn btn-block" style="background:linear-gradient(135deg,#2e7d32,#43a047);color:#fff"> Confirmar compra</button>
          </form>
        {% else %}
          <p style="text-align:center;color:var(--muted);padding:1.5rem 0;font-size:.875rem">Tu carrito está vacío.</p>
        {% endif %}
      </div>
    </aside>

  </div>
</div>
<style>
  @media (max-width: 700px) {
    .container > div > div:first-child > div { grid-template-columns: repeat(2, 1fr) !important; }
  }
  @media (max-width: 480px) {
    .container > div > div:first-child > div { grid-template-columns: 1fr !important; }
  }
</style>
<footer>&copy; 2026 <strong>Minimarket Nelly</strong>. Todos los derechos reservados.</footer>
"""

AUTH_TEMPLATE = """
<div class="auth-wrap">
  <div class="card">
    <h2>{{ title }}</h2>
    <form method="post">
      {% for field in fields %}
        <div class="form-group">
          <label>{{ field.label }}</label>
          <input type="{{ field.type }}" name="{{ field.name }}" placeholder="{{ field.placeholder }}" {{ 'required' if field.required else '' }}>
        </div>
      {% endfor %}
      <button type="submit" class="btn btn-primary btn-block">{{ submit }}</button>
    </form>
    <p style="text-align:center;margin-top:1rem;font-size:.875rem;color:var(--muted)">{{ footer_text | safe }}</p>
  </div>
</div>
"""

LOGIN_CONTENT = """
<div class="auth-wrap">
  <div class="card">
    <h2> Iniciar Sesión</h2>
    <form method="post">
      <div class="form-group"><label>Usuario</label><input name="username" required placeholder="Tu nombre de usuario"></div>
      <div class="form-group"><label>Contraseña</label><input type="password" name="password" required placeholder="••••••••"></div>
      <button type="submit" class="btn btn-primary btn-block">Ingresar</button>
    </form>
    <p style="text-align:center;margin-top:1rem;font-size:.875rem;color:var(--muted)">¿No tienes cuenta? <a href="/register" style="color:var(--light);font-weight:600">Regístrate</a></p>
  </div>
</div>
"""

REGISTER_CONTENT = """
<div class="auth-wrap">
  <div class="card">
    <h2> Crear Cuenta</h2>
    <form method="post">
      <div class="form-group"><label>Usuario</label><input name="username" required placeholder="Elige un nombre de usuario"></div>
      <div class="form-group"><label>Correo Electrónico</label><input type="email" name="email" required placeholder="tucorreo@ejemplo.com"></div>
      <div class="form-group"><label>Contraseña</label><input type="password" name="password" required placeholder="Mínimo 6 caracteres"></div>
      <button type="submit" class="btn btn-primary btn-block">Registrarse</button>
    </form>
    <p style="text-align:center;margin-top:1rem;font-size:.875rem;color:var(--muted)">¿Ya tienes cuenta? <a href="/login" style="color:var(--light);font-weight:600">Inicia sesión</a></p>
  </div>
</div>
"""

ADMIN_PANEL_CONTENT = """
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.25rem">
  <h2 style="color:var(--dark)">🗂 Panel de Administración</h2>
  <a href="/admin/add" class="btn btn-primary">+ Nuevo Producto</a>
</div>
<table>
  <thead>
    <tr><th>ID</th><th>Nombre</th><th>Precio</th><th>Stock</th><th>Categoría</th><th>Acciones</th></tr>
  </thead>
  <tbody>
    {% for p in productos %}
    <tr>
      <td style="color:var(--muted);font-weight:700">#{{ p.id }}</td>
      <td><strong>{{ p.nombre }}</strong></td>
      <td style="color:#2e7d32;font-weight:700">S/{{ "%.2f"|format(p.precio) }}</td>
      <td><span class="badge {{ 'badge-stock-ok' if p.stock >= 20 else 'badge-stock-low' }}">{{ p.stock }}</span></td>
      <td><span class="badge badge-cat">{{ p.categoria }}</span></td>
      <td class="actions">
        <a href="/admin/edit/{{ p.id }}" class="btn btn-ghost">✏ Editar</a>
        <a href="/admin/delete/{{ p.id }}" class="btn btn-danger" onclick="return confirm('¿Eliminar?')">🗑</a>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>
"""

ADMIN_CLIENTES_CONTENT = """
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.25rem">
  <h2 style="color:var(--dark)">Gestión de Clientes</h2>
  <a href="/admin/clientes/add" class="btn btn-primary">+ Nuevo Cliente</a>
</div>
<table>
  <thead>
    <tr><th>Usuario</th><th>Correo</th><th>Rol</th><th>Acciones</th></tr>
  </thead>
  <tbody>
    {% for username, data in usuarios.items() %}
      {% if username != session.username %}
      <tr>
        <td><strong>{{ username }}</strong></td>
        <td>{{ data.email }}</td>
        <td><span class="badge badge-{{ data.role }}">{{ data.role }}</span></td>
        <td class="actions">
          <a href="/admin/clientes/edit/{{ username }}" class="btn btn-ghost">✏ Editar</a>
          <a href="/admin/clientes/delete/{{ username }}" class="btn btn-danger" onclick="return confirm('¿Eliminar?')">🗑</a>
        </td>
      </tr>
      {% endif %}
    {% endfor %}
  </tbody>
</table>
"""

FORM_PRODUCTO_CONTENT = """
<div style="max-width:520px;margin:0 auto">
  <div class="card">
    <h2 style="color:var(--dark);margin-bottom:1.25rem">{{ '✏ Editar' if producto else ' Nuevo' }} Producto</h2>
    <form method="post">
      <div class="form-group"><label>Nombre</label><input name="nombre" value="{{ producto.nombre if producto else '' }}" required placeholder="Ej: Leche Gloria"></div>
      <div class="form-row">
        <div class="form-group"><label>Precio (S/)</label><input name="precio" type="number" step="0.01" value="{{ producto.precio if producto else '' }}" required placeholder="0.00"></div>
        <div class="form-group"><label>Stock</label><input name="stock" type="number" value="{{ producto.stock if producto else '' }}" required placeholder="0"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Categoría</label><input name="categoria" value="{{ producto.categoria if producto else '' }}" placeholder="Ej: Lácteos"></div>
        <div class="form-group"><label>Peso / Descripción</label><input name="peso" value="{{ producto.peso if producto else '' }}" placeholder="Ej: 390 gr"></div>
      </div>
      <div class="form-group"><label>URL de Imagen</label><input name="img" value="{{ producto.img if producto else '' }}" placeholder="https://..."></div>
      <div class="form-actions">
        <button type="submit" class="btn btn-primary"> Guardar</button>
        <a href="/admin" class="btn btn-ghost">Cancelar</a>
      </div>
    </form>
  </div>
</div>
"""

FORM_CLIENTE_CONTENT = """
<div style="max-width:460px;margin:0 auto">
  <div class="card">
    <h2 style="color:var(--dark);margin-bottom:1.25rem">{{ '✏ Editar Cliente' if cliente else '👤 Nuevo Cliente' }}</h2>
    <form method="post">
      {% if not cliente %}
      <div class="form-group"><label>Usuario</label><input name="username" required placeholder="Nombre de usuario"></div>
      {% endif %}
      <div class="form-group"><label>Correo Electrónico</label><input type="email" name="email" value="{{ cliente.email if cliente else '' }}" required placeholder="correo@ejemplo.com"></div>
      <div class="form-group"><label>Contraseña</label><input type="password" name="password" {% if cliente %}placeholder="Dejar en blanco para no cambiar"{% else %}required{% endif %}></div>
      <div class="form-group">
        <label>Rol</label>
        <select name="role">
          <option value="cliente" {{ 'selected' if cliente and cliente.role == 'cliente' }}>Cliente</option>
          <option value="admin"   {{ 'selected' if cliente and cliente.role == 'admin' }}>Admin</option>
        </select>
      </div>
      <div class="form-actions">
        <button type="submit" class="btn btn-primary"> Guardar</button>
        <a href="/admin/clientes" class="btn btn-ghost">Cancelar</a>
      </div>
    </form>
  </div>
</div>
"""

PERFIL_CONTENT = """
<div style="max-width:460px;margin:0 auto">
  <div class="card">
    <h2 style="color:var(--dark);margin-bottom:1rem"> Editar Perfil</h2>
    <div style="background:#fefaf2;padding:.85rem 1rem;border-radius:8px;border:1px solid var(--border);margin-bottom:1.25rem;font-size:.875rem">
      <p><strong style="color:var(--muted)">Usuario:</strong> {{ session.username }}</p>
      <p style="margin-top:.3rem"><strong style="color:var(--muted)">Correo:</strong> {{ current_email }}</p>
    </div>
    <form method="post">
      <div class="form-group"><label>Nuevo nombre de usuario</label><input type="text" name="new_username" value="{{ session.username }}"></div>
      <div class="form-group"><label>Correo electrónico</label><input type="email" name="email" value="{{ current_email }}" required></div>
      <div class="form-actions">
        <button type="submit" class="btn btn-primary"> Guardar</button>
        <a href="/" class="btn btn-ghost">Cancelar</a>
      </div>
    </form>
  </div>
</div>
"""

# ------------------------------------------------------------
# RUTAS
# ------------------------------------------------------------
@app.route('/')
def index():
    return render_base(INDEX_CONTENT)

@app.route('/contacto')
def contacto():
    return render_base(CONTACTO_CONTENT)

@app.route('/productos')
def productos():
    carrito = session.get('carrito', {})
    total = sum(i['precio'] * i['cantidad'] for i in carrito.values())
    return render_template_string(PRODUCTOS_TEMPLATE, productos=PRODUCTOS, total=total)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = USERS.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            flash(f'Bienvenido {username}', 'success')
            return redirect(url_for('admin_panel') if user['role'] == 'admin' else url_for('productos'))
        flash('Usuario o contraseña incorrectos', 'danger')
    return render_base(LOGIN_CONTENT)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip()
        password = request.form['password'].strip()
        if not username or not email or not password:
            flash('Todos los campos son obligatorios', 'danger')
        elif username in USERS:
            flash('El nombre de usuario ya existe', 'danger')
        else:
            USERS[username] = {'password': password, 'role': 'cliente', 'email': email}
            save_users(USERS)
            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
    return render_base(REGISTER_CONTENT)

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'warning')
    return redirect(url_for('index'))

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    username_actual = session['username']
    usuario_data = USERS.get(username_actual)
    if not usuario_data:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('logout'))
    if request.method == 'POST':
        new_username = request.form.get('new_username', '').strip()
        new_email    = request.form.get('email', '').strip()
        if not new_email:
            flash('El correo es obligatorio', 'danger')
            return redirect(url_for('perfil'))
        if new_username and new_username != username_actual:
            if new_username in USERS:
                flash('El nuevo nombre de usuario ya está en uso', 'danger')
                return redirect(url_for('perfil'))
            USERS[new_username] = USERS.pop(username_actual)
            USERS[new_username]['email'] = new_email
            session['username'] = new_username
            flash('Nombre de usuario actualizado', 'success')
        else:
            USERS[username_actual]['email'] = new_email
            flash('Correo actualizado', 'success')
        save_users(USERS)
        return redirect(url_for('perfil'))
    return render_base(PERFIL_CONTENT, current_email=usuario_data.get('email', ''))

# CARRITO
@app.route('/agregar', methods=['POST'])
def agregar():
    nombre   = request.form.get('nombre_producto')
    producto = next((p for p in PRODUCTOS if p['nombre'] == nombre), None)
    if not producto:
        flash('Producto no disponible', 'danger')
        return redirect(url_for('productos'))
    carrito = session.get('carrito', {})
    for item in carrito.values():
        if item['nombre'] == nombre:
            item['cantidad'] += 1
            break
    else:
        carrito[str(uuid.uuid4())] = {'nombre': nombre, 'precio': producto['precio'], 'cantidad': 1}
    session['carrito'] = carrito
    session.modified = True
    flash(f'{nombre} añadido al carrito', 'success')
    return redirect(url_for('productos'))

@app.route('/quitar/<item_id>', methods=['POST'])
def quitar(item_id):
    carrito = session.get('carrito', {})
    carrito.pop(item_id, None)
    session['carrito'] = carrito
    flash('Producto eliminado del carrito', 'info')
    return redirect(url_for('productos'))

@app.route('/vaciar', methods=['POST'])
def vaciar():
    session.pop('carrito', None)
    flash('¡Compra realizada! Gracias.', 'success')
    return redirect(url_for('productos'))

# ADMIN — PRODUCTOS
@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    return render_base(ADMIN_PANEL_CONTENT, productos=PRODUCTOS)

@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add():
    if request.method == 'POST':
        nuevo_id = max((p['id'] for p in PRODUCTOS), default=0) + 1
        PRODUCTOS.append({
            'id':       nuevo_id,
            'nombre':   request.form['nombre'].strip(),
            'precio':   float(request.form['precio']),
            'stock':    int(request.form['stock']),
            'categoria':request.form['categoria'],
            'peso':     request.form.get('peso', ''),
            'img':      request.form.get('img', 'https://via.placeholder.com/150'),
        })
        flash('Producto agregado', 'success')
        return redirect(url_for('admin_panel'))
    return render_base(FORM_PRODUCTO_CONTENT, producto=None)

@app.route('/admin/edit/<int:pid>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit(pid):
    producto = next((p for p in PRODUCTOS if p['id'] == pid), None)
    if not producto:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('admin_panel'))
    if request.method == 'POST':
        producto.update({
            'nombre':   request.form['nombre'].strip(),
            'precio':   float(request.form['precio']),
            'stock':    int(request.form['stock']),
            'categoria':request.form['categoria'],
            'peso':     request.form.get('peso', producto.get('peso', '')),
            'img':      request.form.get('img',  producto.get('img', '')),
        })
        flash('Producto actualizado', 'success')
        return redirect(url_for('admin_panel'))
    return render_base(FORM_PRODUCTO_CONTENT, producto=producto)

@app.route('/admin/delete/<int:pid>')
@login_required
@admin_required
def admin_delete(pid):
    global PRODUCTOS
    PRODUCTOS = [p for p in PRODUCTOS if p['id'] != pid]
    flash('Producto eliminado', 'success')
    return redirect(url_for('admin_panel'))

# ADMIN — CLIENTES
@app.route('/admin/clientes')
@login_required
@admin_required
def admin_clientes():
    return render_base(ADMIN_CLIENTES_CONTENT, usuarios=USERS)

@app.route('/admin/clientes/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_cliente_add():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip()
        password = request.form['password'].strip()
        role     = request.form['role']
        if not username or not email or not password:
            flash('Todos los campos son requeridos', 'danger')
        elif username in USERS:
            flash('El usuario ya existe', 'danger')
        else:
            USERS[username] = {'password': password, 'role': role, 'email': email}
            save_users(USERS)
            flash('Cliente agregado', 'success')
            return redirect(url_for('admin_clientes'))
    return render_base(FORM_CLIENTE_CONTENT, cliente=None)

@app.route('/admin/clientes/edit/<username>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_cliente_edit(username):
    if username not in USERS:
        flash('Cliente no encontrado', 'danger')
        return redirect(url_for('admin_clientes'))
    if request.method == 'POST':
        new_email    = request.form.get('email', '').strip()
        new_password = request.form.get('password', '').strip()
        role         = request.form['role']
        if not new_email:
            flash('El correo es obligatorio', 'danger')
            return redirect(url_for('admin_cliente_edit', username=username))
        USERS[username]['email'] = new_email
        if new_password:
            USERS[username]['password'] = new_password
        USERS[username]['role'] = role
        save_users(USERS)
        if session['username'] == username:
            session['role'] = role
        flash('Cliente actualizado', 'success')
        return redirect(url_for('admin_clientes'))
    return render_base(FORM_CLIENTE_CONTENT, cliente=USERS[username])

@app.route('/admin/clientes/delete/<username>')
@login_required
@admin_required
def admin_cliente_delete(username):
    if username == 'admin':
        flash('No se puede eliminar al superadministrador', 'danger')
    elif username == session['username']:
        flash('No puedes eliminar tu propia cuenta', 'danger')
    elif username in USERS:
        del USERS[username]
        save_users(USERS)
        flash('Cliente eliminado', 'success')
    else:
        flash('Cliente no encontrado', 'danger')
    return redirect(url_for('admin_clientes'))

# ------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip()
        password = request.form['password'].strip()
        role     = request.form['role']
        if not username or not email or not password:
            flash('Todos los campos son requeridos', 'danger')
        elif username in USERS:
            flash('El usuario ya existe', 'danger')
        else:
            USERS[username] = {'password': password, 'role': role, 'email': email}
            save_users(USERS)
            flash('Cliente agregado', 'success')
            return redirect(url_for('admin_clientes'))
    return render_base(FORM_CLIENTE_CONTENT, cliente=None)

@app.route('/admin/clientes/edit/<username>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_cliente_edit(username):
    if username not in USERS:
        flash('Cliente no encontrado', 'danger')
        return redirect(url_for('admin_clientes'))
    if request.method == 'POST':
        new_email    = request.form.get('email', '').strip()
        new_password = request.form.get('password', '').strip()
        role         = request.form['role']
        if not new_email:
            flash('El correo es obligatorio', 'danger')
            return redirect(url_for('admin_cliente_edit', username=username))
        USERS[username]['email'] = new_email
        if new_password:
            USERS[username]['password'] = new_password
        USERS[username]['role'] = role
        save_users(USERS)
        if session['username'] == username:
            session['role'] = role
        flash('Cliente actualizado', 'success')
        return redirect(url_for('admin_clientes'))
    return render_base(FORM_CLIENTE_CONTENT, cliente=USERS[username])

@app.route('/admin/clientes/delete/<username>')
@login_required
@admin_required
def admin_cliente_delete(username):
    if username == 'admin':
        flash('No se puede eliminar al superadministrador', 'danger')
    elif username == session['username']:
        flash('No puedes eliminar tu propia cuenta', 'danger')
    elif username in USERS:
        del USERS[username]
        save_users(USERS)
        flash('Cliente eliminado', 'success')
    else:
        flash('Cliente no encontrado', 'danger')
    return redirect(url_for('admin_clientes'))

# ------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
