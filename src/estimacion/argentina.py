# -*- coding: utf-8 -*-
"""Caso-objeción — Argentina kirchnerista (2003-2015): superávit + emisión cambiaria + inflación.

La objeción cuantitativista: "hubo inflación porque se emitía para comprar dólares (mantener el
peso competitivo); se inunda la plaza de pesos y se va al dólar y a bienes". Correcto en su
mecánica. Pero dos hechos lo reinterpretan:

Panel A — el desacople dinero/precios: M2 creció de forma bastante ESTABLE (~25-40%) durante todo
el periodo, mientras la inflación (corregida) se aceleró de ~5% a ~30%+. Mismo dinero, inflación
creciente -> lo que cambió fue la DEMANDA de dinero (velocidad), no la cantidad.

Panel B — la secuencia temporal: la fase de MÁXIMA compra de dólares (2003-2011, acumulación de
reservas) fue la de MENOR inflación (remonetización tras el colapso de 2001, respaldo creciente);
la inflación se disparó cuando el respaldo se deterioró y las reservas se DRENARON hacia fines
fiscales (2011-2015). La emisión por compra de dólares crea pesos contra un activo de calidad
(reservas); el problema vino cuando ese activo se drenó.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import matplotlib.pyplot as plt
import pandas as pd

from src.utils import RAIZ, fetch_fred, estilo

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
CSV = os.path.join(RAIZ, "data", "manual", "argentina_inflacion.csv")


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    estilo()
    infl = pd.read_csv(CSV, comment="#")
    m2 = fetch_fred("MYAGM2ARM189N")["MYAGM2ARM189N"]
    res = fetch_fred("TRESEGARM052N")["TRESEGARM052N"].loc["2003":"2015"]

    # crecimiento interanual de M2 en diciembre de cada año
    m2yoy = 100 * m2.pct_change(12)
    m2_dic = {a: m2yoy.loc[f"{a}-12-01"] for a in infl["anio"] if f"{a}-12-01" in m2yoy.index}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 6.2))

    # ── Panel A: crecimiento de M2 vs inflación corregida ─────────────────────
    anios = infl["anio"].values
    ax1.plot(anios, infl["infl_corregida"], color="#c0392b", linewidth=2.4, marker="o",
             markersize=5, label="Inflación corregida (interanual)")
    xm = [a for a in anios if a in m2_dic]
    ym = [m2_dic[a] for a in xm]
    ax1.plot(xm, ym, color="#1b6ca8", linewidth=2.2, marker="s", markersize=5,
             label="Crecimiento de M2 (interanual, dic.)")
    # marcar el punto aproximado (2007)
    ap = infl[infl["aprox"] == 1]
    ax1.scatter(ap["anio"], ap["infl_corregida"], s=90, facecolors="none",
                edgecolors="#c0392b", linewidths=1.5, zorder=4)
    ax1.annotate("2007: estimación\n(Cavallo)", xy=(2007, 20), xytext=(-4, -38),
                 textcoords="offset points", fontsize=8, color="#c0392b")
    ax1.annotate("misma emisión (~30%),\ninflación baja:\nremonetización", xy=(2004, 6.1),
                 xytext=(6, 34), textcoords="offset points", fontsize=8.5, color="#555")
    ax1.annotate("misma emisión,\ninflación alta:\ndesmonetización", xy=(2014, 38.5),
                 xytext=(-120, -6), textcoords="offset points", fontsize=8.5, color="#555")
    ax1.set_title("A. Mismo dinero, distinta inflación:\nel desacople delata a la demanda de dinero")
    ax1.set_ylabel("% interanual")
    ax1.set_xlabel("")
    ax1.legend(loc="upper left", fontsize=9)

    # ── Panel B: reservas — compra de dólares (acumulación) vs drenaje ─────────
    ax2.plot(res.index, res / 1000, color="#1e8449", linewidth=2.4)
    pico = res.idxmax()
    ax2.axvspan(pd.Timestamp("2003-01-01"), pico, color="#1e8449", alpha=0.08)
    ax2.axvspan(pico, pd.Timestamp("2015-12-31"), color="#c0392b", alpha=0.08)
    ax2.annotate("ACUMULACIÓN 2003-2011\n(compra de dólares = emisión)\ninflación moderada",
                 xy=(pd.Timestamp("2006-01-01"), 20), fontsize=9, color="#1e6b3a", ha="center")
    ax2.annotate("DRENAJE 2011-2015\n(reservas a pagar deuda,\ncepo) inflación disparada",
                 xy=(pd.Timestamp("2013-06-01"), 40), fontsize=9, color="#a33228", ha="center")
    ax2.annotate(f"pico {res.max()/1000:.0f} mil M USD ({pico.strftime('%b-%Y')})",
                 xy=(pico, res.max()/1000), xytext=(-140, -26), textcoords="offset points",
                 fontsize=8.5, color="#333",
                 arrowprops=dict(arrowstyle="->", color="#333", lw=0.8))
    ax2.set_title("B. La fase de más compra de dólares fue\nla de menos inflación (respaldo creciente)")
    ax2.set_ylabel("Reservas internacionales (miles de M USD)")

    fig.suptitle("Argentina kirchnerista (2003-2015): ¿por qué superávit y emisión cambiaria con inflación?",
                 fontsize=12.5, fontweight="bold")
    fig.text(0.01, 0.005,
             "La objeción monetarista (emisión por compra de dólares -> inflación) no explica que la fase de MÁXIMA compra de dólares (2003-2011) fuera la de MENOR inflación, ni que la MISMA emisión (~30% M2)\n"
             "diera 6% de inflación en 2004 y 38% en 2014. Lo que cambió no fue la cantidad de dinero sino su demanda: alta cuando el respaldo crecía (remonetización + reservas), baja cuando se deterioró (déficit, INDEC,\n"
             "drenaje de reservas). Inflación corregida: empalme INDEC(-06)/Santa Fe/IPC Congreso/CABA (ver data/manual/); M2 y reservas de FRED. La cifra anual es incierta; la tendencia, robusta.",
             fontsize=7.5, style="italic", color="#333")
    fig.subplots_adjust(bottom=0.20, top=0.87, wspace=0.22)

    fpng = os.path.join(outdir, "argentina.png")
    fig.savefig(fpng, bbox_inches="tight", dpi=150)
    plt.close(fig)

    print("Argentina kirchnerista — desacople dinero/precios:")
    for a in [2004, 2007, 2010, 2013, 2014]:
        i = infl[infl.anio == a]["infl_corregida"].iloc[0]
        m = m2_dic.get(a, float("nan"))
        print(f"  {a}: M2 +{m:.0f}%  |  inflación {i:.0f}%")
    print(f"  Reservas: pico {res.max()/1000:.0f} mil M USD ({res.idxmax().strftime('%Y-%m')}); fin 2015: {res.iloc[-1]/1000:.0f} mil M")
    print(f"OK -> {fpng}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=OUTDIR)
    main(p.parse_args().outdir)
