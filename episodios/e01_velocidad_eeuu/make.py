# -*- coding: utf-8 -*-
"""e01 — Velocidad de M2 en EE.UU. (1959-hoy): la reversión a la media que nunca llega."""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import matplotlib.pyplot as plt

from src.utils import fetch_fred, estilo, sombrear, caja_veredicto, guardar


def main(outdir):
    estilo()
    v = fetch_fred("M2V")  # velocidad de M2, trimestral, desde 1959

    fig, ax = plt.subplots()
    ax.plot(v.index, v["M2V"], color="#1b6ca8", linewidth=1.8, label="Velocidad de M2 (PIB nominal / M2)")

    # Media del periodo "estable" que un cuantitativista tomaría como ancla
    media_pre90 = v.loc[:"1990-12-31", "M2V"].mean()
    ax.axhline(media_pre90, color="#555555", linestyle=":", linewidth=1.4)
    ax.annotate(f"media 1959-1990 = {media_pre90:.2f}\n(la 'media' a la que debería revertir)",
                xy=(v.index[10], media_pre90), xytext=(0, 8), textcoords="offset points",
                fontsize=9, color="#555555")

    ax.set_ylim(1.0, 2.35)

    # Rupturas: tras cada una, la velocidad se estabiliza en un nivel distinto
    sombrear(ax, "1990-01-01", "1997-12-31", "ruptura años 90:\nsube y no vuelve")
    sombrear(ax, "2008-09-01", "2010-12-31", "2008: cae\ny no vuelve")
    sombrear(ax, "2020-03-01", "2021-12-31", "2020: se hunde\ny no vuelve")

    import pandas as pd
    ax.annotate("aquí la TC funcionaba:\n30 años oscilando en torno a la media",
                xy=(pd.Timestamp("1972-01-01"), 1.50), fontsize=9, color="#1b6ca8", ha="center")

    ax.set_title("La velocidad de M2 en EE.UU. no revierte a la media (1959-2025)")
    ax.set_ylabel("Velocidad de circulación de M2")
    ax.set_xlabel("")
    ax.legend(loc="lower left")

    caja_veredicto(fig,
        "TC (reversión a la media): tras cada shock, V debería volver a su media. Observado: tras 1990, 2008 y 2020 se estabiliza en niveles distintos.\n"
        "FTPL: V refleja la demanda de dinero, que depende de expectativas y respaldo — no tiene por qué tener media fija.")
    fig.subplots_adjust(bottom=0.20)

    guardar(fig, v, outdir, "e01_velocidad_m2", "Reserva Federal de San Luis (FRED), serie M2V")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
    main(p.parse_args().outdir)
