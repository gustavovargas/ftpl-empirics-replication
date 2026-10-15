# -*- coding: utf-8 -*-
"""e08 — Israel 1985: el plan de estabilización — M1 se multiplica por siete.

Panel A: la gran inflación israelí (1982-1990) y su fin con el plan de julio de 1985.
Panel B: los 30 meses siguientes — remonetización ×7 con la inflación mensual cayendo
del 18% al 1,4%. Patrón Alemania/Brasil, con agregados de la OCDE.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from src.utils import fetch_fred, estilo, caja_veredicto, guardar

PLAN = pd.Timestamp("1985-07-01")  # Plan de Estabilización Económica (gobierno de unidad nacional)

MES = {1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun",
       7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"}


def main(outdir):
    estilo()
    ipc = fetch_fred("ISRCPIALLMINMEI")["ISRCPIALLMINMEI"]
    m1 = fetch_fred("MANMM101ILM189S")["MANMM101ILM189S"]   # M1 Israel (OCDE), desde dic-1982

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 6.0))

    # ── Panel A: 1983-1990, índices ene-1983 = 100, escala log ────────────────
    v = slice("1983-01-01", "1990-12-31")
    p = 100 * ipc.loc[v] / ipc.loc["1983-01-01"]
    m = 100 * m1.loc[v] / m1.loc["1983-01-01"]
    ax1.plot(p.index, p, color="#1e8449", linewidth=2.2, label="IPC (ene. 1983 = 100)")
    ax1.plot(m.index, m, color="#1b6ca8", linewidth=2.0, label="M1 (ene. 1983 = 100)")
    ax1.set_yscale("log")
    ax1.axvline(PLAN, color="#c0392b", linestyle="--", linewidth=1.4)
    ax1.annotate("jul-1985: plan de estabilización\n(ajuste fiscal + ley de no-impresión\n+ ancla cambiaria + pacto de rentas)",
                 xy=(PLAN, 110), xytext=(10, 0), textcoords="offset points", fontsize=9, color="#c0392b")
    ax1.annotate("aquí la TC brilla:\ndinero y precios\nsuben juntos", xy=(pd.Timestamp("1983-04-01"), 3000),
                 fontsize=9, color="#444444")
    ax1.set_title("A. La gran inflación israelí y su final (1983-1990)")
    ax1.set_ylabel("Índice, escala log (ene. 1983 = 100)")
    ax1.legend(loc="center right", fontsize=9)
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # ── Panel B: jun-1985 = 100 → dic-1987 ────────────────────────────────────
    z = slice("1985-01-01", "1987-12-31")
    pz = 100 * ipc.loc[z] / ipc.loc["1985-06-01"]
    mz = 100 * m1.loc[z] / m1.loc["1985-06-01"]
    ax2.plot(mz.index, mz, color="#1b6ca8", linewidth=2.4, marker="o", markersize=3.5,
             label="M1 (jun. 1985 = 100)")
    ax2.plot(pz.index, pz, color="#1e8449", linewidth=2.4, marker="o", markersize=3.5,
             label="IPC (jun. 1985 = 100)")
    ax2.axvline(PLAN, color="#c0392b", linestyle="--", linewidth=1.4)

    infl = ipc.pct_change()
    ax2.annotate(f"M1 se multiplica por {mz.iloc[-1]/100:.1f}\nen los 30 meses del plan…",
                 xy=(mz.index[-1], mz.iloc[-1]), xytext=(pd.Timestamp("1985-11-01"), 620), textcoords="data",
                 fontsize=10, color="#1b6ca8", fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="#1b6ca8", lw=1))
    ax2.annotate(f"…y la inflación cae del {100*infl.loc['1985-06-01']:.0f}% AL MES (jun-85)\nal {100*infl.loc['1986':'1987'].mean():.1f}% mensual en 1986-87 (los precios suben\n{pz.iloc[-1]-100:.0f}% en total, tras el ajuste inicial del propio plan)",
                 xy=(pz.index[-1], pz.iloc[-1]), xytext=(pd.Timestamp("1986-02-01"), 235), textcoords="data",
                 fontsize=10, color="#1e8449", fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="#1e8449", lw=1))
    ax2.set_title("B. Tras el plan: remonetización ×7, inflación desplomada")
    ax2.set_ylabel("Índice (jun. 1985 = 100)")
    ax2.legend(loc="upper left", fontsize=9)
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, _: (lambda d: f"{MES[d.month]}-{d.year % 100:02d}")(mdates.num2date(x))))

    caja_veredicto(fig,
        "TC: parar una inflación del 400% anual exige frenar el dinero; lo observado es M1 ×7 en 30 meses con la inflación en el 1,4% mensual.\n"
        "FTPL: el plan recortó el déficit de ~12% del PIB a ~0, prohibió por ley el crédito del Banco de Israel al gobierno y ancló el shekel (con ayuda de EE.UU.):\n"
        "restaurado el respaldo, la demanda de dinero renació y absorbió la remonetización. Tercera repetición del patrón (Alemania 1923, Brasil 1994).")
    fig.subplots_adjust(bottom=0.22, wspace=0.24)

    df_out = pd.DataFrame({"IPC": ipc, "M1": m1}).loc[v]
    guardar(fig, df_out, outdir, "e08_israel_1985",
            "FRED/OCDE (ISRCPIALLMINMEI, MANMM101ILM189S)")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
    main(p.parse_args().outdir)
