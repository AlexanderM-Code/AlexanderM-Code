"""Genera los paneles SVG del README del perfil.

Uso:
    pip install fonttools brotli
    python tools/readme/build.py

Cada panel es un SVG animado con las fuentes recortadas e incrustadas
(Space Grotesk y JetBrains Mono, licencia OFL) y los íconos de Simple Icons
(CC0), así GitHub los muestra igual en cualquier computador.
Para cambiar un dato, edita las constantes de este archivo y vuelve a ejecutarlo.
"""
import base64
import html
import io
import json
import pathlib
import re

from fontTools import subset
from fontTools.ttLib import TTFont

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
SALIDA = RAIZ / "assets" / "readme"
ICONOS = json.loads((AQUI / "icons" / "icons.json").read_text())

# ---------- Paleta (la del README original: azul petróleo y cian) ----------
C = {
    "bg": "#0b1a20", "bg2": "#0f2027", "panel": "#12262e", "panel2": "#163039",
    "line": "#24414b", "line2": "#2f5562", "teal": "#2c5364",
    "cyan": "#4fc3f7", "cyan2": "#9be3ff", "ink": "#e8f3f6", "ink2": "#a9c3cb", "ink3": "#7b9aa4",
    "green": "#3fd68f", "amber": "#ffb74d", "red": "#ff6b6b", "tile": "#e8f3f6",
}
AJUSTE_COLOR = {"javascript": "#c9a800", "swagger": "#4f9a16", "react": "#149ec4", "openjdk": "#e76f00"}

FUENTES = {
    "SG5": "space-grotesk-latin-500-normal.woff2",
    "SG7": "space-grotesk-latin-700-normal.woff2",
    "JB4": "jetbrains-mono-latin-400-normal.woff2",
    "JB7": "jetbrains-mono-latin-700-normal.woff2",
}


def e(t: str) -> str:
    return html.escape(t, quote=True)


def fuente(nombre: str, texto: str) -> str:
    opts = subset.Options()
    opts.flavor = "woff2"
    f = TTFont(AQUI / "fonts" / FUENTES[nombre])
    s = subset.Subsetter(opts)
    s.populate(text=texto + " ")
    s.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff2"
    f.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


BASE_CSS = """
.sg{font-family:SG5,'Segoe UI',system-ui,sans-serif;font-weight:500}
.sgb{font-family:SG7,'Segoe UI',system-ui,sans-serif;font-weight:700}
.mono{font-family:JB4,ui-monospace,Consolas,monospace}
.monob{font-family:JB7,ui-monospace,Consolas,monospace;font-weight:700}
@keyframes blink{50%{opacity:0}}
@keyframes pulse{0%{transform:scale(1);opacity:.55}100%{transform:scale(2.6);opacity:0}}
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes type{from{width:0}}
@keyframes grow{from{transform:scaleY(0)}}
@keyframes draw{to{stroke-dashoffset:0}}
.cursor{animation:blink 1s steps(1) infinite}
.ping{transform-box:fill-box;transform-origin:center;animation:pulse 2s ease-out infinite}
.rise{opacity:0;animation:rise .6s ease-out forwards}
.bar{transform-box:fill-box;transform-origin:bottom;animation:grow .9s cubic-bezier(.2,.8,.2,1) both}
@media (prefers-reduced-motion:reduce){*{animation:none!important;opacity:1!important}}
"""


def documento(ancho: int, alto: int, etiqueta: str, cuerpo: str, css: str = "") -> str:
    texto = " ".join(html.unescape(t) for t in re.findall(r">([^<>]+)<", cuerpo)) + " ".join(
        html.unescape(t) for t in re.findall(r'data-t="([^"]+)"', cuerpo))
    usadas = {k for k in FUENTES if re.search(
        {"SG5": r'class="[^"]*\bsg\b', "SG7": r'class="[^"]*\bsgb\b', "JB4": r'class="[^"]*\bmono\b',
         "JB7": r'class="[^"]*\bmonob\b'}[k], cuerpo)}
    caras = "".join(
        f'@font-face{{font-family:{k};src:url(data:font/woff2;base64,{fuente(k, texto)}) format("woff2")}}'
        for k in sorted(usadas))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}" '
            f'role="img" aria-label="{e(etiqueta)}"><title>{e(etiqueta)}</title>'
            f'<style>{caras}{BASE_CSS}{css}</style>{cuerpo}</svg>\n')


