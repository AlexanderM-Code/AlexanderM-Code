"""Genera los paneles en pixel art del README del perfil.

Uso:
    pip install fonttools brotli
    python tools/readme/build.py

Cada panel es un SVG animado con las fuentes recortadas e incrustadas
(Tiny5, Space Grotesk y JetBrains Mono, licencia OFL) y los íconos
de Simple Icons (CC0), así GitHub los muestra igual en cualquier equipo.
Para cambiar un dato, edítalo aquí y vuelve a ejecutar el script.
"""
import base64
import html
import io
import json
import pathlib
import random
import re

from fontTools import subset
from fontTools.ttLib import TTFont

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
SALIDA = RAIZ / "assets" / "readme"
ICONOS = json.loads((AQUI / "icons" / "icons.json").read_text())
random.seed(7)

# ---------- Paleta: noche en Medellín, azul petróleo y cian ----------
C = {
    "bg": "#0a1820", "panel": "#10242d", "panel2": "#163240", "line": "#24414b", "line2": "#2f5a68",
    "cyan": "#4fc3f7", "cyan2": "#9be3ff", "ink": "#eaf4f7", "ink2": "#a9c3cb", "ink3": "#7d9ca6",
    "green": "#3fd68f", "amber": "#ffb74d", "amber2": "#ffd28a", "red": "#ff6b6b", "tile": "#eaf4f7",
    "sky": ["#071223", "#0a1830", "#0e2140", "#132b4d", "#183859", "#1f4664"],
    "mont1": "#123543", "mont2": "#0d2833", "city": "#0a1d26", "ground": "#0b1419", "grass": "#2f7a5a",
}
AJUSTE_COLOR = {"javascript": "#c9a800", "swagger": "#4f9a16", "react": "#149ec4", "openjdk": "#e76f00"}

FUENTES = {
    "PX": ("tiny5-latin-400-normal.woff2", r'class="[^"]*\bpx\b'),
    "SG5": ("space-grotesk-latin-500-normal.woff2", r'class="[^"]*\bsg\b'),
    "SG7": ("space-grotesk-latin-700-normal.woff2", r'class="[^"]*\bsgb\b'),
    "JB4": ("jetbrains-mono-latin-400-normal.woff2", r'class="[^"]*\bmono\b'),
    "JB7": ("jetbrains-mono-latin-700-normal.woff2", r'class="[^"]*\bmonob\b'),
}

BASE_CSS = """
.px{font-family:PX,'Courier New',monospace;font-weight:400}
.sg{font-family:SG5,'Segoe UI',system-ui,sans-serif;font-weight:500}
.sgb{font-family:SG7,'Segoe UI',system-ui,sans-serif;font-weight:700}
.mono{font-family:JB4,ui-monospace,Consolas,monospace}
.monob{font-family:JB7,ui-monospace,Consolas,monospace;font-weight:700}
.pix{shape-rendering:crispEdges}
@keyframes blink{50%{opacity:0}}
@keyframes tw{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes win{0%,60%{opacity:1}70%,90%{opacity:.15}}
@keyframes led{0%,100%{opacity:1}50%{opacity:.35}}
@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@keyframes grow{from{transform:scaleY(0)}}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}
.cursor{animation:blink 1s steps(1) infinite}
.tw{animation:tw 3s steps(3) infinite}
.win{animation:win 7s steps(1) infinite}
.led{animation:led 1.6s steps(2) infinite}
.rise{opacity:0;animation:rise .5s steps(4) forwards}
.bar{transform-box:fill-box;transform-origin:bottom;animation:grow .9s steps(6) both}
.bob{animation:bob 1.8s steps(2) infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important;opacity:1!important}}
"""


def e(t: str) -> str:
    return html.escape(t, quote=True)


def fuente(nombre: str, texto: str) -> str:
    opts = subset.Options()
    opts.flavor = "woff2"
    f = TTFont(AQUI / "fonts" / FUENTES[nombre][0])
    s = subset.Subsetter(opts)
    s.populate(text=texto + " ")
    s.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff2"
    f.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def documento(ancho: int, alto: int, etiqueta: str, cuerpo: str) -> str:
    texto = " ".join(html.unescape(t) for t in re.findall(r">([^<>]+)<", cuerpo))
    caras = "".join(
        f'@font-face{{font-family:{k};src:url(data:font/woff2;base64,{fuente(k, texto)}) format("woff2")}}'
        for k, (_, patron) in FUENTES.items() if re.search(patron, cuerpo))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}" '
            f'role="img" aria-label="{e(etiqueta)}"><title>{e(etiqueta)}</title>'
            f'<style>{caras}{BASE_CSS}</style>{cuerpo}</svg>\n')


