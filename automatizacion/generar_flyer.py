#!/usr/bin/env python3
"""Genera el flyer del menú del día usando plantilla_flyer.html (diseño "Historia de Instagram").
Uso: python3 generar_flyer.py AAAA-MM-DD"""
import base64, csv, datetime, html, json, pathlib, sys
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).resolve().parent
MESES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]
DIAS = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]


def b64(path):
    p = pathlib.Path(path)
    if not p.exists():
        return ""
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def construir(dia, fila, cfg):
    t = (AQUI / "plantilla_flyer.html").read_text(encoding="utf-8")
    d = datetime.date.fromisoformat(dia)
    vals = {
        "LOGO": b64(AQUI / "logo_principal.png"),
        "TAM_1": "40" if len(fila["opcion_1"]) <= 36 else "35",
        "TAM_2": "40" if len(fila["opcion_2"]) <= 36 else "35",
        "FECHA": f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month-1]}",
        "PEDIDOS": cfg.get("pedidos_hasta", ""),
        "FOTO_1": b64(AQUI / "fotos" / fila["foto_1"]) if fila.get("foto_1") else "",
        "FOTO_2": b64(AQUI / "fotos" / fila["foto_2"]) if fila.get("foto_2") else "",
        "OPCION_1": fila["opcion_1"],
        "OPCION_2": fila["opcion_2"],
        "PRECIO": cfg.get("precio", ""),
        "WHATSAPP": cfg.get("whatsapp", ""),
        "INSTAGRAM": cfg.get("instagram", ""),
    }
    for k, v in vals.items():
        t = t.replace("{{" + k + "}}", v if k in ("LOGO", "FOTO_1", "FOTO_2", "TAM_1", "TAM_2") else html.escape(v))
    # el recorte original de la foto 1 era para otra foto: centrarlo
    t = t.replace("object-position: 43.765% 50%", "object-position: 50% 50%")
    return t


def main():
    dia = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
    cfg = json.loads((AQUI / "config.json").read_text(encoding="utf-8"))
    with open(AQUI / "menus.csv", newline="", encoding="utf-8") as fh:
        filas = {r["fecha"]: r for r in csv.DictReader(fh)}
    if dia not in filas:
        sys.exit(f"No hay menú cargado para {dia} en menus.csv")
    out = AQUI / "salida"; out.mkdir(exist_ok=True)
    destino = out / f"flyer_{dia}.png"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.set_content(construir(dia, filas[dia], cfg), wait_until="networkidle")
        pg.wait_for_timeout(500)
        pg.screenshot(path=str(destino))
        b.close()
    print(destino)


if __name__ == "__main__":
    main()
