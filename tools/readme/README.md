# Paneles del README

`build.py` genera los paneles en pixel art de `assets/readme/`: Medellín de noche con el Metrocable, tarjetas de proyecto, la trayectoria como una línea de metro, el inventario de herramientas con insignias y el cierre.

```bash
pip install fonttools brotli
python tools/readme/build.py
```

Para cambiar un dato (un proyecto, una cifra, una certificación), edítalo en `build.py` y vuelve a ejecutarlo. Fuentes: Tiny5, Space Grotesk y JetBrains Mono (OFL). Íconos: Simple Icons (CC0).

`contribuciones.py` dibuja mis contribuciones reales de GitHub como un edificio de Medellín de noche (cada ventana es un día). Lo ejecuta todos los días el workflow `contribuciones.yml` y lo publica en la rama `output`. Para probarlo sin internet: `CONTRIB_DEMO=1 python tools/readme/contribuciones.py dist`.