def marco(ancho: int, alto: int, r: int = 14) -> str:
    return (f'<defs><pattern id="g" width="20" height="20" patternUnits="userSpaceOnUse">'
            f'<path d="M20 0H0V20" fill="none" stroke="{C["line"]}" stroke-opacity=".35"/></pattern>'
            f'<linearGradient id="bgx" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C["bg2"]}"/>'
            f'<stop offset="1" stop-color="{C["bg"]}"/></linearGradient></defs>'
            f'<rect width="{ancho}" height="{alto}" rx="{r}" fill="url(#bgx)"/>'
            f'<rect width="{ancho}" height="{alto}" rx="{r}" fill="url(#g)"/>'
            f'<rect x=".5" y=".5" width="{ancho - 1}" height="{alto - 1}" rx="{r}" fill="none" stroke="{C["line2"]}"/>')


def encabezado(x: int, y: int, titulo: str, comando: str, derecha: str = "", ancho: int = 940) -> str:
    return (f'<text x="{x}" y="{y}" class="monob" font-size="15" fill="{C["cyan"]}" letter-spacing="2">{e(titulo)}</text>'
            f'<text x="{x + 14 + len(titulo) * 10.6}" y="{y}" class="mono" font-size="13" fill="{C["ink3"]}">{e(comando)}</text>'
            + (f'<text x="{x + ancho}" y="{y}" text-anchor="end" class="mono" font-size="13" fill="{C["ink2"]}">{e(derecha)}</text>' if derecha else "")
            + f'<line x1="{x}" y1="{y + 16}" x2="{x + ancho}" y2="{y + 16}" stroke="{C["line2"]}"/>')


def icono(slug: str, x: float, y: float, t: float = 34, fondo: bool = True) -> str:
    i = ICONOS[slug]
    color = AJUSTE_COLOR.get(slug, "#" + i["hex"])
    esc = (t * 0.62) / 24
    off = (t - 24 * esc) / 2
    tile = f'<rect x="{x}" y="{y}" width="{t}" height="{t}" rx="7" fill="{C["tile"]}"/>' if fondo else ""
    return tile + f'<path transform="translate({x + off:.1f} {y + off:.1f}) scale({esc:.3f})" d="{i["path"]}" fill="{color}"/>'


def icono_custom(tipo: str, x: float, y: float, t: float = 34) -> str:
    tile = f'<rect x="{x}" y="{y}" width="{t}" height="{t}" rx="7" fill="{C["tile"]}"/>'
    if tipo == "powerbi":
        b = t * 0.14
        return tile + "".join(
            f'<rect x="{x + t * .24 + k * (b + 3):.1f}" y="{y + t * (0.62 - h):.1f}" width="{b:.1f}" height="{t * (h + .16):.1f}" rx="1.5" fill="{c}"/>'
            for k, (h, c) in enumerate([(.18, "#f2c811"), (.32, "#e8b600"), (.46, "#c99700")]))
    if tipo == "sql":
        cx, w = x + t / 2, t * .5
        return tile + (f'<g fill="none" stroke="#1f6f86" stroke-width="2.2"><ellipse cx="{cx}" cy="{y + t * .3}" rx="{w / 2}" ry="{t * .1}"/>'
                       f'<path d="M{cx - w / 2} {y + t * .3}v{t * .4}c0 {t * .13} {w} {t * .13} {w} 0v-{t * .4}"/>'
                       f'<path d="M{cx - w / 2} {y + t * .5}c0 {t * .13} {w} {t * .13} {w} 0"/></g>')
    if tipo == "java":
        return icono("openjdk", x, y, t)
    raise ValueError(tipo)


