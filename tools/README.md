# Herramientas del perfil

`make_header.py` genera `assets/encabezado-claro.svg` y `assets/encabezado-oscuro.svg` con la paleta y las fuentes del [portafolio](https://alexanderm-code.github.io/) (Schibsted Grotesk y JetBrains Mono, licencia OFL). Para cambiar un texto o una cifra del encabezado, edita las constantes al inicio del archivo y ejecuta:

```bash
pip install fonttools brotli
python tools/make_header.py
```
