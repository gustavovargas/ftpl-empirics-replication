# -*- coding: utf-8 -*-
"""Sección 7 del paper — la cláusula de "reversión a la media" de la velocidad, testada.

La defensa cuantitativista moderna admite que la velocidad varía pero sostiene que revierte a
una media (así la demanda de dinero seguiría siendo una función estable). Este módulo lo contrasta:
- ADF y Zivot-Andrews (raíz unitaria, la segunda con una ruptura endógena): ¿es la velocidad
  estacionaria alrededor de una media constante?
- Bai-Perron sobre el NIVEL: ¿cuántas veces salta la media, y a qué niveles?
- Semivida de reversión de un AR(1): si es de décadas, la "reversión" no es operativa.
Robustez: se repite con la Divisia M4 (el agregado amplio que prefiere la escuela del dinero amplio).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ruptures as rpt
from arch.unitroot import ADF, ZivotAndrews

from src.utils import RAIZ, fetch_fred, estilo

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def bateria(v, freq):
    """ADF, Zivot-Andrews y semivida AR(1) de una serie de velocidad."""
    v = v.dropna()
    adf, za = ADF(v), ZivotAndrews(v)
    vl = v.shift(1).dropna()
    rho = np.polyfit(vl, v.loc[vl.index], 1)[0]
    semivida = (np.log(0.5) / np.log(rho)) / freq  # en años
    return dict(n=len(v), adf_p=adf.pvalue, za_p=za.pvalue, semivida=semivida)


def rupturas_media(v, n_bkps=4, min_size=12):
    """Rupturas de la MEDIA del nivel (Bai-Perron clásico, coste l2). Devuelve fechas y medias."""
    x = v.values.reshape(-1, 1)
    idx = rpt.Dynp(model="l2", min_size=min_size, jump=1).fit(x).predict(n_bkps=n_bkps)
    cortes = [0] + idx
    tramos = []
    for i in range(len(cortes) - 1):
        a, b = cortes[i], cortes[i + 1]
        tramos.append((v.index[a], v.index[min(b, len(v) - 1)], v.iloc[a:b].mean()))
    return tramos


def velocidad_divisia():
    """Velocidad de la Divisia M4 = PIB nominal / Divisia M4 (nivel). La escala no afecta a los tests."""
    gdp = fetch_fred("GDP")["GDP"]
    dm4 = pd.read_excel(os.path.join(RAIZ, "data", "raw", "divisia_cfs.xlsx"),
                        sheet_name="Broad", skiprows=1).iloc[:, [0, 1]]
    dm4.columns = ["fecha", "DM4"]
    dm4["fecha"] = pd.to_datetime(dm4["fecha"], errors="coerce")
    dm4 = dm4.dropna().set_index("fecha")["DM4"].resample("QS").mean()
    idx = gdp.index.intersection(dm4.index)
    return (gdp.loc[idx] / dm4.loc[idx]).dropna()


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    estilo()
    # Muestra recortada a fin de 2025: el rótulo dice 1959-2025 y la caché puede traer 2026
    m2v = fetch_fred("M2V")["M2V"].dropna().loc[:"2025-12-31"]
    dm4v = velocidad_divisia().loc[:"2025-12-31"]

    t_m2 = bateria(m2v, 4)
    t_dm4 = bateria(dm4v, 4)
    tramos = rupturas_media(m2v)

    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.plot(m2v.index, m2v, color="#1b6ca8", linewidth=1.7, label="M2 velocity (quarterly)")
    media_global = m2v.mean()
    ax.axhline(media_global, color="#999", linestyle=":", linewidth=1.2)
    ax.annotate(f"full-sample mean = {media_global:.2f}\n(the 'mean' it should revert to)",
                xy=(m2v.index[5], media_global), xytext=(0, 8), textcoords="offset points",
                fontsize=9, color="#777")

    # Medias por régimen (Bai-Perron): la "media" salta a niveles distintos
    for a, b, m in tramos:
        ax.hlines(m, a, b, color="#c0392b", linewidth=2.6, zorder=5)
        ax.annotate(f"{m:.2f}", xy=(a + (b - a) / 2, m), xytext=(0, 6), textcoords="offset points",
                    ha="center", fontsize=9, color="#c0392b", fontweight="bold")
    ax.plot([], [], color="#c0392b", linewidth=2.6, label="Segment means (four imposed breaks, least-squares)")

    ax.set_title("The velocity of M2 shows no reversion to a fixed mean in 65 years")
    ax.set_ylabel("Velocity of circulation of M2")
    ax.legend(loc="upper left", fontsize=9)

    caja = (
        "Tests on M2 velocity (n={n}, 1959-2025):\n"
        "  ADF (H0 = unit root):         p = {adf:.2f}  →  unit root not rejected\n"
        "  Zivot-Andrews (1 break):      p = {za:.2f}  →  not rejected even with a break\n"
        "  AR(1) half-life of reversion: {hl:.0f} YEARS\n"
        "Robustness with Divisia M4: ADF p = {adf2:.2f}, half-life {hl2:.0f} years.\n"
        '"Mean reversion" requires a fixed mean: there is none.\n'
        "A mean re-estimated after every break anchors nothing."
    ).format(n=t_m2["n"], adf=t_m2["adf_p"], za=t_m2["za_p"], hl=t_m2["semivida"],
             adf2=t_dm4["adf_p"], hl2=t_dm4["semivida"])
    ax.text(0.02, 0.30, caja, transform=ax.transAxes, ha="left", va="top", fontsize=8.5,
            family="monospace", bbox=dict(boxstyle="round,pad=0.5", facecolor="#f7f5f0", edgecolor="#ccc"))

    

    fpng = os.path.join(outdir, "velocidad.png")
    fig.savefig(fpng, bbox_inches="tight", dpi=150)
    plt.close(fig)

    print("Sección 7 — reversión a la media de la velocidad:")
    print(f"  M2:          ADF p={t_m2['adf_p']:.2f}, ZA p={t_m2['za_p']:.2f}, semivida={t_m2['semivida']:.0f} años (n={t_m2['n']})")
    print(f"  Divisia M4:  ADF p={t_dm4['adf_p']:.2f}, ZA p={t_dm4['za_p']:.2f}, semivida={t_dm4['semivida']:.0f} años (n={t_dm4['n']})")
    print(f"  Regímenes de media detectados (M2): {[round(m,2) for _,_,m in tramos]}")
    print(f"OK -> {fpng}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=OUTDIR)
    main(p.parse_args().outdir)