# ======================================================================
# 1. Portada
# ======================================================================
def portada() -> str:
    W, H = 1000, 470
    estado = [("API de CineX", "Render + MySQL en Aiven"),
              ("Observatorio de Salud", "GitHub Pages · datos mensuales"),
              ("casarendon.com", "cliente real")]
    filas = ""
    for k, (n, d) in enumerate(estado):
        y = 168 + k * 44
        filas += (f'<g class="rise" style="animation-delay:{1.6 + k * .25}s">'
                  f'<circle cx="694" cy="{y - 5}" r="5" fill="{C["green"]}"/><circle class="ping" cx="694" cy="{y - 5}" r="5" fill="{C["green"]}" style="animation-delay:{k * .6}s"/>'
                  f'<text x="710" y="{y}" class="sg" font-size="15" fill="{C["ink"]}">{e(n)}</text>'
                  f'<text x="710" y="{y + 18}" class="mono" font-size="11.5" fill="{C["ink3"]}">{e(d)}</text></g>')
    celdas = [("UBICACIÓN", "Medellín, Colombia"), ("FORMACIÓN", "Ingeniería de Software · VII"),
              ("PRÁCTICA", "Disponible desde ya"), ("MODALIDAD", "Presencial, híbrida o remota")]
    datos = "".join(
        f'<text x="{48 + k * 232}" y="418" class="monob" font-size="11" fill="{C["cyan"]}" letter-spacing="1.5">{e(a)}</text>'
        f'<text x="{48 + k * 232}" y="440" class="sg" font-size="15" fill="{C["ink"]}">{e(b)}</text>'
        for k, (a, b) in enumerate(celdas))
    cuerpo = (marco(W, H)
              + f'<rect x="0" y="0" width="{W}" height="40" rx="14" fill="{C["panel2"]}"/><rect x="0" y="26" width="{W}" height="14" fill="{C["panel2"]}"/>'
              + f'<line x1="0" y1="40" x2="{W}" y2="40" stroke="{C["line2"]}"/>'
              + "".join(f'<circle cx="{24 + k * 20}" cy="20" r="6" fill="{c}"/>' for k, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]))
              + f'<text x="{W / 2}" y="25" text-anchor="middle" class="mono" font-size="13" fill="{C["ink3"]}">alexander@medellin: ~/portafolio</text>'
              # prompt escrito
              + f'<clipPath id="tp"><rect x="48" y="66" width="220" height="24" style="animation:type 1.1s steps(14) .3s both"/></clipPath>'
              + f'<text x="48" y="84" class="mono" font-size="17" fill="{C["green"]}" clip-path="url(#tp)">$ <tspan fill="{C["ink"]}">whoami</tspan></text>'
              + f'<rect x="132" y="70" width="9" height="18" fill="{C["cyan"]}" class="cursor"/>'
              + f'<g class="rise" style="animation-delay:1.1s"><text x="44" y="160" class="sgb" font-size="62" fill="{C["ink"]}" letter-spacing="-1.5">Alexander</text>'
              + f'<text x="44" y="226" class="sgb" font-size="62" fill="{C["cyan"]}" letter-spacing="-1.5">Mejía Ospina</text></g>'
              + f'<g class="rise" style="animation-delay:1.35s"><text x="48" y="268" class="sg" font-size="18" fill="{C["ink2"]}">Ingeniería de Software · VII semestre · UCC, Medellín</text>'
              + f'<text x="48" y="296" class="sg" font-size="18" fill="{C["ink2"]}">Java y Spring Boot · Python y SQL · React</text></g>'
              + f'<g class="rise" style="animation-delay:1.5s"><rect x="48" y="320" width="420" height="38" rx="19" fill="{C["panel2"]}" stroke="{C["green"]}" stroke-opacity=".6"/>'
              + f'<circle cx="70" cy="339" r="5" fill="{C["green"]}"/><circle class="ping" cx="70" cy="339" r="5" fill="{C["green"]}"/>'
              + f'<text x="86" y="344.5" class="sg" font-size="15.5" fill="{C["ink"]}">Disponible desde ya para práctica empresarial</text></g>'
              # bloque de estado
              + f'<rect x="672" y="66" width="290" height="270" rx="10" fill="{C["panel"]}" stroke="{C["line2"]}"/>'
              + f'<text x="690" y="94" class="mono" font-size="13" fill="{C["green"]}">$ <tspan fill="{C["ink"]}">status --produccion</tspan></text>'
              + f'<line x1="672" y1="110" x2="962" y2="110" stroke="{C["line2"]}"/>'
              + f'<text x="690" y="136" class="monob" font-size="11" fill="{C["cyan"]}" letter-spacing="1.5">EN LÍNEA</text>'
              + filas
              + f'<line x1="672" y1="300" x2="962" y2="300" stroke="{C["line2"]}"/>'
              + f'<text x="690" y="323" class="mono" font-size="11.5" fill="{C["ink3"]}">vigilado con UptimeRobot · 5 min</text>'
              + f'<line x1="48" y1="388" x2="{W - 48}" y2="388" stroke="{C["line2"]}"/>'
              + datos)
    return documento(W, H, "Alexander Mejía Ospina, estudiante de Ingeniería de Software en la Universidad Cooperativa de Colombia, Medellín. "
                     "Backend con Java y Spring Boot, datos con Python y SQL, web con React. Disponible desde ya para práctica empresarial, presencial, híbrida o remota.",
                     cuerpo)


