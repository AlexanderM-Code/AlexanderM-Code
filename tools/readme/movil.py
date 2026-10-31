"""Versiones para celular de los paneles del README.

GitHub muestra cada panel al ancho de la pantalla; en un celular eso deja el
texto diminuto. Estas versiones tienen la misma escena y los mismos datos, pero
en formato vertical y con letra grande. El README las elige con
<picture><source media="(max-width: 700px)">.
"""
import random

from build import (ALEX, ALEX_SALUDO, C, PALETA_ALEX, cielo, comuna, documento, e, edificios, estrellas, icono,
                   icono_custom, led, marco, SERVICIOS, metrocable, montanas, panel, r, sprite)


def portada_movil():
    W, H = 1000, 1060
    suelo = 780
    random.seed(17)
    celdas = [("UBICACIÓN", "Medellín"), ("FORMACIÓN", "Ing. de Software · VII"),
              ("PRÁCTICA", "Disponible desde ya"), ("MODALIDAD", "Presencial o remota")]
    datos = ""
    for k, (a, b) in enumerate(celdas):
        x = 64 + (k % 2) * 470
        y = suelo + 84 + (k // 2) * 110
        datos += (f'<text x="{x}" y="{y}" class="px" font-size="32" fill="{C["amber"]}">{e(a)}</text>'
                  f'<text x="{x}" y="{y + 46}" class="sg" font-size="34" fill="{C["ink"]}">{e(b)}</text>')
    cuerpo = (cielo(W, suelo)
              + estrellas(W, 560, 40, (40, 40, 960, 520))
              + montanas(W, suelo - 120, 220, C["mont1"], 28, 3)
              + montanas(W, suelo - 60, 150, C["mont2"], 24, 11)
              + comuna(0, 420, suelo - 90, 5)
              + comuna(600, 1000, suelo - 80, 9)
              + metrocable(90, 600, 640, 660, 3, 16)
              + edificios(360, 700, suelo, 21)
              + r(0, suelo, W, H - suelo, C["ground"], ' class="pix"') + r(0, suelo, W, 8, C["grass"], ' class="pix"')
              + f'<text x="68" y="166" class="px" font-size="104" fill="#08090c" opacity=".7">ALEXANDER</text>'
              + f'<text x="60" y="158" class="px" font-size="104" fill="{C["ink"]}">ALEXANDER</text>'
              + f'<text x="68" y="290" class="px" font-size="104" fill="#08090c" opacity=".7">MEJÍA OSPINA</text>'
              + f'<text x="60" y="282" class="px" font-size="104" fill="{C["cyan"]}">MEJÍA OSPINA</text>'
              + f'<text x="64" y="356" class="sg" font-size="36" fill="{C["ink"]}">Estudiante de Ingeniería de Software</text>'
              + f'<text x="64" y="404" class="sg" font-size="36" fill="{C["ink"]}">Universidad Cooperativa de Colombia</text>'
              + marco(60, 440, 880, 84, "#101217", C["green"], 6, True)
              + led(96, 472, C["green"], 20)
              + f'<text x="134" y="494" class="sgb" font-size="36" fill="{C["ink"]}">Disponible desde ya para práctica</text>'
              + f'<g class="bob">{sprite(ALEX, PALETA_ALEX, 790, suelo - 21 * 9, 9)}</g>'
              + datos)
    return documento(W, H, "Alexander Mejía Ospina, estudiante de Ingeniería de Software en la Universidad Cooperativa de Colombia, Medellín. "
                     "Disponible desde ya para práctica empresarial.", cuerpo)


def tarjeta_movil(estado, color, titulo, linea1, linea2, accion, aria):
    W, H = 490, 340
    cuerpo = (marco(0, 0, W - 6, H - 6, C["panel"], C["line2"], 6, True)
              + marco(24, 24, len(estado) * 17 + 70, 46, "#101217", color, 4, False)
              + led(42, 39, color, 16)
              + f'<text x="70" y="56" class="px" font-size="24" fill="{color}">{e(estado)}</text>'
              + f'<text x="26" y="142" class="px" font-size="48" fill="{C["ink"]}">{e(titulo)}</text>'
              + f'<text x="28" y="196" class="sg" font-size="30" fill="{C["ink2"]}">{e(linea1)}</text>'
              + f'<text x="28" y="236" class="sg" font-size="30" fill="{C["ink2"]}">{e(linea2)}</text>'
              + r(24, 260, W - 54, 6, C["line"], ' class="pix"')
              + f'<text x="28" y="310" class="px" font-size="32" fill="{C["amber"]}">{e(accion)} ›</text>')
    return documento(W, H, aria, cuerpo)


def trayectoria_movil():
    from build import HITOS, TRAYECTORIA_ALT
    hitos = HITOS
    W = 1000
    y0, paso = 190, 186
    H = y0 + paso * len(hitos) + 210
    xv = 110
    via = '<g class="pix">' + r(xv - 10, y0 - 30, 20, H - y0 - 20, "#3a3e48") + r(xv - 4, y0 - 30, 6, H - y0 - 20, "#9a978f") + "</g>"
    est = ""
    for k, (anio, t, s) in enumerate(hitos):
        y = y0 + k * paso
        est += (f'<g class="rise" style="animation-delay:{.2 + k * .2:.1f}s">'
                + marco(xv - 22, y - 22, 44, 44, C["ink"], C["cyan"], 5, False) + r(xv - 8, y - 8, 16, 16, C["cyan"], ' class="pix"')
                + f'<text x="180" y="{y - 20}" class="px" font-size="40" fill="{C["amber"]}">{anio}</text>'
                + f'<text x="180" y="{y + 30}" class="sgb" font-size="40" fill="{C["ink"]}">{e(t)}</text>'
                + f'<text x="180" y="{y + 74}" class="mono" font-size="28" fill="{C["ink3"]}">{e(s)}</text></g>')
    ym = y0 + paso * len(hitos)
    meta = (marco(xv - 26, ym - 26, 52, 52, C["amber"], C["amber2"], 5, False)
            + marco(170, ym - 76, 560, 140, "#2e1a0c", C["amber"], 6, True)
            + f'<text x="206" y="{ym - 30}" class="px" font-size="32" fill="{C["amber"]}">SIGUIENTE</text>'
            + f'<text x="206" y="{ym + 42}" class="px" font-size="48" fill="{C["ink"]}">PRÁCTICA</text>')
    tren = ('<g class="pix">' + r(-26, 0, 52, 90, "#ece8df") + r(-26, 70, 52, 8, C["green"])
            + "".join(r(-16, 10 + k * 18, 32, 10, C["cyan"]) for k in range(3)) + "</g>")
    cuerpo = (panel(W, H)
              + f'<text x="48" y="96" class="px" font-size="56" fill="{C["amber"]}">TRAYECTORIA</text>'
              + via + est + meta
              + f'<g><g transform="translate({xv} 0)">{tren}</g>'
              + f'<animateTransform attributeName="transform" type="translate" values="0 {y0 - 60};0 {ym - 120};0 {ym - 120}" keyTimes="0;.85;1" dur="9s" repeatCount="indefinite"/></g>')
    return documento(W, H, TRAYECTORIA_ALT, cuerpo)


def stack_movil():
    from build import HERRAMIENTAS
    certs = [
        ("googlecloud", "Cloud Load Balancing", "Google Cloud · 2026"),
        ("googlecloud", "App Dev Environment", "Google Cloud · 2026"),
        ("googlecloud", "Computing Foundations ×2", "Google Cloud · 2026"),
        ("cplusplus", "C++ Essentials 1", "Cisco · 2025"),
        ("java", "Diplomados Java y JS", "Politécnico de Colombia"),
    ]
    W = 1000
    out = (f'<text x="48" y="96" class="px" font-size="56" fill="{C["amber"]}">INVENTARIO</text>'
           f'<text x="48" y="146" class="sg" font-size="32" fill="{C["ink2"]}">Qué uso, para qué y dónde</text>')
    y = 200
    for g, items in HERRAMIENTAS:
        out += f'<text x="48" y="{y + 30}" class="px" font-size="40" fill="{C["cyan"]}">{e(g)}</text>'
        y += 56
        for slug, nombre, uso, donde in items:
            ic = icono_custom(slug, 64, y + 18, 72) if slug in ("powerbi", "sql", "java") else icono(slug, 64, y + 18, 72)
            out += (marco(48, y, W - 100, 108, "#101217", C["line"], 5, False) + ic
                    + f'<text x="160" y="{y + 48}" class="sgb" font-size="34" fill="{C["ink"]}">{e(nombre)}</text>'
                    + f'<text x="930" y="{y + 48}" text-anchor="end" class="mono" font-size="24" fill="{C["amber"]}">{e(donde)}</text>'
                    + f'<text x="160" y="{y + 88}" class="sg" font-size="28" fill="{C["ink2"]}">{e(uso)}</text>')
            y += 120
        y += 20
    y += 80
    y += 30
    out += r(48, y - 60, W - 100, 6, C["line"], ' class="pix"')
    out += f'<text x="48" y="{y + 20}" class="px" font-size="56" fill="{C["amber"]}">INSIGNIAS</text>'
    y += 70
    for slug, n, d in certs:
        ic = icono_custom("java", 72, y + 20, 80) if slug == "java" else icono(slug, 72, y + 20, 80)
        out += (marco(48, y, W - 100, 120, "#101217", C["line"], 5, False) + ic
                + f'<text x="180" y="{y + 56}" class="sgb" font-size="36" fill="{C["ink"]}">{e(n)}</text>'
                + f'<text x="180" y="{y + 98}" class="mono" font-size="26" fill="{C["ink3"]}">{e(d)}</text>')
        y += 140
    y += 30
    for k, (a, b) in enumerate([("PRUEBAS", "19"), ("SOLICITUDES", "26"), ("CASOS", "1,18 M")]):
        x = 48 + k * 310
        out += (f'<text x="{x}" y="{y}" class="mono" font-size="26" fill="{C["ink3"]}">{e(a)}</text>'
                f'<text x="{x}" y="{y + 64}" class="px" font-size="64" fill="{C["amber"]}">{e(b)}</text>')
    H = y + 120
    return documento(W, H, "Inventario: Java, Spring Boot, Python, FastAPI, SQL, MySQL, pandas, Power BI, Looker Studio, Jupyter, HTML, CSS, JavaScript, React, "
                     "Flutter, Dart, JUnit, pytest, Postman, Swagger, Docker, GitHub Actions y Git. Insignias de Google Cloud, C++ Essentials 1 de Cisco "
                     "y diplomados en Java y JavaScript del Politécnico de Colombia.", panel(W, H) + out)


def contribuciones_movil():
    W, H = 1000, 230
    cuerpo = (panel(W, H)
              + f'<text x="48" y="96" class="px" font-size="56" fill="{C["amber"]}">CONTRIBUCIONES</text>'
              + f'<text x="48" y="156" class="sg" font-size="34" fill="{C["ink2"]}">Mi actividad real del último año en GitHub,</text>'
              + f'<text x="48" y="200" class="sg" font-size="34" fill="{C["ink2"]}">actualizada cada 12 horas.</text>')
    return documento(W, H, "Contribuciones: mi actividad real del último año en GitHub.", cuerpo)


def en_linea_movil():
    W, H = 1000, 540
    filas = ""
    for k, (n, d) in enumerate(SERVICIOS):
        y = 240 + k * 100
        filas += (led(56, y - 26, C["green"], 22, k * .4)
                  + f'<text x="98" y="{y}" class="sgb" font-size="38" fill="{C["ink"]}">{e(n)}</text>'
                  + f'<text x="98" y="{y + 34}" class="mono" font-size="24" fill="{C["ink3"]}">{e(d)}</text>')
    cuerpo = (panel(W, H)
              + f'<text x="48" y="96" class="px" font-size="56" fill="{C["cyan"]}">EN LÍNEA</text>'
              + f'<text x="48" y="150" class="sg" font-size="32" fill="{C["ink2"]}">Mis proyectos funcionando ahora</text>'
              + filas)
    return documento(W, H, "En línea: API de CineX, Observatorio de Salud y casarendon.com, vigilados por UptimeRobot.", cuerpo)


def cierre_movil():
    W, H = 1000, 1080
    suelo = 960
    random.seed(23)
    cuerpo = (panel(W, H)
              + f'<g clip-path="url(#cm)"><clipPath id="cm"><rect x="6" y="6" width="{W - 18}" height="{H - 18}"/></clipPath>'
              + cielo(W, suelo, 0, .6) + estrellas(W, 600, 24, (40, 40, 960, 620))
              + edificios(0, 1000, suelo, 33, .75)
              + r(0, suelo, W, H - suelo, C["ground"], ' class="pix"') + r(0, suelo, W, 8, C["grass"], ' class="pix"') + "</g>"
              + f'<text x="56" y="140" class="px" font-size="80" fill="{C["ink"]}">¿TU EQUIPO</text>'
              + f'<text x="56" y="236" class="px" font-size="80" fill="{C["ink"]}">NECESITA UN</text>'
              + f'<text x="56" y="332" class="px" font-size="80" fill="{C["cyan"]}">PRACTICANTE?</text>'
              + f'<text x="60" y="410" class="sg" font-size="36" fill="{C["ink2"]}">Desarrollo de software o análisis</text>'
              + f'<text x="60" y="456" class="sg" font-size="36" fill="{C["ink2"]}">de datos · disponible desde ya</text>'
              + f'<text x="60" y="536" class="px" font-size="48" fill="{C["amber"]}">alexmejia0112@gmail.com</text>'
              + marco(60, 600, 520, 140, "#133a26", C["green"], 6, True)
              + f'<text x="320" y="656" text-anchor="middle" class="px" font-size="32" fill="#bff5da">PRÓXIMA ESTACIÓN</text>'
              + f'<text x="320" y="712" text-anchor="middle" class="px" font-size="48" fill="#ffffff">TU EQUIPO</text>'
              + r(150, 740, 8, suelo - 740, "#343844", ' class="pix"') + r(482, 740, 8, suelo - 740, "#343844", ' class="pix"')
              + sprite(ALEX_SALUDO, PALETA_ALEX, 760, suelo - 21 * 9, 9))
    return documento(W, H, "¿Tu equipo necesita un practicante? Desarrollo de software o análisis de datos, disponible desde ya. alexmejia0112@gmail.com", cuerpo)


def generar():
    return {
        "movil/portada.svg": portada_movil(),
        "movil/proyecto-observatorio.svg": tarjeta_movil("EN VIVO", C["green"], "OBSERVATORIO", "1,18 M casos de salud", "Python · SQL · MySQL", "VER EN VIVO",
                                                         "Observatorio de Salud Pública de Antioquia, en vivo."),
        "movil/proyecto-cinex.svg": tarjeta_movil("EN VIVO", C["green"], "CINEX", "API en Spring Boot", "19 pruebas · MySQL", "PROBAR API",
                                                  "CineX, en vivo: API REST en Spring Boot con 19 pruebas."),
        "movil/proyecto-numi.svg": tarjeta_movil("EN DESARROLLO", C["cyan"], "NUMI", "App con IA sin internet", "Flutter · equipo", "VER DETALLES",
                                                 "Numi, en desarrollo: app educativa con IA que funciona sin internet."),
        "movil/proyecto-casa-rendon.svg": tarjeta_movil("CLIENTE REAL", C["amber"], "CASA RENDÓN", "Sitio en producción", "React · equipo", "VISITAR",
                                                        "Casa Rendón, cliente real: sitio web en React en producción."),
        "movil/trayectoria.svg": trayectoria_movil(),
        "movil/stack.svg": stack_movil(),
        "movil/en-linea.svg": en_linea_movil(),
        "movil/cierre.svg": cierre_movil(),
    }