# ---------------------------------------------------------------- pixel art
def r(x, y, w, h, c, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"{extra}/>'


def marco(x, y, w, h, fondo, borde, s=4, sombra=True):
    """Caja con esquinas escalonadas, borde grueso y sombra dura."""
    out = '<g class="pix">'
    if sombra:
        out += r(x + s, y + h, w - 2 * s, s, "#050d12") + r(x + w, y + s, s, h - s, "#050d12")
    out += r(x + s, y, w - 2 * s, h, borde) + r(x, y + s, w, h - 2 * s, borde)
    out += r(x + 2 * s, y + s, w - 4 * s, h - 2 * s, fondo) + r(x + s, y + 2 * s, w - 2 * s, h - 4 * s, fondo)
    return out + "</g>"


def panel(W, H):
    return (f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>'
            + marco(0, 0, W - 4, H - 4, C["panel"], C["line2"], 4, True))


def sprite(mapa, paleta, x, y, s):
    filas = mapa.strip("\n").split("\n")
    ancho = len(filas[0])
    assert all(len(f) == ancho for f in filas), "sprite irregular"
    out = f'<g class="pix" transform="translate({x} {y})">'
    for j, fila in enumerate(filas):
        i = 0
        while i < ancho:
            ch = fila[i]
            if ch == ".":
                i += 1
                continue
            k = i
            while k < ancho and fila[k] == ch:
                k += 1
            out += r(i * s, j * s, (k - i) * s, s, paleta[ch])
            i = k
    return out + "</g>"


ALEX = """
....HHHHHH....
...HHHHHHHH...
..HHHHHHHHHH..
..HHHSHHSHHH..
..HSSSSSSSSH..
...SEWSSEWS...
...SSSSSSSS...
...SSSsSSSS...
....SSMMSS....
.....SSSS.....
...TTTTTTTT...
..TTTTTTTTTT..
.TTLLLLLLLLTT.
.TTLLLcLLLLTT.
.SSLLLLLLLLSS.
...LLLLLLLL...
...JJJJJJJJ...
...JJJjjJJJ...
...JJJ..JJJ...
...JJJ..JJJ...
..BBBB..BBBB..
"""
ALEX_SALUDO = """
....HHHHHH......SS
...HHHHHHHH.....SS
..HHHHHHHHHH....S.
..HHHSHHSHHH...TT.
..HSSSSSSSSH..TT..
...SEWSSEWS..TT...
...SSSSSSSS.TT....
...SSSsSSSSTT.....
....SSMMSSTT......
.....SSSSTT.......
...TTTTTTTT.......
..TTTTTTTTT.......
.TTTTTTTTTT.......
.TTTTTTTTTT.......
.SSTTTTTTTT.......
...TTTTTTTT.......
...JJJJJJJJ.......
...JJJjjJJJ.......
...JJJ..JJJ.......
...JJJ..JJJ.......
..BBBB..BBBB......
"""
PALETA_ALEX = {"H": "#1a120d", "S": "#c98e64", "s": "#a8724e", "E": "#1a120d", "W": "#ffffff", "M": "#8a4b3a",
               "T": "#1c1f24", "L": "#b7c4cc", "c": "#4fc3f7", "J": "#2c4a7a", "j": "#213860", "B": "#0e0e10"}


def cielo(W, H, y0=0, opacidad=1.0):
    bandas = C["sky"]
    alto = (H - y0) / len(bandas)
    return (f'<g class="pix" opacity="{opacidad}">'
            + "".join(r(0, round(y0 + k * alto), W, round(alto) + 1, c) for k, c in enumerate(bandas)) + "</g>")


def estrellas(W, H, n=38, evitar=None, evitar2=None):
    out = ""
    for _ in range(n):
        x, y = random.randrange(10, W - 10), random.randrange(8, H)
        if any(z and z[0] < x < z[2] and z[1] < y < z[3] for z in (evitar, evitar2)):
            continue
        t = random.choice([2, 3, 3, 4])
        d = random.random() * 3
        out += r(x, y, t, t, random.choice(["#ffffff", "#cdeeff", "#ffe7b3"]),
                 f' class="tw pix" style="animation-delay:{d:.1f}s"')
    return out


def montanas(W, base, alto, color, paso, semilla):
    rnd = random.Random(semilla)
    out = '<g class="pix">'
    h = alto * .5
    for x in range(0, W, paso):
        h = max(alto * .2, min(alto, h + rnd.choice([-1, 0, 1, 1, -1]) * paso * .9))
        out += r(x, base - round(h), paso, round(h) + 2, color)
    return out + "</g>"


def comuna(x0, x1, base, semilla):
    """Casitas de ladera con ventanas encendidas."""
    rnd = random.Random(semilla)
    out = '<g class="pix">'
    x = x0
    while x < x1:
        w = rnd.choice([16, 20, 24])
        h = rnd.choice([12, 16, 20])
        y = base - h - rnd.choice([0, 4, 8])
        out += r(x, y, w, h + 12, rnd.choice(["#173a46", "#1b4553", "#14323d"]))
        out += r(x, y - 4, w, 4, rnd.choice(["#7a3b2e", "#8b4a35", "#5e2f27"]))
        if rnd.random() < .7:
            d = rnd.random() * 7
            out += r(x + 4, y + 4, 4, 4, C["amber"], f' class="win" style="animation-delay:{d:.1f}s"')
        if w > 16 and rnd.random() < .5:
            out += r(x + w - 8, y + 4, 4, 4, C["amber2"])
        x += w + rnd.choice([0, 4])
    return out + "</g>"


def edificios(x0, x1, base, semilla, opacidad=1.0):
    rnd = random.Random(semilla)
    out = f'<g class="pix" opacity="{opacidad}">'
    x = x0
    while x < x1:
        w = rnd.choice([28, 36, 44])
        h = rnd.choice([60, 80, 100, 120, 70])
        out += r(x, base - h, w, h, C["city"])
        for wy in range(base - h + 8, base - 8, 12):
            for wx in range(x + 6, x + w - 6, 10):
                if rnd.random() < .35:
                    d = rnd.random() * 7
                    out += r(wx, wy, 4, 5, C["amber"] if rnd.random() < .7 else C["cyan2"],
                             f' class="win" style="animation-delay:{d:.1f}s"' if rnd.random() < .4 else "")
        x += w + rnd.choice([4, 8, 12])
    return out + "</g>"


def metrocable(xa, ya, xb, yb, n=3, dur=14):
    out = (f'<line x1="{xa}" y1="{ya}" x2="{xb}" y2="{yb}" stroke="#5c7d88" stroke-width="2"/>'
           + r(xa - 6, ya, 12, 60, "#2a4752", ' class="pix"') + r(xb - 6, yb, 12, 80, "#2a4752", ' class="pix"'))
    for k in range(n):
        out += ('<g><g class="pix">' + r(-1, 0, 2, 8, "#5c7d88") + r(-10, 8, 20, 14, "#e8eef0")
                + r(-8, 11, 6, 5, "#4fc3f7") + r(2, 11, 6, 5, "#4fc3f7") + r(-10, 19, 20, 3, "#ffb74d") + "</g>"
                f'<animateMotion dur="{dur}s" repeatCount="indefinite" begin="-{k * dur / n:.1f}s" path="M{xa} {ya}L{xb} {yb}"/></g>')
    return out


def led(x, y, color, s=8, delay=0.0):
    return r(x, y, s, s, color, f' class="led pix" style="animation-delay:{delay:.1f}s"')


def icono(slug, x, y, t=34):
    i = ICONOS[slug]
    color = AJUSTE_COLOR.get(slug, "#" + i["hex"])
    esc = (t * .62) / 24
    off = (t - 24 * esc) / 2
    return (marco(x, y, t, t, C["tile"], "#9fb7c0", 3, False)
            + f'<path transform="translate({x + off:.1f} {y + off:.1f}) scale({esc:.3f})" d="{i["path"]}" fill="{color}"/>')


def icono_custom(tipo, x, y, t=34):
    base = marco(x, y, t, t, C["tile"], "#9fb7c0", 3, False)
    if tipo == "powerbi":
        b = round(t * .14)
        return base + "".join(
            r(round(x + t * .24 + k * (b + 3)), round(y + t * (.62 - h)), b, round(t * (h + .16)), c, ' class="pix"')
            for k, (h, c) in enumerate([(.18, "#f2c811"), (.32, "#e8b600"), (.46, "#c99700")]))
    if tipo == "sql":
        cx, w = x + t / 2, t * .5
        return base + (f'<g fill="none" stroke="#1f6f86" stroke-width="2.2"><ellipse cx="{cx}" cy="{y + t * .3}" rx="{w / 2}" ry="{t * .1}"/>'
                       f'<path d="M{cx - w / 2} {y + t * .3}v{t * .4}c0 {t * .13} {w} {t * .13} {w} 0v-{t * .4}"/>'
                       f'<path d="M{cx - w / 2} {y + t * .5}c0 {t * .13} {w} {t * .13} {w} 0"/></g>')
    if tipo == "java":
        return icono("openjdk", x, y, t)
    raise ValueError(tipo)


def titulo_panel(x, y, titulo, sub="", derecha="", ancho=930):
    return (f'<text x="{x}" y="{y}" class="px" font-size="24" fill="{C["amber"]}" letter-spacing="1">{e(titulo)}</text>'
            + (f'<text x="{x + len(titulo) * 16 + 22}" y="{y - 2}" class="sg" font-size="14.5" fill="{C["ink2"]}">{e(sub)}</text>' if sub else "")
            + (f'<text x="{x + ancho}" y="{y - 1}" text-anchor="end" class="px" font-size="16" fill="{C["ink"]}">{e(derecha)}</text>' if derecha else ""))


# ======================================================================
# 1. Portada: Medellín de noche
# ======================================================================
def portada():
    W, H = 1000, 470
    suelo = 372
    hud = ""
    estado = [("API de CineX", "Render + MySQL"), ("Observatorio", "GitHub Pages"), ("casarendon.com", "cliente real")]
    for k, (n, d) in enumerate(estado):
        y = 86 + k * 28
        hud += (led(718, y - 9, C["green"], 8, k * .4)
                + f'<text x="734" y="{y}" class="sgb" font-size="13.5" fill="{C["ink"]}">{e(n)}</text>'
                + f'<text x="950" y="{y}" text-anchor="end" class="mono" font-size="10.5" fill="{C["ink3"]}">{e(d)}</text>')
    celdas = [("UBICACIÓN", "Medellín, Colombia"), ("FORMACIÓN", "Ingeniería de Software · VII"),
              ("PRÁCTICA", "Disponible desde ya"), ("MODALIDAD", "Presencial, híbrida o remota")]
    datos = "".join(
        f'<text x="{48 + k * 232}" y="{suelo + 44}" class="px" font-size="16" fill="{C["amber"]}" letter-spacing="1">{e(a)}</text>'
        f'<text x="{48 + k * 232}" y="{suelo + 66}" class="sg" font-size="15" fill="{C["ink"]}">{e(b)}</text>'
        for k, (a, b) in enumerate(celdas))
    luna = ('<g class="pix">' + r(612, 44, 24, 8, "#fff2c9") + r(604, 52, 40, 24, "#fff2c9") + r(612, 76, 24, 8, "#fff2c9")
            + r(620, 56, 8, 8, "#f2dca0") + r(628, 68, 6, 6, "#f2dca0") + "</g>")
    cuerpo = (cielo(W, suelo)
              + estrellas(W, 200, 46, (690, 26, 975, 175), (30, 40, 690, 260))
              + luna
              + montanas(W, suelo - 40, 140, C["mont1"], 20, 3)
              + montanas(W, suelo - 20, 90, C["mont2"], 16, 11)
              + comuna(0, 300, suelo - 34, 5)
              + comuna(640, 1000, suelo - 30, 9)
              + metrocable(150, 276, 620, 300, 3, 16)
              + edificios(330, 640, suelo, 21)
              + r(0, suelo, W, H - suelo, C["ground"], ' class="pix"') + r(0, suelo, W, 6, C["grass"], ' class="pix"')
              + r(0, suelo + 6, W, 2, "#1d5a43", ' class="pix"')
              # título
              + '<g class="rise" style="animation-delay:.2s">'
              + f'<text x="46" y="98" class="px" font-size="64" fill="#030a14" opacity=".7">ALEXANDER</text>'
              + f'<text x="42" y="94" class="px" font-size="64" fill="{C["ink"]}">ALEXANDER</text>'
              + f'<text x="46" y="170" class="px" font-size="64" fill="#030a14" opacity=".7">MEJÍA OSPINA</text>'
              + f'<text x="42" y="166" class="px" font-size="64" fill="{C["cyan"]}">MEJÍA OSPINA</text></g>'
              + f'<g class="rise" style="animation-delay:.5s"><text x="46" y="200" class="sg" font-size="17" fill="{C["ink"]}">Estudiante de Ingeniería de Software · Universidad Cooperativa de Colombia</text></g>'
              + '<g class="rise" style="animation-delay:.7s">' + marco(44, 214, 432, 38, "#0b1f2a", C["green"], 4, True)
              + led(62, 229, C["green"], 8) + f'<text x="80" y="238" class="sgb" font-size="15" fill="{C["ink"]}">Disponible desde ya para práctica empresarial</text></g>'
              # HUD de estado
              + marco(700, 30, 266, 138, "#0b1f2a", C["line2"], 4, True)
              + f'<text x="718" y="56" class="px" font-size="16" fill="{C["cyan"]}" letter-spacing="1">EN LÍNEA</text>'
              + f'<text x="950" y="56" text-anchor="end" class="mono" font-size="10.5" fill="{C["ink3"]}">UptimeRobot · 5 min</text>'
              + hud
              # Alexander
              + f'<g class="bob">{sprite(ALEX, PALETA_ALEX, 880, suelo - 21 * 5, 5)}</g>'
              + datos)
    return documento(W, H, "Alexander Mejía Ospina, estudiante de Ingeniería de Software en la Universidad Cooperativa de Colombia, Medellín. "
                     "Disponible desde ya para práctica empresarial, presencial, híbrida o remota. En línea: API de CineX, Observatorio de Salud y casarendon.com.",
                     cuerpo)


# ======================================================================
# 2. Botones
# ======================================================================
def boton(texto, primario):
    W = int(44 + len(texto) * 9.6 + 8)
    H = 46
    fondo = C["amber"] if primario else C["panel2"]
    borde = C["amber2"] if primario else C["line2"]
    tinta = "#1a120d" if primario else C["ink"]
    cuadro = "#1a120d" if primario else C["cyan"]
    cuerpo = (marco(0, 0, W - 4, H - 4, fondo, borde, 3, True)
              + r(16, 17, 8, 8, cuadro, ' class="pix"')
              + f'<text x="34" y="27" class="sgb" font-size="15.5" fill="{tinta}">{e(texto)}</text>')
    return documento(W, H, texto, cuerpo)


# ======================================================================
# 3. Trayectoria: línea del metro
# ======================================================================
def trayectoria():
    W, H = 1000, 360
    hitos = [
        ("2023", "Ingeniería de Software", "Universidad Cooperativa"),
        ("2025", "CineX v1.0 en equipo", "Java · Spring Boot · MySQL"),
        ("2025", "C++ Essentials 1", "Cisco Networking Academy"),
        ("2026", "Google Cloud", "4 insignias"),
        ("2026", "Numi y Casa Rendón", "Flutter con IA · React"),
        ("2026", "En producción", "CineX v2 · Observatorio"),
    ]
    yv = 196
    x0, x1, meta = 70, 790, 920
    paso = (x1 - x0) / (len(hitos) - 1)
    via = '<g class="pix">'
    for x in range(40, W - 40, 70):
        via += r(x, yv + 12, 14, H - yv - 40, "#173540") + r(x - 4, yv + 12, 22, 6, "#1d4350")
    via += r(30, yv, W - 64, 12, "#2a4f5c") + r(30, yv + 2, W - 64, 3, "#7fa2ad") + "</g>"
    est = ""
    for k, (anio, t, s) in enumerate(hitos):
        x = round(x0 + k * paso)
        arriba = k % 2 == 0
        cy = 86 if arriba else 250
        ancho = round(max(66 + len(t) * 7.9, 26 + len(s) * 6.7))
        conector = (r(x - 2, cy + 50, 4, yv - 10 - (cy + 50), C["line2"], ' class="pix"') if arriba
                    else r(x - 2, yv + 14, 4, cy - (yv + 14), C["line2"], ' class="pix"'))
        est += (f'<g class="rise" style="animation-delay:{.2 + k * .25:.2f}s">' + conector
                + marco(x - 12, yv - 10, 24, 24, C["ink"], C["cyan"], 3, False)
                + r(x - 4, yv - 2, 8, 8, C["cyan"], ' class="pix"')
                + marco(x - 14, cy, ancho, 50, "#0b1f2a", C["line2"], 3, True)
                + r(x - 11, cy + 3, 4, 44, C["amber"], ' class="pix"')
                + f'<text x="{x + 2}" y="{cy + 20}" class="px" font-size="16" fill="{C["amber"]}">{anio}</text>'
                + f'<text x="{x + 50}" y="{cy + 20}" class="sgb" font-size="13" fill="{C["ink"]}">{e(t)}</text>'
                + f'<text x="{x + 2}" y="{cy + 38}" class="mono" font-size="10.5" fill="{C["ink3"]}">{e(s)}</text></g>')
    tren = ('<g class="pix">' + r(0, 0, 76, 26, "#e8eef0") + r(0, 18, 76, 4, C["green"]) + r(70, 4, 6, 14, "#c7d2d6")
            + "".join(r(8 + k * 16, 5, 10, 9, C["cyan"]) for k in range(4)) + r(-4, 26, 84, 4, "#33424a")
            + r(8, 30, 8, 4, "#111") + r(60, 30, 8, 4, "#111") + "</g>")
    cuerpo = (panel(W, H)
              + titulo_panel(32, 50, "TRAYECTORIA", "Línea A: de la universidad a la práctica", "2023 → PRÁCTICA")
              + via + est
              + f'<g><g transform="translate(0 {yv - 34})">{tren}</g>'
              + f'<animateTransform attributeName="transform" type="translate" values="{x0 - 40} 0;{meta - 80} 0;{meta - 80} 0" keyTimes="0;.85;1" dur="9s" repeatCount="indefinite"/></g>'
              + '<g class="rise" style="animation-delay:1.8s">' + r(meta - 2, 128, 4, yv - 128, C["amber"], ' class="pix"')
              + marco(meta - 62, 72, 124, 58, "#2a1f0b", C["amber"], 4, True)
              + f'<text x="{meta}" y="94" text-anchor="middle" class="px" font-size="16" fill="{C["amber"]}">SIGUIENTE</text>'
              + f'<text x="{meta}" y="117" text-anchor="middle" class="px" font-size="16" fill="{C["ink"]}">PRÁCTICA</text>'
              + marco(meta - 12, yv - 10, 24, 24, C["amber"], C["amber2"], 3, False) + "</g>")
    return documento(W, H, "Trayectoria como una línea de metro: 2023 Ingeniería de Software; 2025 CineX v1.0 en equipo y C++ Essentials 1; "
                     "2026 cuatro insignias de Google Cloud, Numi, Casa Rendón, CineX v2 y el Observatorio de Salud. Siguiente estación: práctica empresarial.",
                     cuerpo)


# ======================================================================
# 4. Tarjetas de proyecto
# ======================================================================
def tarjeta(estado, color, tipo, titulo, dato, visual, stack, accion, aria):
    W, H = 490, 340
    cuerpo = (marco(0, 0, W - 4, H - 4, C["panel"], C["line2"], 4, True)
              + marco(20, 18, len(estado) * 11 + 46, 30, "#0b1f2a", color, 3, False)
              + led(32, 29, color, 8)
              + f'<text x="48" y="39" class="px" font-size="16" fill="{color}" letter-spacing="1">{e(estado)}</text>'
              + f'<text x="{W - 26}" y="38" text-anchor="end" class="mono" font-size="11" fill="{C["ink3"]}">{e(tipo)}</text>'
              + f'<text x="22" y="90" class="px" font-size="32" fill="{C["ink"]}">{e(titulo.upper())}</text>'
              + f'<text x="22" y="112" class="sg" font-size="14" fill="{C["ink2"]}">{e(dato)}</text>'
              + visual
              + r(20, 290, W - 44, 4, C["line"], ' class="pix"')
              + f'<text x="22" y="316" class="mono" font-size="11" fill="{C["ink3"]}">{e(stack)}</text>'
              + f'<text x="{W - 26}" y="316" text-anchor="end" class="px" font-size="16" fill="{C["amber"]}">{e(accion.upper())} ›</text>')
    return documento(W, H, aria, cuerpo)


def pantalla(x, y, w, h):
    return marco(x, y, w, h, "#07141a", C["line2"], 4, False)


def proyecto_observatorio():
    casos = [98, 2505, 1321, 25804, 1963, 1991, 5761, 6762, 6780, 27628, 4091, 3670, 4980, 2133, 1239, 2007]
    x0, y0, w, h = 34, 264, 420, 88
    bw = w / len(casos)
    barras = ""
    for k, v in enumerate(casos):
        bh = max(4, round(v / 28000 * h / 4) * 4)
        hot = v > 20000
        barras += r(round(x0 + k * bw + 3), y0 - bh, round(bw - 6), bh, C["amber"] if hot else "#2f6f80",
                    f' class="bar pix" style="animation-delay:{.2 + k * .05:.2f}s"')
    vis = (pantalla(22, 126, 444, 154)
           + f'<text x="38" y="150" class="mono" font-size="10.5" fill="{C["ink3"]}">dengue · casos por año · 2007–2022</text>'
           + barras
           + f'<text x="{x0 + 3.5 * bw:.0f}" y="{y0 - 88 - 8}" text-anchor="middle" class="px" font-size="16" fill="{C["amber"]}">2010</text>'
           + f'<text x="{x0 + 9.5 * bw:.0f}" y="{y0 - 88 - 8}" text-anchor="middle" class="px" font-size="16" fill="{C["amber"]}">2016</text>')
    return tarjeta("EN VIVO", C["green"], "proyecto personal", "Observatorio de Salud",
                   "1,18 M casos del SIVIGILA en Antioquia: ETL, SQL y web", vis,
                   "Python · pandas · SQL · MySQL · FastAPI · CI", "ver en vivo",
                   "Observatorio de Salud Pública de Antioquia, en vivo: pipeline en Python y SQL sobre 1,18 millones de casos del SIVIGILA. "
                   "Gráfica de casos de dengue por año con epidemias en 2010 y 2016.")


def proyecto_cinex():
    lineas = [
        (C["green"], "$ ", C["ink"], "GET /showtimes/1/availability"),
        (C["ink3"], "", C["cyan2"], '{ "capacidad": 80, "vendidas": 78,'),
        (C["ink3"], "", C["cyan2"], '  "disponibles": 2 }'),
        (C["green"], "$ ", C["ink"], "POST /bookings  { sillas: 3 }"),
        (C["ink3"], "", C["red"], '409 "Solo quedan 2 sillas disponibles"'),
    ]
    vis = pantalla(22, 126, 444, 154)
    for k, (c1, p, c2, t) in enumerate(lineas):
        vis += (f'<text class="mono rise" style="animation-delay:{.3 + k * .4:.2f}s" x="40" y="{156 + k * 25}" font-size="12.5" fill="{c2}">'
                f'<tspan fill="{c1}">{e(p)}</tspan>{e(t)}</text>')
    return tarjeta("EN VIVO", C["green"], "equipo · v2.0 individual", "CineX",
                   "API REST en Spring Boot con reglas de negocio y 17 pruebas", vis,
                   "Java 21 · Spring Boot · MySQL · JUnit · Docker", "probar la API",
                   "CineX, en vivo: API REST en Java con Spring Boot y MySQL. Ejemplo: al pedir 3 sillas cuando quedan 2, responde 409. "
                   "17 pruebas automáticas. Versión 1.0 en equipo, versión 2.0 individual.")


AVION = """
...AA...
...AA...
..AAAA..
AAAAAAAA
...AA...
..AAAA..
"""


def proyecto_numi():
    vis = (pantalla(22, 126, 444, 154)
           + sprite(AVION, {"A": C["amber"]}, 38, 140, 2)
           + f'<text x="60" y="151" class="mono" font-size="10.5" fill="{C["amber"]}">modo avión · sin internet</text>'
           + '<g class="rise" style="animation-delay:.4s">' + marco(262, 164, 188, 34, "#2f6f80", "#4b93a6", 3, False)
           + f'<text x="278" y="186" class="sg" font-size="14" fill="{C["ink"]}">¿Cuánto es 7 × 8?</text></g>'
           + '<g class="rise" style="animation-delay:1.1s">' + marco(38, 210, 250, 52, "#163240", C["line2"], 3, False)
           + f'<text x="54" y="232" class="sgb" font-size="14" fill="{C["ink"]}">7 × 8 = 56</text>'
           + f'<text x="54" y="250" class="mono" font-size="10.5" fill="{C["ink3"]}">Gemma 2B + RAG en el celular</text></g>')
    return tarjeta("EN DESARROLLO", C["cyan"], "equipo", "Numi",
                   "App educativa con IA que funciona sin internet", vis,
                   "Flutter · Dart · SQLite · Gemma 2B · FastAPI", "ver detalles",
                   "Numi, en desarrollo, proyecto en equipo: app educativa en Flutter con un asistente de IA que corre en el celular sin internet. "
                   "Mi rol: arquitectura, pantallas de Ciencias Naturales, RAG offline y diseño responsive.")


TAZA = """
.V..V....
..V..V...
.........
KKKKKKK..
KkkkkkKKK
KkkkkkK.K
KkkkkkKKK
.KkkkK...
..KKK....
"""


def proyecto_casa():
    vis = (marco(22, 126, 444, 154, "#2a2116", "#5a4630", 4, False)
           + r(26, 130, 436, 18, "#3a2e1f", ' class="pix"')
           + "".join(r(36 + k * 12, 136, 6, 6, c, ' class="pix"') for k, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]))
           + f'<text x="244" y="143" text-anchor="middle" class="mono" font-size="10" fill="#bfa98a">casarendon.com</text>'
           + f'<text x="40" y="198" class="sgb" font-size="34" fill="#f3e6cf">Entre</text>'
           + f'<text x="40" y="238" class="sgb" font-size="34" fill="#e0a64b">Sorbos</text>'
           + sprite(TAZA, {"V": "#d8c9ad", "K": "#e8d9bf", "k": "#6b3e22"}, 186, 196, 4)
           + f'<text x="246" y="192" class="sg" font-size="12.5" fill="#d8c9ad">Café de altura y vino</text>'
           + f'<text x="246" y="210" class="sg" font-size="12.5" fill="#d8c9ad">Andes, Antioquia</text>'
           + marco(246, 224, 146, 28, "#b5651d", "#d78a3c", 3, False)
           + f'<text x="319" y="243" text-anchor="middle" class="monob" font-size="11" fill="#fff3e0">RESERVAR VISITA</text>')
    return tarjeta("CLIENTE REAL", C["amber"], "equipo · en producción", "Casa Rendón",
                   "Sitio en React para una marca de café y vino", vis,
                   "React · JavaScript · HTML · CSS", "visitar el sitio",
                   "Casa Rendón, cliente real en producción: sitio web en React de una marca de café y vino artesanal en Andes, Antioquia. "
                   "Mi rol: diseño y desarrollo del sitio.")