# ======================================================================
# 2. Botones
# ======================================================================
def boton(texto: str, primario: bool, simbolo: str) -> str:
    W = int(48 + len(texto) * 9.4 + 20)
    H = 44
    fondo = C["cyan"] if primario else C["panel"]
    tinta = C["bg"] if primario else C["ink"]
    borde = C["cyan"] if primario else C["line2"]
    cuerpo = (f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="8" fill="{fondo}" stroke="{borde}"/>'
              f'<text x="18" y="28" class="monob" font-size="14" fill="{C["bg"] if primario else C["cyan"]}">{e(simbolo)}</text>'
              f'<text x="42" y="28.5" class="sgb" font-size="15.5" fill="{tinta}">{e(texto)}</text>')
    return documento(W, H, texto, cuerpo)


# ======================================================================
# 3. Trayectoria como git log
# ======================================================================
def trayectoria() -> str:
    W, H = 1000, 330
    hitos = [
        ("2023", "Ingeniería de Software", "Universidad Cooperativa"),
        ("2025", "CineX v1.0 en equipo", "Java · Spring Boot · MySQL"),
        ("2025", "C++ Essentials 1", "Cisco Networking Academy"),
        ("2026", "Google Cloud · 4 insignias", "Load Balancing · App Dev"),
        ("2026", "Numi y Casa Rendón", "Flutter con IA · React"),
        ("2026", "CineX v2 + Observatorio", "en producción · CI"),
    ]
    x0, x1, yl = 60, 760, 180
    paso = (x1 - x0) / (len(hitos) - 1)
    nodos = ""
    for k, (anio, t, s) in enumerate(hitos):
        x = x0 + k * paso
        arriba = k % 2 == 0
        yt = 102 if arriba else 238
        delay = 0.4 + k * 0.35
        nodos += (f'<g class="rise" style="animation-delay:{delay:.2f}s">'
                  f'<line x1="{x}" y1="{yl}" x2="{x}" y2="{yt + (22 if arriba else -18)}" stroke="{C["line2"]}" stroke-dasharray="3 3"/>'
                  f'<circle cx="{x}" cy="{yl}" r="8" fill="{C["bg"]}" stroke="{C["cyan"]}" stroke-width="2.5"/>'
                  f'<text x="{x - 8}" y="{yt - 18}" class="monob" font-size="12" fill="{C["cyan"]}">{anio}</text>'
                  f'<text x="{x - 8}" y="{yt}" class="sgb" font-size="14.5" fill="{C["ink"]}">{e(t)}</text>'
                  f'<text x="{x - 8}" y="{yt + 17}" class="mono" font-size="11" fill="{C["ink3"]}">{e(s)}</text></g>')
    meta_x = 900
    cuerpo = (marco(W, H)
              + encabezado(30, 44, "TRAYECTORIA", "$ git log --graph --oneline", "2023 → práctica")
              + f'<line x1="{x0}" y1="{yl}" x2="{x1}" y2="{yl}" stroke="{C["cyan"]}" stroke-width="3" stroke-dasharray="{x1 - x0}" stroke-dashoffset="{x1 - x0}" style="animation:draw 2.2s ease-out .2s forwards"/>'
              + f'<line x1="{x1}" y1="{yl}" x2="{meta_x}" y2="{yl}" stroke="{C["amber"]}" stroke-width="3" stroke-dasharray="6 6"/>'
              + nodos
              + f'<g class="rise" style="animation-delay:2.6s"><circle cx="{meta_x}" cy="{yl}" r="10" fill="{C["amber"]}"/>'
              + f'<circle class="ping" cx="{meta_x}" cy="{yl}" r="10" fill="{C["amber"]}"/>'
              + f'<line x1="{meta_x}" y1="{yl - 10}" x2="{meta_x}" y2="148" stroke="{C["amber"]}" stroke-dasharray="3 3"/>'
              + f'<rect x="{meta_x - 70}" y="80" width="140" height="68" rx="8" fill="{C["panel2"]}" stroke="{C["amber"]}"/>'
              + f'<text x="{meta_x - 56}" y="104" class="monob" font-size="11" fill="{C["amber"]}" letter-spacing="1.5">SIGUIENTE</text>'
              + f'<text x="{meta_x - 56}" y="124" class="sgb" font-size="14.5" fill="{C["ink"]}">Práctica</text>'
              + f'<text x="{meta_x - 56}" y="140" class="sgb" font-size="14.5" fill="{C["ink"]}">empresarial</text></g>'
              + f'<circle r="5" fill="{C["cyan2"]}"><animateMotion dur="4s" repeatCount="indefinite" path="M{x0} {yl}H{meta_x}"/></circle>')
    return documento(W, H, "Trayectoria: 2023 Ingeniería de Software en la Universidad Cooperativa; 2025 CineX v1.0 en equipo y C++ Essentials 1 de Cisco; "
                     "2026 cuatro insignias de Google Cloud, Numi, Casa Rendón, CineX v2.0 y el Observatorio de Salud. Siguiente: práctica empresarial.",
                     cuerpo)


