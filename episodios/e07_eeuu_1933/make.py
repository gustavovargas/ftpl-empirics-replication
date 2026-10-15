# -*- coding: utf-8 -*-
"""e07 — EE.UU. 1933: la reflación de FDR — el test en dirección contraria.

Panel A: la Gran Contracción 1929-1937 (dinero, precios y producción caen juntos — la
evidencia clásica de Friedman). Panel B: el giro de abril de 1933 — precios y producción
suben en cuanto FDR abandona el oro y anuncia déficits de emergencia, con M2 aún clavada
en su mínimo. El dinero (entradas de oro) llega en 1934: después del giro.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from src.utils import fetch_fred, estilo, caja_veredicto, guardar

OFF_GOLD = pd.Timestamp("1933-04-19")   # embargo del oro; FDR anuncia la política de reflación

MES = {1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun",
       7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"}


def main(outdir):
    estilo()
    wpi = fetch_fred("PPIACO")["PPIACO"]                 # precios al por mayor, desde 1913
    m2 = fetch_fred("M1444AUSM027SNBR")["M1444AUSM027SNBR"]  # money stock Friedman-Schwartz (SA)
    ind = fetch_fred("INDPRO")["INDPRO"]                 # producción industrial

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 6.0))

    # ── Panel A: 1929-1937, índices ene-1929 = 100 ────────────────────────────
    v = slice("1929-01-01", "1937-12-31")
    series = {"Precios al por mayor": (wpi, "#1e8449"),
              "M2 (Friedman-Schwartz)": (m2, "#1b6ca8"),
              "Producción industrial": (ind, "#8e44ad")}
    for nombre, (s, color) in series.items():
        si = 100 * s.loc[v] / s.loc["1929-01-01"]
        ax1.plot(si.index, si, color=color, linewidth=2.0, label=nombre)
    ax1.axvline(OFF_GOLD, color="#c0392b", linestyle="--", linewidth=1.4)
    ax1.annotate("abr-1933: FDR abandona\nel oro y anuncia reflación\ny déficits de emergencia", xy=(OFF_GOLD, 107),
                 xytext=(-165, 0), textcoords="offset points", fontsize=9, color="#c0392b")
    ax1.annotate("aquí la TC brilla:\nM cae un tercio y precios y\nproducción se hunden con ella",
                 xy=(pd.Timestamp("1929-10-01"), 55), fontsize=9, color="#444444")
    ax1.set_title("A. La Gran Contracción y el giro (1929-1937)")
    ax1.set_ylabel("Índice (ene. 1929 = 100)")
    ax1.legend(loc="upper right", fontsize=9)
    ax1.xaxis.set_major_locator(mdates.YearLocator(2))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # ── Panel B: zoom ene-1932 → dic-1934, abr-1933 = 100 ─────────────────────
    z = slice("1932-01-01", "1934-12-31")
    base = "1933-04-01"
    wz = 100 * wpi.loc[z] / wpi.loc[base]
    mz = 100 * m2.loc[z] / m2.loc[base]
    iz = 100 * ind.loc[z] / ind.loc[base]
    ax2.plot(wz.index, wz, color="#1e8449", linewidth=2.4, marker="o", markersize=3.5,
             label="Precios al por mayor (abr. 1933 = 100)")
    ax2.plot(mz.index, mz, color="#1b6ca8", linewidth=2.4, marker="o", markersize=3.5,
             label="M2 (abr. 1933 = 100)")
    ax2.plot(iz.index, iz, color="#8e44ad", linewidth=1.8, alpha=0.75,
             label="Producción industrial (abr. 1933 = 100)")
    ax2.axvline(OFF_GOLD, color="#c0392b", linestyle="--", linewidth=1.4)

    subida_p = wz.loc["1933-10-01"] - 100
    subida_m = mz.loc["1933-10-01"] - 100
    ax2.annotate(f"los precios giran AQUÍ:\n+{subida_p:.0f}% en seis meses…",
                 xy=(pd.Timestamp("1933-08-01"), wz.loc["1933-08-01"]), xytext=(-150, 30),
                 textcoords="offset points", fontsize=10, color="#1e8449", fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="#1e8449", lw=1))
    ax2.annotate(f"…con M2 clavada en su mínimo\n(+{subida_m:.0f}% en esos seis meses);\nel dinero llega en 1934, con el oro",
                 xy=(pd.Timestamp("1933-10-01"), mz.loc["1933-10-01"]), xytext=(10, -48),
                 textcoords="offset points", fontsize=10, color="#1b6ca8", fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="#1b6ca8", lw=1))
    ax2.set_title("B. El giro de abril de 1933: los precios primero, el dinero después")
    ax2.set_ylabel("Índice (abr. 1933 = 100)")
    ax2.legend(loc="upper left", fontsize=9)
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, _: (lambda d: f"{MES[d.month]}-{d.year % 100:02d}")(mdates.num2date(x))))

    caja_veredicto(fig,
        "TC: los precios no debían girar hasta que girase M — y M2 tocó mínimo en abril de 1933 y apenas se movió en seis meses (+2%) mientras los precios subían un 18% y la producción casi un 50%.\n"
        "FTPL (Jacobson-Leeper-Preston 2019): FDR convirtió la deuda en un derecho a dólares (no a oro) y anunció déficits de emergencia SIN respaldo hasta recuperar el nivel de precios:\n"
        "una reflación por cambio de régimen fiscal. El test funciona en ambas direcciones: la misma noticia fiscal que paró los precios en 1923/1926 los arrancó en 1933.")
    fig.subplots_adjust(bottom=0.22, wspace=0.24)

    df_out = pd.DataFrame({"WPI": wpi, "M2_FS": m2, "IndPro": ind}).loc[v]
    guardar(fig, df_out, outdir, "e07_eeuu_1933",
            "FRED (PPIACO, M1444AUSM027SNBR [NBER/Friedman-Schwartz], INDPRO)")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
    main(p.parse_args().outdir)
