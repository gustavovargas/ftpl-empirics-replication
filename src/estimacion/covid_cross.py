# -*- coding: utf-8 -*-
"""Nivel B, test 6a — la carrera de caballos del COVID, con la eurozona como control.

La comparación fiscal-vs-dinero en el pool de países está confundida por mezclar regímenes
monetarios distintos y outliers (Polonia). El test LIMPIO usa la eurozona como experimento
natural: 7 países con la MISMA M3 y el mismo BCE -> la política monetaria es constante por
construcción, así que cualquier variación de inflación entre ellos NO puede ser de cantidad de
dinero. Panel A: dentro del euro, la variable fiscal de Barro-Bianchi ordena la inflación.
Panel B: el pool completo, más ruidoso (como en el propio Barro-Bianchi), con las R² de todas
las variantes reportadas por integridad.

Variable fiscal de Barro-Bianchi (2023): gasto COVID / (deuda/PIB 2019 x duración 2019).
Intuición FTPL: el mismo gasto no respaldado es más inflacionista cuanto menor es la base de
deuda que lo absorbe y más corta su duración.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.utils import RAIZ, fetch_fred, estilo

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
CSV = os.path.join(RAIZ, "data", "censo", "covid_cross.csv")


def _fit(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    b, a = np.polyfit(x, y, 1)
    r2 = 1 - np.sum((y - (a + b * x)) ** 2) / np.sum((y - y.mean()) ** 2)
    return b, a, r2, np.corrcoef(x, y)[0, 1]


def crecimiento_m3(codigo):
    s = fetch_fred(codigo)[codigo]
    return 100 * (s.loc["2021-12-01"] / s.loc["2019-12-01"] - 1)


def _scatter(ax, x, y, labels, xlabel, titulo, color):
    ax.scatter(x, y, s=75, color=color, zorder=3, edgecolors="white", linewidths=0.8)
    for xi, yi, l in zip(x, y, labels):
        ax.annotate(l, xy=(xi, yi), xytext=(4, 3), textcoords="offset points", fontsize=8, color="#444")
    b, a, r2, r = _fit(x, y)
    xs = np.linspace(min(x), max(x), 50)
    ax.plot(xs, a + b * xs, color=color, linewidth=1.8, alpha=0.75, linestyle="--")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Cumulative inflation 2020-2023 (%)")
    ax.set_title(f"{titulo}\nR² = {r2:.2f}   (n = {len(x)})", fontsize=11.5)
    return b, r2, r


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    estilo()
    df = pd.read_csv(CSV, comment="#")
    df["f_bb"] = df["fiscal_covid"] / ((df["deuda_pib_2019"] / 100) * df["duracion_2019"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 6.4))

    # ── Panel A: DENTRO de la eurozona (misma M3) — el test limpio ─────────────
    euro = df[df["euro"] == 1]
    bA, r2A, rA = _scatter(ax1, euro["f_bb"], euro["infl_acum_20_23"], euro["codigo"],
                           "Barro–Bianchi fiscal impulse\n[spending / (debt × duration)]",
                           "A. Inside the euro (SAME monetary policy):\nthe fiscal variable orders inflation", "#1e8449")

    # ── Panel B: no-euro, inflación vs crecimiento de M amplia ────────────────
    con_m3 = df[df["fred_m3"].notna() & (df["fred_m3"] != "")].copy()
    con_m3["m3_growth"] = con_m3["fred_m3"].map(crecimiento_m3)
    bB, r2B, rB = _scatter(ax2, con_m3["m3_growth"], con_m3["infl_acum_20_23"], con_m3["codigo"],
                           "Broad money (M3) growth 2020-2021 (%)",
                           "B. Outside the euro: broad money also\ncorrelates, but cannot explain the euro area", "#1b6ca8")

    # R² del pool completo con cada variante (para la nota)
    _, _, r2_crudo, _ = _fit(df["fiscal_covid"], df["infl_acum_20_23"])
    _, _, r2_bb_pool, _ = _fit(df["f_bb"], df["infl_acum_20_23"])

    fig.suptitle("The COVID horse race: the euro area as a constant-monetary-policy experiment",
                 fontsize=12.5, fontweight="bold")
    fig.subplots_adjust(top=0.86, wspace=0.22)

    fpng = os.path.join(outdir, "covid_cross.png")
    fig.savefig(fpng, bbox_inches="tight", dpi=150)
    plt.close(fig)
    df.to_csv(os.path.join(outdir, "covid_cross_datos.csv"), index=False)

    print("Test 6a — carrera de caballos COVID:")
    print(f"  A. EUROZONA (misma M3, n={len(euro)}): inflación ~ fiscal-BB -> R²={r2A:.2f}, r={rA:+.2f}  <- test limpio")
    print(f"  B. no-euro (n={len(con_m3)}): inflación ~ M amplia -> R²={r2B:.2f}, r={rB:+.2f}")
    print(f"  Pool completo (n={len(df)}): fiscal crudo R²={r2_crudo:.2f}; fiscal Barro-Bianchi R²={r2_bb_pool:.2f}")
    print(f"OK -> {fpng}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=OUTDIR)
    main(p.parse_args().outdir)