# ======================================================================
# 4. Tarjetas de proyecto
# ======================================================================
def tarjeta(etiqueta_estado: str, color_estado: str, tipo: str, titulo: str, dato: str, visual: str,
            stack: str, accion: str, aria: str) -> str:
    W, H = 490, 330
    cuerpo = (marco(W, H, 12)
              + f'<rect x="24" y="22" width="{len(etiqueta_estado) * 7.6 + 34}" height="24" rx="12" fill="{C["panel2"]}" stroke="{color_estado}" stroke-opacity=".7"/>'
              + f'<circle cx="38" cy="34" r="4" fill="{color_estado}"/><circle class="ping" cx="38" cy="34" r="4" fill="{color_estado}"/>'
              + f'<text x="49" y="38.5" class="monob" font-size="11" fill="{color_estado}" letter-spacing="1">{e(etiqueta_estado)}</text>'
              + f'<text x="{W - 24}" y="38.5" text-anchor="end" class="mono" font-size="11.5" fill="{C["ink3"]}">{e(tipo)}</text>'
              + f'<text x="24" y="84" class="sgb" font-size="26" fill="{C["ink"]}" letter-spacing="-.5">{e(titulo)}</text>'
              + f'<text x="24" y="108" class="sg" font-size="14" fill="{C["ink2"]}">{e(dato)}</text>'
              + visual
              + f'<line x1="24" y1="282" x2="{W - 24}" y2="282" stroke="{C["line2"]}"/>'
              + f'<text x="24" y="306" class="mono" font-size="11.5" fill="{C["ink3"]}">{e(stack)}</text>'
              + f'<text x="{W - 24}" y="306" text-anchor="end" class="monob" font-size="12" fill="{C["cyan"]}">{e(accion)} ↗</text>')
    return documento(W, H, aria, cuerpo)


def proyecto_observatorio() -> str:
    casos = [98, 2505, 1321, 25804, 1963, 1991, 5761, 6762, 6780, 27628, 4091, 3670, 4980, 2133, 1239, 2007]
    x0, y0, w, h = 24, 262, 442, 128
    bw = w / len(casos)
    barras = ""
    for k, v in enumerate(casos):
        bh = max(2, v / 28000 * h)
        caliente = v > 20000
        barras += (f'<rect class="bar" style="animation-delay:{.3 + k * .05:.2f}s" x="{x0 + k * bw + 3:.1f}" y="{y0 - bh:.1f}" width="{bw - 6:.1f}" height="{bh:.1f}" rx="2" '
                   f'fill="{C["amber"] if caliente else C["teal"]}"/>')
    vis = (f'<text x="24" y="132" class="mono" font-size="11" fill="{C["ink3"]}">casos de dengue por año · 2007–2022</text>'
           + barras
           + f'<text x="{x0 + 3 * bw + bw / 2:.0f}" y="{y0 - 25804 / 28000 * h - 6:.0f}" text-anchor="middle" class="monob" font-size="11" fill="{C["amber"]}">2010</text>'
           + f'<text x="{x0 + 9 * bw + bw / 2:.0f}" y="{y0 - 27628 / 28000 * h - 6:.0f}" text-anchor="middle" class="monob" font-size="11" fill="{C["amber"]}">2016</text>'
           + f'<line x1="24" y1="{y0}" x2="466" y2="{y0}" stroke="{C["line2"]}"/>')
    return tarjeta("EN VIVO", C["green"], "proyecto personal", "Observatorio de Salud",
                   "1,18 M casos del SIVIGILA en Antioquia: ETL, SQL y web", vis,
                   "Python · pandas · SQL · MySQL · FastAPI · CI", "ver en vivo",
                   "Observatorio de Salud Pública de Antioquia, en vivo: pipeline en Python y SQL sobre 1,18 millones de casos del SIVIGILA. "
                   "Gráfica de casos de dengue por año con epidemias en 2010 y 2016.")


