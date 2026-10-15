# -*- coding: utf-8 -*-
"""e04 — Alemania 1922-1924: la hiperinflación termina con la imprenta encendida.

Panel A: la hiperinflación completa (donde la TC brilla: dinero y precios suben juntos
10 órdenes de magnitud). Panel B: los 12 meses posteriores a la estabilización (donde
falla: el dinero se multiplica por 4 y los precios no se mueven).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from src.utils import RAIZ, estilo, caja_veredicto, guardar

CSV = os.path.join(RAIZ, "data", "manual", "alemania_1923.csv")
ESTABILIZACION = pd.Timestamp("1923-11-15")  # Rentenmark + tope de emisión + reforma fiscal


def main(outdir):
    estilo()
    df = pd.read_csv(CSV, comment="#", parse_dates=["fecha"]).set_index("fecha")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 6.0))

    # ── Panel A: hiperinflación completa, índices ene-1922 = 100, escala log ──
    p = 100 * df["indice_precios_1913_100"] / df["indice_precios_1913_100"].iloc[0]
    m = 100 * df["circulacion_marcos"] / df["circulacion_marcos"].iloc[0]
    ax1.plot(p.index, p, color="#1e8449", linewidth=2.2, label="Precios mayoristas (ene. 1922 = 100)")
    ax1.plot(m.index, m, color="#1b6ca8", linewidth=2.0, label="Billetes en circulación (ene. 1922 = 100)")
    ax1.set_yscale("log")
    ax1.axvline(ESTABILIZACION, color="#c0392b", linestyle="--", linewidth=1.3)
    ax1.annotate("15-11-1923:\nRentenmark, tope de emisión\ny reforma fiscal",
                 xy=(ESTABILIZACION, 10**3), xytext=(-150, 0), textcoords="offset points",
                 fontsize=9, color="#c0392b")
    ax1.annotate("aquí la TC brilla:\ndinero y precios suben juntos\ndiez órdenes de magnitud",
                 xy=(pd.Timestamp("1922-12-01"), 10**7), fontsize=9, color="#444444")
    ax1.set_title("A. La hiperinflación (1922-1924)")
    ax1.set_ylabel("Índice, escala log (ene. 1922 = 100)")
    ax1.legend(loc="lower right", fontsize=9)
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # ── Panel B: los 12 meses tras la estabilización, dic-1923 = 100, lineal ──
    zoom = df.loc["1923-12-01":]
    pz = 100 * zoom["indice_precios_1913_100"] / zoom["indice_precios_1913_100"].iloc[0]
    mz = 100 * zoom["circulacion_marcos"] / zoom["circulacion_marcos"].iloc[0]
    ax2.plot(pz.index, pz, color="#1e8449", linewidth=2.4, marker="o", markersize=4,
             label="Precios mayoristas (dic. 1923 = 100)")
    ax2.plot(mz.index, mz, color="#1b6ca8", linewidth=2.4, marker="o", markersize=4,
             label="Billetes en circulación (dic. 1923 = 100)")
    ax2.annotate(f"la circulación se multiplica por {mz.iloc[-1]/100:.1f}\nen el año posterior a la estabilización…",
                 xy=(mz.index[-1], mz.iloc[-1]), xytext=(-230, -60), textcoords="offset points",
                 fontsize=10, color="#1b6ca8", fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="#1b6ca8", lw=1))
    ax2.annotate(f"…y los precios suben un {pz.iloc[-1]-100:.0f}%",
                 xy=(pz.index[-1], pz.iloc[-1]), xytext=(-160, 22), textcoords="offset points",
                 fontsize=10, color="#1e8449", fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="#1e8449", lw=1))
    ax2.set_title("B. Los 12 meses siguientes: imprenta encendida, precios quietos")
    ax2.set_ylabel("Índice (dic. 1923 = 100)")
    ax2.legend(loc="center left", fontsize=9)
    MES = {1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun",
           7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"}
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, _: (lambda d: f"{MES[d.month]}-{d.year % 100:02d}")(mdates.num2date(x))))

    caja_veredicto(fig,
        "TC: los precios siguen a la cantidad de dinero — cierto en la subida (panel A), falso en el punto de giro: tras el 15-11-1923 la circulación se cuadruplica y los precios no se mueven (panel B).\n"
        "FTPL: lo que cambió no fue el ritmo de la imprenta sino el régimen fiscal (tope legal de crédito al gobierno y presupuesto equilibrado en semanas): restaurado el respaldo, la demanda de\n"
        "dinero se recuperó y absorbió la remonetización. Sargent: 'no fue simplemente la cantidad creciente de billetes lo que causó la hiperinflación'.")
    fig.subplots_adjust(bottom=0.22, wspace=0.22)

    guardar(fig, df, outdir, "e04_alemania_1923",
            "Sargent (1982), 'The Ends of Four Big Inflations', tablas G1 y G4 (datos de Young); digitalización propia")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
    main(p.parse_args().outdir)
