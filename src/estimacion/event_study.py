# -*- coding: utf-8 -*-
"""Test 2 del paper — el hecho de la remonetización (event study de panel).

Alinea los episodios en t=0 (mes de la reforma) y traza la trayectoria media de
(a) los saldos reales M/P y (b) el nivel de precios, indexados a la reforma=100.

El hecho a establecer: tras la reforma, los saldos reales SE RECUPERAN (remonetización)
mientras la inflación se desploma — lo contrario de lo que predeciría una TC estricta,
en la que frenar los precios exigiría frenar el dinero.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.utils import estilo
from src.estimacion.series import (cargar_c01_austria, cargar_c03_hungria, cargar_c23_mexico,
                                   cargar_c30_turquia, cargar_e04, cargar_e05, cargar_e06,
                                   cargar_e08)

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
VENTANA = (-24, 18)  # meses respecto a la reforma


def _serie_por_offset(serie, reforma, rango):
    """Reindexa una serie mensual a offset entero de meses respecto a la reforma."""
    ref = pd.Timestamp(reforma).to_period("M")
    s = serie.loc[rango[0]:rango[1]].dropna()
    s = s.copy()
    s.index = (s.index.to_period("M") - ref).map(lambda x: x.n)
    s = s[~s.index.duplicated(keep="first")]
    return s


def panel_episodios():
    """Desinflaciones con precio (y dinero donde exista) — reutiliza los cargadores."""
    return [cargar_c01_austria(), cargar_e04(), cargar_c03_hungria(), cargar_e05(),
            cargar_e06(), cargar_e08(), cargar_c23_mexico(), cargar_c30_turquia()]


def construir(cfgs):
    idx = range(VENTANA[0], VENTANA[1] + 1)
    precios, reales = {}, {}
    for cfg in cfgs:
        nombre = cfg["label"].split(" · ")[1]
        p = _serie_por_offset(cfg["precio"], cfg["reforma"], cfg["rango"])
        p = 100 * p / p.loc[0]
        precios[nombre] = p.reindex(idx)
        if cfg.get("dinero") is not None:
            mm = _serie_por_offset(cfg["dinero"], cfg["reforma"], cfg["rango"])
            pp = _serie_por_offset(cfg["precio"], cfg["reforma"], cfg["rango"])
            rb = (mm / pp).dropna()
            rb = 100 * rb / rb.loc[0]
            reales[nombre] = rb.reindex(idx)
    return pd.DataFrame(precios), pd.DataFrame(reales)


COLORES_EP = {"Germany 1923": "#1b6ca8", "Brazil 1994": "#e67e22", "Israel 1985": "#8e44ad",
              "Austria 1922": "#148f77", "Hungary 1924": "#b7950b",
              "Mexico 1987": "#616a6b", "Turkey 2001": "#2e4053"}


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    estilo()
    cfgs = panel_episodios()
    precios, reales = construir(cfgs)

    fig, ax = plt.subplots(figsize=(11.5, 6.5))
    x = reales.index
    for col in reales.columns:
        ax.plot(x, reales[col], color=COLORES_EP.get(col, "#9e9e9e"), linewidth=1.3,
                alpha=0.85, label=col)
    media = reales.mean(axis=1)
    sd = reales.std(axis=1)
    ax.fill_between(x, media - sd, media + sd, color="#c0392b", alpha=0.10, zorder=1)
    ax.plot(x, media, color="#c0392b", linewidth=3.0, label="Panel mean", zorder=5)

    ax.axvline(0, color="#333", linestyle="--", linewidth=1.4)
    ax.axhline(100, color="#999", linewidth=0.8, linestyle=":")
    ax.annotate("reform", xy=(0, ax.get_ylim()[1]), xytext=(5, -6),
                textcoords="offset points", fontsize=10, color="#333", va="top")
    ax.annotate(f"remonetisation: average real balances\nmultiply by {media.loc[12]/media.loc[0]:.1f} in the 12 months\nafter the reform, while inflation collapses",
                xy=(12, media.loc[12]), xytext=(-260, 10), textcoords="offset points",
                fontsize=10, color="#c0392b", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.2))
    ax.annotate("flight from money\n(high inflation)", xy=(-15, media.loc[-15]),
                xytext=(-10, 40), textcoords="offset points", fontsize=9, color="#666")

    ax.set_title("Test 2 — The remonetisation fact: real balances rise after the reform")
    ax.set_ylabel("Real balances M/P (reform = 100)")
    ax.set_xlabel("Months from the reform")
    ax.legend(loc="upper left", fontsize=9)
    

    fpng = os.path.join(outdir, "event_study.png")
    fig.savefig(fpng, bbox_inches="tight", dpi=150)
    plt.close(fig)
    precios.to_csv(os.path.join(outdir, "event_study_precios.csv"))
    reales.to_csv(os.path.join(outdir, "event_study_saldos_reales.csv"))

    # Estadístico-resumen
    rb_media = reales.mean(axis=1)
    print("\nTest 2 — saldos reales medios (reforma=100):")
    for t in [-12, -6, 0, 6, 12]:
        if t in rb_media.index and not np.isnan(rb_media.loc[t]):
            print(f"  t={t:+d} meses: {rb_media.loc[t]:.0f}")
    ganancia = rb_media.loc[12] / rb_media.loc[0] if 12 in rb_media.index else np.nan
    print(f"  Remonetización media a +12 meses: x{ganancia:.2f} sobre el nivel de la reforma.")
    print(f"OK -> {fpng}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=OUTDIR)
    main(p.parse_args().outdir)