def proyecto_cinex() -> str:
    lineas = [
        (C["green"], "$ ", C["ink"], "GET /showtimes/1/availability"),
        (C["ink3"], "", C["cyan2"], '{ "capacidad": 80, "vendidas": 78,'),
        (C["ink3"], "", C["cyan2"], '  "disponibles": 2 }'),
        (C["green"], "$ ", C["ink"], "POST /bookings  { sillas: 3 }"),
        (C["ink3"], "", C["red"], '409 "Solo quedan 2 sillas disponibles"'),
    ]
    vis = f'<rect x="24" y="124" width="442" height="140" rx="8" fill="{C["bg"]}" stroke="{C["line2"]}"/>'
    for k, (c1, p, c2, t) in enumerate(lineas):
        vis += (f'<text class="mono rise" style="animation-delay:{.4 + k * .45:.2f}s" x="40" y="{152 + k * 24}" font-size="12.5" fill="{c2}">'
                f'<tspan fill="{c1}">{e(p)}</tspan>{e(t)}</text>')
    return tarjeta("EN VIVO", C["green"], "equipo · v2.0 individual", "CineX",
                   "API REST en Spring Boot con reglas de negocio y 17 pruebas", vis,
                   "Java 21 · Spring Boot · MySQL · JUnit · Docker", "probar la API",
                   "CineX, en vivo: API REST en Java con Spring Boot y MySQL. Ejemplo: al pedir 3 sillas cuando quedan 2, responde 409. "
                   "17 pruebas automáticas. Versión 1.0 en equipo, versión 2.0 individual.")


def proyecto_numi() -> str:
    vis = (f'<rect x="24" y="124" width="442" height="140" rx="8" fill="{C["bg"]}" stroke="{C["line2"]}"/>'
           f'<text x="40" y="148" class="mono" font-size="11" fill="{C["amber"]}">✈ modo avión · sin internet</text>'
           f'<g class="rise" style="animation-delay:.5s"><rect x="250" y="160" width="196" height="34" rx="14" fill="{C["teal"]}"/>'
           f'<text x="266" y="182" class="sg" font-size="14" fill="{C["ink"]}">¿Cuánto es 7 × 8?</text></g>'
           f'<g class="rise" style="animation-delay:1.2s"><rect x="40" y="204" width="250" height="44" rx="14" fill="{C["panel2"]}" stroke="{C["line2"]}"/>'
           f'<text x="56" y="223" class="sg" font-size="14" fill="{C["ink"]}">7 × 8 = 56</text>'
           f'<text x="56" y="240" class="mono" font-size="10.5" fill="{C["ink3"]}">Gemma 2B + RAG en el celular</text></g>')
    return tarjeta("EN DESARROLLO", C["cyan"], "equipo", "Numi",
                   "App educativa con IA que funciona sin internet", vis,
                   "Flutter · Dart · SQLite · Gemma 2B · FastAPI", "ver detalles",
                   "Numi, en desarrollo, proyecto en equipo: app educativa en Flutter con un asistente de IA que corre en el celular sin internet. "
                   "Mi rol: arquitectura, pantallas de Ciencias Naturales, RAG offline y diseño responsive.")


def proyecto_casa() -> str:
    vis = (f'<rect x="24" y="124" width="442" height="140" rx="8" fill="#2a2116" stroke="{C["line2"]}"/>'
           f'<rect x="24" y="124" width="442" height="22" rx="8" fill="{C["panel2"]}"/><rect x="24" y="138" width="442" height="8" fill="{C["panel2"]}"/>'
           + "".join(f'<circle cx="{38 + k * 12}" cy="135" r="3.5" fill="{c}"/>' for k, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]))
           + f'<text x="245" y="139" text-anchor="middle" class="mono" font-size="10.5" fill="{C["ink3"]}">casarendon.com</text>'
           f'<text x="44" y="196" class="sgb" font-size="34" fill="#f3e6cf">Entre</text>'
           f'<text x="44" y="232" class="sgb" font-size="34" fill="#e0a64b">Sorbos</text>'
           f'<text x="210" y="190" class="sg" font-size="12.5" fill="#d8c9ad">Café de altura y vino artesanal</text>'
           f'<text x="210" y="208" class="sg" font-size="12.5" fill="#d8c9ad">Andes, Antioquia</text>'
           f'<rect x="210" y="222" width="132" height="26" rx="4" fill="#b5651d"/>'
           f'<text x="276" y="239.5" text-anchor="middle" class="monob" font-size="10" fill="#fff3e0">RESERVAR VISITA</text>')
    return tarjeta("CLIENTE REAL", C["amber"], "equipo · en producción", "Casa Rendón",
                   "Sitio en React para una marca de café y vino", vis,
                   "React · JavaScript · HTML · CSS", "visitar el sitio",
                   "Casa Rendón, cliente real en producción: sitio web en React de una marca de café y vino artesanal en Andes, Antioquia. "
                   "Mi rol: diseño y desarrollo del sitio.")


