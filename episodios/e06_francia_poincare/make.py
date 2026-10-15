# -*- coding: utf-8 -*-
"""e06 — Francia 1926 (Poincaré): la estabilización por pura noticia fiscal.

Panel A: 1922-1928 — el franco y los precios se desbocan con la crisis fiscal y política,
y giran en seco cuando Poincaré vuelve al gobierno (23-jul-1926). Panel B: zoom del giro.
Sin reforma monetaria, sin nueva moneda, sin contracción de billetes: solo cambió el
régimen fiscal esperado.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from src.utils import fetch_fred, estilo, caja_veredicto, guardar

POINCARE = pd.Timestamp("1926-07-23")  # gobierno de unión nacional; Poincaré también en Hacienda

MES = {1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun",
       7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"}


def main(outdir):
    estilo()
    fx = fetch_fred("M1404BUSM306NNBR")["M1404BUSM306NNBR"]   # francos por dólar (NBER m14076)
    wpi = fetch_fred("M04057FRM360NNBR")["M04057FRM360NNBR"]  # precios mayoristas Francia (NBER)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 6.0))

    # ── Panel A: 1922-1928, índices ene-1922 = 100 ────────────────────────────
    v = slice("1922-01-01", "1928-12-31")
    f = 100 * fx.loc[v] / fx.loc["1922-01-01"]
    p = 100 * wpi.loc[v] / wpi.loc["1922-01-01"]
    ax1.plot(f.index, f, color="#c0392b", linewidth=2.0,
             label="Francos por dólar (ene. 1922 = 100; subir = franco más débil)")
    ax1.plot(p.index, p, color="#1e8449", linewidth=2.2, label="Precios mayoristas (ene. 1922 = 100)")
    ax1.axvline(POINCARE, color="#1b6ca8", linestyle="--", linewidth=1.4)
    ax1.annotate("23-jul-1926:\nvuelve Poincaré", xy=(POINCARE, 120), xytext=(8, 0),
                 textcoords="offset points", fontsize=9, color="#1b6ca8", fontweight="bold")
    ax1.annotate("crisis fiscal y política:\n7 gobiernos en 1925-26,\ndeuda flotante impagable,\nmiedo al impuesto al capital",
                 xy=(pd.Timestamp("1923-03-01"), 235), fontsize=9, color="#444444")
    ax1.set_title("A. La crisis del franco (1922-1928)")
    ax1.set_ylabel("Índice (ene. 1922 = 100)")
    ax1.legend(loc="upper left", fontsize=9)
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # ── Panel B: zoom ene-1926 → dic-1927, jun-1926 = 100 ─────────────────────
    z = slice("1926-01-01", "1927-12-31")
    fz = 100 * fx.loc[z] / fx.loc["1926-06-01"]
    pz = 100 * wpi.loc[z] / wpi.loc["1926-06-01"]
    ax2.plot(fz.index, fz, color="#c0392b", linewidth=2.4, marker="o", markersize=4,
             label="Francos por dólar (jun. 1926 = 100)")
    ax2.plot(pz.index, pz, color="#1e8449", linewidth=2.4, marker="o", markersize=4,
             label="Precios mayoristas (jun. 1926 = 100)")
    ax2.set_ylim(64, 124)
    ax2.axvline(POINCARE, color="#1b6ca8", linestyle="--", linewidth=1.4)
    ax2.annotate("vuelve\nPoincaré", xy=(POINCARE, 120), xytext=(-58, -4),
                 textcoords="offset points", fontsize=9, color="#1b6ca8", fontweight="bold")
    apreciacion = 100 * (1 - fz.loc["1926-12-01"] / fz.loc["1926-07-01"])
    caida_p = 100 * (1 - pz.loc["1926-12-01"] / pz.loc["1926-07-01"])
    ax2.annotate(f"el franco se aprecia un {apreciacion:.0f}% en cinco meses — antes de que lo grueso\ndel ajuste fiscal surtiera efecto: puro cambio de expectativas",
                 xy=(pd.Timestamp("1926-12-01"), fz.loc["1926-12-01"]), xytext=(-45, -38),
                 textcoords="offset points", fontsize=10, color="#c0392b", fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1))
    ax2.annotate(f"los precios CAEN un {caida_p:.0f}%\nsin contracción monetaria: la circulación\nde billetes AUMENTÓ (Sargent 1984)",
                 xy=(pd.Timestamp("1927-03-01"), pz.loc["1927-03-01"]), xytext=(6, 30),
                 textcoords="offset points", fontsize=10, color="#1e8449", fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="#1e8449", lw=1))
    ax2.set_title("B. El giro: estabilización por decreto de credibilidad")
    ax2.set_ylabel("Índice (jun. 1926 = 100)")
    ax2.legend(loc="upper right", fontsize=9)
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, _: (lambda d: f"{MES[d.month]}-{d.year % 100:02d}")(mdates.num2date(x))))

    caja_veredicto(fig,
        "TC: sin cambio en la cantidad de dinero no hay por qué esperar giro en los precios — y la circulación de billetes apenas varió antes del giro y AUMENTÓ después,\n"
        "cuando el Banco de Francia compraba divisas para frenar la apreciación. Observado: el franco y los precios giraron en la semana del cambio de gobierno.\n"
        "FTPL: el nivel de precios siguió al valor esperado del respaldo fiscal (impuestos +, caja de amortización de la deuda), no a la cantidad de dinero. Sargent: 'los métodos de Poincaré'.")
    fig.subplots_adjust(bottom=0.22, wspace=0.24)

    df_out = pd.DataFrame({"francos_por_dolar": fx, "wpi_francia": wpi}).loc[v]
    guardar(fig, df_out, outdir, "e06_francia_poincare",
            "NBER Macrohistory vía FRED (M1404BUSM306NNBR, M04057FRM360NNBR)")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
    main(p.parse_args().outdir)