# ======================================================================
# 5. Inventario (stack) e insignias
# ======================================================================
HERRAMIENTAS = [
    ("BACKEND", [
        ("java", "Java", "API REST con reglas de negocio", "CineX"),
        ("springboot", "Spring Boot", "capas, JPA, validaciones y Swagger", "CineX"),
        ("python", "Python", "ETL que limpia 1,18 M de casos", "Observatorio"),
        ("fastapi", "FastAPI", "API de solo lectura de los datos", "Observatorio"),
    ]),
    ("DATOS", [
        ("sql", "SQL", "CTE, ventanas y canal endémico", "Observatorio"),
        ("mysql", "MySQL", "modelo estrella y esquema de la API", "Observatorio · CineX"),
        ("pandas", "pandas", "limpieza y validación de datos", "Observatorio"),
        ("powerbi", "Power BI · Looker", "tableros de datos en clase", "Académico"),
    ]),
    ("WEB Y MÓVIL", [
        ("react", "React", "componentes del sitio de un cliente", "Casa Rendón"),
        ("javascript", "JavaScript", "panel web que consume la API", "CineX"),
        ("flutter", "Flutter", "app con IA que funciona sin internet", "Numi"),
    ]),
    ("CALIDAD Y DEVOPS", [
        ("junit5", "JUnit · Mockito", "17 pruebas de la API", "CineX"),
        ("pytest", "pytest", "pruebas del pipeline y la API", "Observatorio"),
        ("githubactions", "GitHub Actions", "CI y datos actualizados cada mes", "CineX · Observatorio"),
        ("docker", "Docker", "todo el entorno con un comando", "CineX · Observatorio"),
        ("postman", "Postman", "26 solicitudes automatizadas", "CineX"),
    ]),
]


