"""Genera los encabezados SVG del README (tema claro y oscuro) con la paleta del portafolio.

Uso: python tools/make_header.py  (requiere fonttools y brotli)
Las fuentes se recortan a los caracteres usados y se incrustan en el SVG,
así GitHub las muestra igual que en https://alexanderm-code.github.io/.
"""
import base64
import io
import pathlib

from fontTools import subset
from fontTools.ttLib import TTFont

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "tools" / "fonts"
SALIDA = RAIZ / "assets"

ETIQUETA = "INGENIERÍA DE SOFTWARE · MEDELLÍN"
DISPONIBLE = "Disponible desde ya para práctica empresarial"
NOMBRE = "Alexander Mejía Ospina"
LEMA_1 = "Construyo APIs, sitios web y análisis de datos"
LEMA_2 = "que funcionan en producción, con pruebas y despliegue."
CIFRAS = [
    ("3", "proyectos en línea"),
    ("1,18 M", "casos de salud pública analizados"),
    ("17", "pruebas automáticas en CineX"),
    ("7.º", "semestre de Ingeniería de Software"),
]

TEMAS = {
    "claro": {
        "paper": "#f3efe6", "surface": "#fbf9f4", "ink": "#17181c", "ink2": "#45464c",
        "ink3": "#5f5f66", "line": "rgba(23,24,28,0.14)", "rule": "#17181c",
        "grid": "rgba(33,65,181,0.06)", "green": "#1c8a4b", "blue": "#2141b5",
    },
    "oscuro": {
        "paper": "#121418", "surface": "#1c1f25", "ink": "#ece8df", "ink2": "#bdbab2",
        "ink3": "#9a978f", "line": "rgba(236,232,223,0.13)", "rule": "#ece8df",
        "grid": "rgba(142,168,255,0.07)", "green": "#3fbf74", "blue": "#8ea8ff",
    },
}


def fuente_b64(archivo: str, texto: str) -> str:
    opciones = subset.Options()
    opciones.flavor = "woff2"
    opciones.layout_features = ["*"]
    fuente = TTFont(FUENTES / archivo)
    sub = subset.Subsetter(opciones)
    sub.populate(text=texto)
    sub.subset(fuente)
    buf = io.BytesIO()
    fuente.flavor = "woff2"
    fuente.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(tema: dict, grotesk: str, mono: str) -> str:
    w, h = 1280, 470
    x0 = 64
    col = (w - 2 * x0) / 4
    cifras = []
    for i, (num, txt) in enumerate(CIFRAS):
        x = x0 + i * col
        sep = f'<line x1="{x - 18:.0f}" y1="372" x2="{x - 18:.0f}" y2="436" stroke="{tema["line"]}"/>' if i else ""
        cifras.append(
            f'{sep}<text x="{x:.0f}" y="404" class="num">{esc(num)}</text>'
            f'<text x="{x:.0f}" y="430" class="cap">{esc(txt)}</text>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(NOMBRE)}. {esc(LEMA_1)} {esc(LEMA_2)}">
<defs>
<style>
@font-face{{font-family:"SG";src:url(data:font/woff2;base64,{grotesk}) format("woff2");font-weight:400 900}}
@font-face{{font-family:"JBM";src:url(data:font/woff2;base64,{mono}) format("woff2");font-weight:100 800}}
.mono{{font-family:"JBM",ui-monospace,Consolas,monospace;font-size:15px;letter-spacing:.12em;fill:{tema["ink3"]}}}
.pill{{font-family:"SG",system-ui,sans-serif;font-size:16px;fill:{tema["ink"]}}}
.name{{font-family:"SG",system-ui,sans-serif;font-weight:800;font-size:92px;letter-spacing:-.035em;fill:{tema["ink"]}}}
.lema{{font-family:"SG",system-ui,sans-serif;font-size:25px;fill:{tema["ink2"]}}}
.num{{font-family:"JBM",ui-monospace,Consolas,monospace;font-size:34px;font-weight:500;fill:{tema["ink"]}}}
.cap{{font-family:"SG",system-ui,sans-serif;font-size:15px;fill:{tema["ink3"]}}}
</style>
<pattern id="g" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{tema["grid"]}" stroke-width="1"/></pattern>
</defs>
<rect width="{w}" height="{h}" rx="14" fill="{tema["paper"]}"/>
<rect width="{w}" height="{h}" rx="14" fill="url(#g)"/>
<text x="{x0}" y="62" class="mono">{esc(ETIQUETA)}</text>
<rect x="{x0}" y="80" width="408" height="34" rx="17" fill="{tema["surface"]}" stroke="{tema["line"]}"/>
<circle cx="{x0 + 20}" cy="97" r="5" fill="{tema["green"]}"><animate attributeName="opacity" values="1;.35;1" dur="2.4s" repeatCount="indefinite"/></circle>
<text x="{x0 + 34}" y="102.5" class="pill">{esc(DISPONIBLE)}</text>
<text x="{x0 - 4}" y="222" class="name">{esc(NOMBRE)}</text>
<text x="{x0}" y="276" class="lema">{esc(LEMA_1)}</text>
<text x="{x0}" y="310" class="lema">{esc(LEMA_2)}</text>
<line x1="{x0}" y1="352" x2="{w - x0}" y2="352" stroke="{tema["rule"]}" stroke-width="1.5"/>
{"".join(cifras)}
</svg>
'''


def main() -> None:
    texto = ETIQUETA + DISPONIBLE + NOMBRE + LEMA_1 + LEMA_2 + "".join(a + b for a, b in CIFRAS)
    grotesk = fuente_b64("schibsted-grotesk-latin.woff2", texto)
    mono = fuente_b64("jetbrains-mono-latin.woff2", texto)
    SALIDA.mkdir(exist_ok=True)
    for nombre, tema in TEMAS.items():
        (SALIDA / f"encabezado-{nombre}.svg").write_text(svg(tema, grotesk, mono), encoding="utf-8")
        print("listo:", SALIDA / f"encabezado-{nombre}.svg")


if __name__ == "__main__":
    main()
