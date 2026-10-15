# -*- coding: utf-8 -*-
"""e09 — Somalia 1991-2011: dinero fiat sin Estado — el suelo del valor es el coste de producción.

Gráfico distinto a los demás episodios: puntos DOCUMENTADOS sobre una línea de eventos
(no existe serie mensual fiable del periodo sin Estado). El mensaje: el chelín no valió
lo que dictara su cantidad ni cayó a cero al desaparecer el emisor — convergió al coste
de producir e importar el billete, como una mercancía.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import matplotlib.pyplot as plt
import pandas as pd

from src.utils import RAIZ, estilo, caja_veredicto, guardar

CSV = os.path.join(RAIZ, "data", "manual", "somalia.csv")

EVENTOS = [  # (fecha, texto, color, altura_y)
    ("1991-01-26", "cae Barre: desaparecen\nel Estado y el banco central", "#c0392b", 2350),
    ("1996-06-15", "Aideed encarga ~165.000 M\n(imprenta de Ottawa)", "#7a3d02", 55000),
    ("1999-06-15", "Puntland importa\nbilletes (Indonesia)", "#7a3d02", 2350),
    ("2001-03-15", "comerciantes importan\notros 60.000 M", "#7a3d02", 3550),
    ("2009-06-15", "gobierno de transición:\nreapertura del banco central", "#1b6ca8", 2350),
]

SUELO = 33333  # 1.000 SoSh a ~0,03 USD = coste aprox. de producir+importar el billete


def main(outdir):
    estilo()
    df = pd.read_csv(CSV, comment="#", parse_dates=["fecha"])

    fig, ax = plt.subplots(figsize=(12.5, 6.5))
    ax.set_yscale("log")
    ax.set_xlim(pd.Timestamp("1990-01-01"), pd.Timestamp("2012-12-31"))
    ax.set_ylim(2000, 90000)

    # Puntos documentados + interpolación ilustrativa (explícitamente etiquetada)
    ax.plot(df["fecha"], df["sosh_por_usd"], linestyle=":", color="#888888", linewidth=1.2, zorder=1)
    ax.scatter(df["fecha"], df["sosh_por_usd"], s=90, color="#1e8449", zorder=3)
    ax.annotate("● puntos documentados (Luther 2015; Fitzgerald 2002)",
                xy=(pd.Timestamp("1993-01-01"), 15500), fontsize=9, color="#1e8449")
    for _, r in df.iterrows():
        ax.annotate(f"{r['sosh_por_usd']:,.0f}".replace(",", "."),
                    xy=(r["fecha"], r["sosh_por_usd"]), xytext=(0, 10),
                    textcoords="offset points", ha="center", fontsize=9,
                    color="#1e8449", fontweight="bold")
    ax.annotate("trazo punteado: interpolación ilustrativa\n(no existe serie mensual fiable del periodo)",
                xy=(pd.Timestamp("1997-06-01"), 7300), fontsize=8.5, color="#888888", ha="center")

    # Suelo del valor: coste de producir e importar el billete
    ax.axhline(SUELO, color="#c0392b", linewidth=1.6, linestyle="-", alpha=0.85)
    ax.annotate("suelo: coste de producir e importar el billete de 1.000 SoSh (~0,03 $)\n"
                "— hacia 2002 el señoreaje de falsificar se agotó (Mubarak 2003; Luther 2015)",
                xy=(pd.Timestamp("1990-06-01"), SUELO), xytext=(0, 8), textcoords="offset points",
                fontsize=9, color="#c0392b")

    # Eventos
    for fecha, texto, color, altura in EVENTOS:
        f = pd.Timestamp(fecha)
        ax.axvline(f, color=color, linestyle="--", linewidth=1.0, alpha=0.7)
        ax.annotate(texto, xy=(f, altura), xytext=(4, 0), textcoords="offset points",
                    fontsize=8.5, color=color, va="bottom")

    ax.set_title("Somalia 1991-2011: el chelín sin Estado no valió su cantidad — valió su coste de producción")
    ax.set_ylabel("Chelines somalíes por dólar (escala log; subir = chelín más débil)")

    caja_veredicto(fig,
        "Sin emisor, el chelín no cayó a cero (siguió circulando 20 años) ni obedeció a una 'cantidad controlada' (las oleadas de falsificación hicieron la oferta elástica).\n"
        "Convergió al coste marginal de producir e importar billetes y se ancló ahí: la economía de un dinero-MERCANCÍA. Ni TC ni FTPL puras: el caso ilustra la teoría del dinero\n"
        "como activo — su valor necesita un respaldo (fiscal) o un coste real de producción; cuando desapareció el primero, mandó el segundo.")
    fig.subplots_adjust(bottom=0.20)

    guardar(fig, df.set_index("fecha"), outdir, "e09_somalia",
            "Luther (2015, Public Choice); Luther & White (2016); Fitzgerald (2002); Symes (2006)")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
    main(p.parse_args().outdir)
