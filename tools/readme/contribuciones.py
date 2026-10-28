"""Dibuja mis contribuciones de GitHub como un edificio de Medellín de noche.

Cada columna es una semana y cada ventana un día: se enciende más mientras
más programé ese día. Encima van las cifras reales del último año.

Uso:
    python tools/readme/contribuciones.py <carpeta_salida>

Variables de entorno:
    GH_USER         usuario de GitHub (por defecto AlexanderM-Code)
    CONTRIB_DEMO=1  usa datos de ejemplo (para probar sin internet)

Lo ejecuta cada día el workflow .github/workflows/contribuciones.yml y publica
el resultado en la rama output.
"""
import datetime as dt
import os
import pathlib
import random
import re
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build import C, cielo, documento, e, estrellas, led, marco, panel, r  # noqa: E402

USUARIO = os.environ.get("GH_USER", "AlexanderM-Code")
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
VENTANA = {0: "#123039", 1: "#7a4f1c", 2: "#c2822a", 3: "#ffb74d", 4: "#ffe2a8"}


# ---------------------------------------------------------------- datos
def descargar() -> dict:
    """Devuelve {fecha: (contribuciones, nivel 0-4)} del último año."""
    if os.environ.get("CONTRIB_DEMO"):
        rnd = random.Random(4)
        hoy = dt.date.today()
        dias = {}
        for i in range(364, -1, -1):
            d = hoy - dt.timedelta(days=i)
            n = 0 if rnd.random() < .55 else rnd.choice([1, 1, 2, 3, 5, 8, 12])
            dias[d.isoformat()] = (n, 0 if n == 0 else 1 if n < 3 else 2 if n < 6 else 3 if n < 10 else 4)
        return dias
    req = urllib.request.Request(f"https://github.com/users/{USUARIO}/contributions",
                                 headers={"User-Agent": "contribuciones-readme"})
    pagina = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    textos = {m.group(1): m.group(2) for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', pagina)}
    dias = {}
    for m in re.finditer(r'<td[^>]*?data-date="(\d{4}-\d\d-\d\d)"[^>]*>', pagina):
        celda = m.group(0)
        ident = re.search(r'id="([^"]+)"', celda)
        nivel = re.search(r'data-level="(\d)"', celda)
        nivel = int(nivel.group(1)) if nivel else 0
        texto = textos.get(ident.group(1) if ident else "", "")
        n = re.match(r"\s*(\d+)", texto)
        dias[m.group(1)] = (int(n.group(1)) if n else (1 if nivel else 0), nivel)
    if not dias:
        raise SystemExit("No se encontraron contribuciones en la página de GitHub")
    return dias


def cifras(dias: dict) -> dict:
    fechas = sorted(dias)
    total = sum(n for n, _ in dias.values())
    activos = sum(1 for n, _ in dias.values() if n > 0)
    mejor = max(n for n, _ in dias.values())
    racha = larga = 0
    for f in fechas:
        racha = racha + 1 if dias[f][0] > 0 else 0
        larga = max(larga, racha)
    return {"total": total, "activos": activos, "larga": larga, "mejor": mejor}


def semanas(dias: dict, n_semanas: int) -> list:
    """Lista de semanas (domingo a sábado); cada día es (fecha, n, nivel) o None."""
    fechas = sorted(dias)
    fin = dt.date.fromisoformat(fechas[-1])
    inicio = fin - dt.timedelta(days=fin.isoweekday() % 7) - dt.timedelta(weeks=n_semanas - 1)
    out = []
    for s in range(n_semanas):
        col = []
        for d in range(7):
            f = inicio + dt.timedelta(weeks=s, days=d)
            k = f.isoformat()
            col.append((f, *dias[k]) if k in dias and f <= fin else None)
        out.append(col)
    return out


# ---------------------------------------------------------------- dibujo
def ciudad(cols: list, x0: float, base: float, ancho: float, v: float, paso: float, semilla: int) -> str:
    """Edificios con una ventana por día. v: lado de la ventana, paso: separación vertical."""
    rnd = random.Random(semilla)
    out = '<g class="pix">'
    luces = ""
    hoy = None
    alto_ventanas = 7 * paso
    for s, col in enumerate(cols):
        x = x0 + s * ancho
        techo = base - alto_ventanas - 10 - rnd.choice([0, 0, 6, 12, 18, 24])
        out += r(round(x), round(techo), round(ancho - 2), round(base - techo), rnd.choice(["#0b1e27", "#0d2430", "#0a1a22"]))
        if rnd.random() < .18:
            out += r(round(x + ancho / 2 - 1), round(techo - 10), 2, 10, "#2a4752")
            out += r(round(x + ancho / 2 - 2), round(techo - 12), 4, 3, C["red"], ' class="led"')
        for d, dia in enumerate(col):
            wx = round(x + (ancho - 2 - v) / 2)
            wy = round(base - alto_ventanas - 4 + d * paso)
            if dia is None:
                continue
            nivel = dia[2]
            color = VENTANA[nivel]
            if nivel == 0:
                out += r(wx, wy, round(v), round(v), color)
            else:
                luces += (f'<rect x="{wx}" y="{wy}" width="{round(v)}" height="{round(v)}" fill="{color}" '
                          f'class="pix"><title>{dia[0].isoformat()}: {dia[1]}</title></rect>')
            hoy = (wx, wy)
    out += "</g>" + luces
    if hoy:
        out += led(hoy[0] - 2, hoy[1] - 2, C["cyan"], round(v) + 4)
    return out


def meses(cols: list, x0: float, ancho: float, y: float, tam: float) -> str:
    out, ultimo = "", None
    for s, col in enumerate(cols):
        dia = next((d for d in col if d), None)
        if dia and dia[0].month != ultimo and dia[0].day <= 7:
            out += f'<text x="{x0 + s * ancho:.0f}" y="{y}" class="mono" font-size="{tam}" fill="{C["ink3"]}">{MESES[dia[0].month - 1]}</text>'
            ultimo = dia[0].month
    return out


def chip(x, y, valor, etiqueta, escala=1.0):
    w = 150 * escala
    return (marco(x, y, w, 62 * escala, "#0b1f2a", C["line2"], 3 * escala, False)
            + f'<text x="{x + 14 * escala:.0f}" y="{y + 32 * escala:.0f}" class="px" font-size="{24 * escala:.0f}" fill="{C["amber"]}">{e(str(valor))}</text>'
            + f'<text x="{x + 14 * escala:.0f}" y="{y + 50 * escala:.0f}" class="mono" font-size="{10.5 * escala:.1f}" fill="{C["ink2"]}">{e(etiqueta)}</text>')


def leyenda(x, y, v, tam):
    out = f'<text x="{x}" y="{y + v - 1}" class="mono" font-size="{tam}" fill="{C["ink3"]}">menos</text>'
    x += tam * 3.6
    for k in range(5):
        out += r(round(x + k * (v + 4)), y, v, v, VENTANA[k], ' class="pix"')
    out += f'<text x="{x + 5 * (v + 4) + 4:.0f}" y="{y + v - 1}" class="mono" font-size="{tam}" fill="{C["ink3"]}">más</text>'
    return out


def escritorio(dias: dict, k: dict) -> str:
    W, H = 1000, 380
    cols = semanas(dias, 53)
    suelo = 318
    x0, ancho = 26, 17.9
    actualizado = dt.date.fromisoformat(sorted(dias)[-1])
    cuerpo = (panel(W, H)
              + f'<g clip-path="url(#cc)"><clipPath id="cc"><rect x="4" y="4" width="{W - 12}" height="{H - 12}"/></clipPath>'
              + cielo(W, suelo, 0, .55) + estrellas(W, 120, 30, (20, 20, 980, 120))
              + r(0, suelo, W, H - suelo, C["ground"], ' class="pix"') + r(0, suelo, W, 6, C["grass"], ' class="pix"') + "</g>"
              + f'<text x="32" y="48" class="px" font-size="24" fill="{C["amber"]}" letter-spacing="1">CONTRIBUCIONES</text>'
              + f'<text x="32" y="72" class="sg" font-size="14" fill="{C["ink2"]}">Cada ventana encendida es un día que programé.</text>'
              + f'<text x="32" y="92" class="mono" font-size="11" fill="{C["ink3"]}">Último año · actualizado el {actualizado.day} de {MESES[actualizado.month - 1]}. de {actualizado.year}</text>'
              + chip(384, 30, k["total"], "contribuciones", .94)
              + chip(533, 30, k["activos"], "días activos", .94)
              + chip(682, 30, k["larga"], "días de racha", .94)
              + chip(831, 30, k["mejor"], "en mi mejor día", .94)
              + ciudad(cols, x0, suelo, ancho, 9, 13, 3)
              + meses(cols, x0, ancho, 344, 11)
              + leyenda(800, 352, 9, 10.5))
    return documento(W, H, f"Contribuciones del último año en GitHub, dibujadas como un edificio de Medellín de noche: "
                     f"{k['total']} contribuciones, {k['activos']} días activos, racha más larga de {k['larga']} días "
                     f"y {k['mejor']} contribuciones en el mejor día.", cuerpo)


def movil(dias: dict, k: dict) -> str:
    W, H = 1000, 960
    cols = semanas(dias, 26)
    suelo = 820
    x0, ancho = 40, 35.5
    actualizado = dt.date.fromisoformat(sorted(dias)[-1])
    cuerpo = (panel(W, H)
              + f'<g clip-path="url(#cm)"><clipPath id="cm"><rect x="6" y="6" width="{W - 18}" height="{H - 18}"/></clipPath>'
              + cielo(W, suelo, 0, .55) + estrellas(W, 420, 26, (30, 30, 970, 440))
              + r(0, suelo, W, H - suelo, C["ground"], ' class="pix"') + r(0, suelo, W, 8, C["grass"], ' class="pix"') + "</g>"
              + f'<text x="48" y="96" class="px" font-size="56" fill="{C["amber"]}">CONTRIBUCIONES</text>'
              + f'<text x="48" y="150" class="sg" font-size="32" fill="{C["ink2"]}">Cada ventana encendida es un día</text>'
              + f'<text x="48" y="192" class="sg" font-size="32" fill="{C["ink2"]}">que programé · últimos 6 meses</text>'
              + chip(48, 230, k["total"], "contribuciones", 2.8)
              + chip(530, 230, k["activos"], "días activos", 2.8)
              + ciudad(cols, x0, suelo, ancho, 20, 30, 5)
              + meses(cols, x0, ancho, 880, 26)
              + f'<text x="48" y="926" class="mono" font-size="24" fill="{C["ink3"]}">Racha más larga: {k["larga"]} días · actualizado el {actualizado.day} de {MESES[actualizado.month - 1]}.</text>')
    return documento(W, H, f"Contribuciones de GitHub de los últimos seis meses como un edificio de Medellín de noche: "
                     f"{k['total']} contribuciones en el año y {k['activos']} días activos.", cuerpo)


def main() -> None:
    salida = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    salida.mkdir(parents=True, exist_ok=True)
    dias = descargar()
    k = cifras(dias)
    (salida / "contribuciones.svg").write_text(escritorio(dias, k), encoding="utf-8")
    (salida / "contribuciones-movil.svg").write_text(movil(dias, k), encoding="utf-8")
    print(f"listo: {k}")


if __name__ == "__main__":
    main()