# ======================================================================
# 5. Stack y certificaciones
# ======================================================================
def stack() -> str:
    W, H = 1000, 470
    grupos = [
        ("BACKEND", [("java", "Java"), ("springboot", "Spring Boot"), ("python", "Python"), ("fastapi", "FastAPI")], "CineX, Observatorio"),
        ("DATOS", [("sql", "SQL"), ("mysql", "MySQL"), ("pandas", "pandas"), ("powerbi", "Power BI"), ("looker", "Looker"), ("jupyter", "Jupyter")], "Observatorio, Analítica de Datos"),
        ("WEB Y MÓVIL", [("html5", "HTML"), ("css", "CSS"), ("javascript", "JS"), ("react", "React"), ("flutter", "Flutter"), ("dart", "Dart")], "Casa Rendón, Numi"),
        ("CALIDAD Y DEVOPS", [("junit5", "JUnit"), ("pytest", "pytest"), ("postman", "Postman"), ("swagger", "Swagger"), ("docker", "Docker"), ("githubactions", "Actions"), ("git", "Git")], "CineX, Observatorio"),
    ]
    izq = ""
    y = 96
    for k, (g, items, donde) in enumerate(grupos):
        izq += (f'<text x="30" y="{y}" class="monob" font-size="11.5" fill="{C["cyan"]}" letter-spacing="1.5">{e(g)}</text>'
                f'<text x="{30 + len(g) * 8.6 + 12}" y="{y}" class="mono" font-size="11" fill="{C["ink3"]}">· {e(donde)}</text>')
        for j, (slug, nombre) in enumerate(items):
            x = 30 + j * 78
            d = .2 + k * .25 + j * .05
            ic = icono_custom(slug, x + 18, y + 12, 36) if slug in ("powerbi", "sql", "java") else icono(slug, x + 18, y + 12, 36)
            izq += (f'<g class="rise" style="animation-delay:{d:.2f}s">{ic}'
                    f'<text x="{x + 36}" y="{y + 66}" text-anchor="middle" class="sg" font-size="11.5" fill="{C["ink2"]}">{e(nombre)}</text></g>')
        y += 92
    certs = [
        ("googlecloud", "Cloud Load Balancing", "Google Cloud · mar. 2026"),
        ("googlecloud", "App Dev Environment", "Google Cloud · abr. 2026"),
        ("googlecloud", "Computing Foundations ×2", "Google Cloud · 2026"),
        ("cplusplus", "C++ Essentials 1", "Cisco · oct. 2025"),
        ("java", "Diplomados Java y JavaScript", "Politécnico de Colombia"),
    ]
    der = ""
    for k, (slug, n, d) in enumerate(certs):
        yy = 92 + k * 58
        ic = icono_custom("java", 640, yy, 34) if slug == "java" else icono(slug, 640, yy, 34)
        der += (f'<g class="rise" style="animation-delay:{.4 + k * .15:.2f}s">{ic}'
                f'<text x="686" y="{yy + 15}" class="sgb" font-size="14" fill="{C["ink"]}">{e(n)}</text>'
                f'<text x="686" y="{yy + 32}" class="mono" font-size="11" fill="{C["ink3"]}">{e(d)}</text>'
                f'<text x="966" y="{yy + 22}" text-anchor="end" class="monob" font-size="13" fill="{C["green"]}">✓</text></g>')
    numeros = [("17", "pruebas JUnit"), ("26", "solicitudes"), ("1,18 M", "registros")]
    nums = "".join(
        f'<text x="{640 + k * 112}" y="418" class="monob" font-size="24" fill="{C["cyan"]}">{e(a)}</text>'
        f'<text x="{640 + k * 112}" y="438" class="mono" font-size="10.5" fill="{C["ink3"]}">{e(b)}</text>'
        for k, (a, b) in enumerate(numeros))
    cuerpo = (marco(W, H)
              + encabezado(30, 44, "STACK", "$ cat stack.txt", "", 560)
              + f'<line x1="610" y1="24" x2="610" y2="{H - 24}" stroke="{C["line2"]}"/>'
              + encabezado(640, 44, "CERTIFICACIONES", "", "verificables", 330)
              + izq + der
              + f'<line x1="640" y1="384" x2="970" y2="384" stroke="{C["line2"]}"/>'
              + nums)
    return documento(W, H, "Stack: backend con Java, Spring Boot, Python y FastAPI; datos con SQL, MySQL, pandas, Power BI, Looker Studio y Jupyter; "
                     "web y móvil con HTML, CSS, JavaScript, React, Flutter y Dart; calidad y DevOps con JUnit, pytest, Postman, Swagger, Docker, GitHub Actions y Git. "
                     "Certificaciones: Google Cloud Implementing Cloud Load Balancing for Compute Engine, Set Up an App Dev Environment, "
                     "dos Google Cloud Computing Foundations, C++ Essentials 1 de Cisco y diplomados en Java y JavaScript del Politécnico de Colombia.",
                     cuerpo)