def stack():
    W = 1000
    izq = (f'<text x="32" y="86" class="mono" font-size="10.5" fill="{C["ink3"]}" letter-spacing="1">HERRAMIENTA</text>'
           f'<text x="186" y="86" class="mono" font-size="10.5" fill="{C["ink3"]}" letter-spacing="1">PARA QUÉ LA USÉ</text>'
           f'<text x="590" y="86" text-anchor="end" class="mono" font-size="10.5" fill="{C["ink3"]}" letter-spacing="1">DÓNDE</text>'
           + r(32, 94, 558, 2, C["line2"], ' class="pix"'))
    y = 104
    fila = 0
    for g, items in HERRAMIENTAS:
        y += 8
        izq += f'<text x="32" y="{y + 16}" class="px" font-size="16" fill="{C["cyan"]}" letter-spacing="1">{e(g)}</text>'
        y += 26
        for slug, nombre, uso, donde in items:
            if fila % 2 == 0:
                izq += r(28, y, 566, 30, "#0d222b", ' class="pix"')
            ic = icono_custom(slug, 34, y + 4, 22) if slug in ("powerbi", "sql", "java") else icono(slug, 34, y + 4, 22)
            izq += (ic
                    + f'<text x="66" y="{y + 20}" class="sgb" font-size="13.5" fill="{C["ink"]}">{e(nombre)}</text>'
                    + f'<text x="186" y="{y + 20}" class="sg" font-size="13" fill="{C["ink2"]}">{e(uso)}</text>'
                    + f'<text x="590" y="{y + 20}" text-anchor="end" class="mono" font-size="11" fill="{C["amber"]}">{e(donde)}</text>')
            y += 30
            fila += 1
    H = y + 34
    izq += f'<text x="32" y="{y + 22}" class="mono" font-size="10.5" fill="{C["ink3"]}">También: HTML, CSS, Dart, SQLite, Firebase, Jupyter, Git, Maven, Gradle, Scrum</text>'
    H += 14
    certs = [
        ("googlecloud", "Cloud Load Balancing", "Google Cloud · mar. 2026"),
        ("googlecloud", "App Dev Environment", "Google Cloud · abr. 2026"),
        ("googlecloud", "Computing Foundations ×2", "Google Cloud · 2026"),
        ("cplusplus", "C++ Essentials 1", "Cisco · oct. 2025"),
        ("java", "Diplomados Java y JavaScript", "Politécnico de Colombia"),
    ]
    der = ""
    for k, (slug, n, d) in enumerate(certs):
        yy = 78 + k * 60
        ic = icono_custom("java", 650, yy + 7, 36) if slug == "java" else icono(slug, 650, yy + 7, 36)
        der += (f'<g class="rise" style="animation-delay:{.3 + k * .15:.2f}s">'
                + marco(640, yy, 326, 50, "#0b1f2a", C["line"], 3, False) + ic
                + f'<text x="698" y="{yy + 22}" class="sgb" font-size="13.5" fill="{C["ink"]}">{e(n)}</text>'
                + f'<text x="698" y="{yy + 39}" class="mono" font-size="10.5" fill="{C["ink3"]}">{e(d)}</text>'
                + r(938, yy + 22, 4, 4, C["green"], ' class="pix"') + r(942, yy + 26, 4, 4, C["green"], ' class="pix"')
                + r(946, yy + 22, 4, 4, C["green"], ' class="pix"') + r(950, yy + 18, 4, 4, C["green"], ' class="pix"')
                + r(954, yy + 14, 4, 4, C["green"], ' class="pix"') + "</g>")
    stats = [("PRUEBAS", "17"), ("SOLICITUDES", "26"), ("CASOS", "1,18 M")]
    nums = ""
    for k, (a, b) in enumerate(stats):
        x = 640 + k * 112
        nums += (f'<text x="{x}" y="418" class="mono" font-size="11" fill="{C["ink3"]}" letter-spacing="1">{e(a)}</text>'
                 f'<text x="{x}" y="450" class="px" font-size="32" fill="{C["amber"]}">{e(b)}</text>')
    der += (marco(640, 492, 326, 126, "#0b1f2a", C["amber"], 3, False)
            + f'<text x="658" y="520" class="px" font-size="16" fill="{C["amber"]}" letter-spacing="1">APRENDIENDO AHORA</text>'
            + led(658, 540, C["amber"], 8)
            + f'<text x="676" y="548" class="sg" font-size="13.5" fill="{C["ink"]}">Tablero en Power BI con los datos</text>'
            + f'<text x="676" y="566" class="sg" font-size="13.5" fill="{C["ink"]}">del Observatorio</text>'
            + led(658, 584, C["amber"], 8, .5)
            + f'<text x="676" y="592" class="sg" font-size="13.5" fill="{C["ink"]}">Análisis de datos con Python</text>')
    cuerpo = (panel(W, H)
              + titulo_panel(32, 50, "INVENTARIO", "qué uso, para qué y dónde", "", 560)
              + r(612, 30, 4, H - 64, C["line"], ' class="pix"')
              + f'<text x="640" y="50" class="px" font-size="24" fill="{C["amber"]}" letter-spacing="1">INSIGNIAS</text>'
              + f'<text x="966" y="49" text-anchor="end" class="sg" font-size="14" fill="{C["ink2"]}">verificables</text>'
              + izq + der
              + r(640, 390, 326, 4, C["line"], ' class="pix"')
              + nums)
    return documento(W, H, "Inventario: " + "; ".join(f"{n}: {u} ({d})" for _, it in HERRAMIENTAS for _, n, u, d in it) + ". Insignias: Google Cloud Implementing Cloud Load Balancing for Compute Engine, "
                     "Set Up an App Dev Environment, dos Google Cloud Computing Foundations, C++ Essentials 1 de Cisco y diplomados en Java y JavaScript del Politécnico de Colombia. "
                     "17 pruebas, 26 solicitudes de Postman y 1,18 millones de casos analizados.",
                     cuerpo)