# ======================================================================
# 6. Contribuciones (encabezado) y cierre
# ======================================================================
def contribuciones() -> str:
    W, H = 1000, 78
    cuerpo = (marco(W, H)
              + f'<text x="30" y="36" class="monob" font-size="15" fill="{C["cyan"]}" letter-spacing="2">CONTRIBUCIONES</text>'
              + f'<text x="30" y="58" class="sg" font-size="14" fill="{C["ink2"]}">Mi actividad real del último año en GitHub, actualizada cada 12 horas.</text>'
              + f'<text x="970" y="47" text-anchor="end" class="mono" font-size="13" fill="{C["ink3"]}">$ git log --since="1 year"</text>')
    return documento(W, H, "Contribuciones: mi actividad real del último año en GitHub.", cuerpo)


def cierre() -> str:
    W, H = 1000, 250
    cuerpo = (marco(W, H)
              + f'<text x="48" y="58" class="mono" font-size="15" fill="{C["green"]}">$ <tspan fill="{C["ink"]}">./contratar --practicante</tspan></text>'
              + f'<rect x="300" y="44" width="9" height="18" fill="{C["cyan"]}" class="cursor"/>'
              + f'<text x="46" y="122" class="sgb" font-size="42" fill="{C["ink"]}" letter-spacing="-1">¿Tu equipo necesita</text>'
              + f'<text x="46" y="168" class="sgb" font-size="42" fill="{C["cyan"]}" letter-spacing="-1">un practicante?</text>'
              + f'<text x="48" y="206" class="sg" font-size="15.5" fill="{C["ink2"]}">Desarrollo de software o análisis de datos · disponible desde ya</text>'
              + f'<text x="48" y="230" class="monob" font-size="16" fill="{C["amber"]}">alexmejia0112@gmail.com</text>'
              + f'<g transform="translate(760 70)">'
              + f'<rect width="190" height="140" rx="10" fill="{C["panel"]}" stroke="{C["line2"]}"/>'
              + f'<text x="18" y="32" class="monob" font-size="11" fill="{C["cyan"]}" letter-spacing="1.5">BUSCO</text>'
              + f'<text x="18" y="60" class="sgb" font-size="16" fill="{C["ink"]}">Desarrollo de</text>'
              + f'<text x="18" y="80" class="sgb" font-size="16" fill="{C["ink"]}">software o datos</text>'
              + f'<circle cx="24" cy="116" r="5" fill="{C["green"]}"/><circle class="ping" cx="24" cy="116" r="5" fill="{C["green"]}"/>'
              + f'<text x="38" y="120.5" class="sg" font-size="13" fill="{C["ink"]}">Medellín · remoto</text></g>')
    return documento(W, H, "¿Tu equipo necesita un practicante? Desarrollo de software o análisis de datos, disponible desde ya. alexmejia0112@gmail.com", cuerpo)


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    archivos = {
        "portada.svg": portada(),
        "btn-portafolio.svg": boton("Ver portafolio", True, ">_"),
        "btn-cv.svg": boton("Hoja de vida", False, "[]"),
        "btn-cv-datos.svg": boton("Hoja de vida · Datos", False, "[]"),
        "btn-linkedin.svg": boton("LinkedIn", False, "in"),
        "btn-correo.svg": boton("Correo", False, "@"),
        "trayectoria.svg": trayectoria(),
        "proyecto-observatorio.svg": proyecto_observatorio(),
        "proyecto-cinex.svg": proyecto_cinex(),
        "proyecto-numi.svg": proyecto_numi(),
        "proyecto-casa-rendon.svg": proyecto_casa(),
        "stack.svg": stack(),
        "contribuciones.svg": contribuciones(),
        "cierre.svg": cierre(),
    }
    for nombre, svg in archivos.items():
        (SALIDA / nombre).write_text(svg, encoding="utf-8")
        print(f"{nombre:28s} {len(svg) / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