# ======================================================================
# 6. Contribuciones y cierre
# ======================================================================
def contribuciones():
    W, H = 1000, 84
    cuerpo = (panel(W, H)
              + f'<text x="32" y="44" class="px" font-size="24" fill="{C["amber"]}" letter-spacing="1">CONTRIBUCIONES</text>'
              + f'<text x="32" y="66" class="sg" font-size="14" fill="{C["ink2"]}">Mi actividad real del último año en GitHub, actualizada cada 12 horas.</text>')
    return documento(W, H, "Contribuciones: mi actividad real del último año en GitHub.", cuerpo)


def cierre():
    W, H = 1000, 290
    suelo = 244
    letrero = (marco(632, 36, 252, 70, "#0d3b2c", C["green"], 4, True)
               + f'<text x="758" y="62" text-anchor="middle" class="px" font-size="16" fill="#bff5da" letter-spacing="1">PRÓXIMA ESTACIÓN</text>'
               + f'<text x="758" y="92" text-anchor="middle" class="px" font-size="24" fill="#ffffff">TU EQUIPO</text>'
               + r(690, 110, 4, suelo - 110, "#2a4752", ' class="pix"') + r(822, 110, 4, suelo - 110, "#2a4752", ' class="pix"'))
    cuerpo = (f'<clipPath id="cc"><rect x="4" y="4" width="{W - 12}" height="{H - 12}"/></clipPath>'
              + panel(W, H)
              + '<g clip-path="url(#cc)">' + cielo(W, suelo, 0, .6)
              + estrellas(W, 150, 26, (30, 30, 610, 230))
              + edificios(520, 1000, suelo, 33, .75)
              + r(0, suelo, W, H - suelo, C["ground"], ' class="pix"') + r(0, suelo, W, 6, C["grass"], ' class="pix"') + "</g>"
              + f'<text x="48" y="90" class="px" font-size="40" fill="{C["ink"]}">¿TU EQUIPO NECESITA</text>'
              + f'<text x="48" y="138" class="px" font-size="40" fill="{C["cyan"]}">UN PRACTICANTE?</text>'
              + f'<text x="50" y="176" class="sg" font-size="15.5" fill="{C["ink2"]}">Desarrollo de software o análisis de datos · disponible desde ya</text>'
              + f'<text x="50" y="210" class="px" font-size="24" fill="{C["amber"]}">alexmejia0112@gmail.com</text>'
              + letrero
              + sprite(ALEX_SALUDO, PALETA_ALEX, 880, suelo - 21 * 5, 5))
    return documento(W, H, "¿Tu equipo necesita un practicante? Desarrollo de software o análisis de datos, disponible desde ya. alexmejia0112@gmail.com", cuerpo)


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for viejo in SALIDA.glob("*.svg"):
        viejo.unlink()
    archivos = {
        "portada.svg": portada(),
        "btn-portafolio.svg": boton("Ver portafolio", True),
        "btn-cv.svg": boton("Hoja de vida", False),
        "btn-cv-datos.svg": boton("Hoja de vida · Datos", False),
        "btn-linkedin.svg": boton("LinkedIn", False),
        "btn-correo.svg": boton("Correo", False),
        "trayectoria.svg": trayectoria(),
        "proyecto-observatorio.svg": proyecto_observatorio(),
        "proyecto-cinex.svg": proyecto_cinex(),
        "proyecto-numi.svg": proyecto_numi(),
        "proyecto-casa-rendon.svg": proyecto_casa(),
        "stack.svg": stack(),
        "cierre.svg": cierre(),
    }
    import movil
    (SALIDA / "movil").mkdir(exist_ok=True)
    for viejo in (SALIDA / "movil").glob("*.svg"):
        viejo.unlink()
    archivos.update(movil.generar())
    for nombre, svg in archivos.items():
        (SALIDA / nombre).write_text(svg, encoding="utf-8")
        print(f"{nombre:28s} {len(svg) / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
