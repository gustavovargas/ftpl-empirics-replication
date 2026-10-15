# -*- coding: utf-8 -*-
"""e05 — Brasil 1994 (Plano Real): la inflación se desploma mientras M1 se multiplica.

Panel A: hiperinflación 1992-1996 (dinero y precios suben juntos — la TC brilla).
Panel B: los 18 meses tras el real (jul-1994): M1 ×5 y la inflación mensual del 47% al ~1,5%.

Nota de unidades: la serie SGS 1824 (M1, saldo fin de periodo) viene en la moneda corriente
de cada época. Se empalma a "miles de reales equivalentes": ÷(1000×2750) hasta jul-1993
(cruzeiros), ÷2750 de ago-1993 a jun-1994 (cruzeiros reais; 2.750 CR$ = 1 R$) y tal cual
desde jul-1994 (reales).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from src.utils import fetch_fred, fetch_bcb, estilo, caja_veredicto, guardar

URV = pd.Timestamp("1994-03-01")     # unidad de cuenta indexada (desindexación)
REAL = pd.Timestamp("1994-07-01")    # entra en circulación el real

MES = {1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun",
       7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"}


def m1_en_reales():
    """SGS 1824 empalmado a miles de reales equivalentes."""
    m1 = fetch_bcb(1824)["sgs_1824"].copy()
    m1.loc[:"1993-07-31"] /= 1000 * 2750
    m1.loc["1993-08-01":"1994-06-30"] /= 2750
    return m1


def main(outdir):
    estilo()
    m1 = m1_en_reales()
    ipc = fetch_fred("BRACPIALLMINMEI")["BRACPIALLMINMEI"]
    ipca_m = fetch_bcb(433)["sgs_433"]  # IPCA, variación mensual %

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 6.0))

    # ── Panel A: 1992-1996, índices ene-1992 = 100, escala log ────────────────
    v = slice("1992-01-01", "1996-12-31")
    p = 100 * ipc.loc[v] / ipc.loc["1992-01-01"]
    m = 100 * m1.loc[v] / m1.loc["1992-01-01"]
    ax1.plot(p.index, p, color="#1e8449", linewidth=2.2, label="IPC (ene. 1992 = 100)")
    ax1.plot(m.index, m, color="#1b6ca8", linewidth=2.0, label="M1 en reales equivalentes (ene. 1992 = 100)")
    ax1.set_yscale("log")
    ax1.axvline(URV, color="#e67e22", linestyle=":", linewidth=1.3)
    ax1.axvline(REAL, color="#c0392b", linestyle="--", linewidth=1.3)
    ax1.annotate("mar-94: URV\n(desindexación)", xy=(URV, 2e4), xytext=(-105, 0),
                 textcoords="offset points", fontsize=9, color="#e67e22")
    ax1.annotate("1-jul-94:\nel real", xy=(REAL, 2e5), xytext=(10, 0),
                 textcoords="offset points", fontsize=9, color="#c0392b")
    ax1.annotate("aquí la TC brilla:\ndinero y precios\nsuben juntos", xy=(pd.Timestamp("1992-10-01"), 3e3),
                 fontsize=9, color="#444444")
    ax1.set_title("A. La hiperinflación brasileña (1992-1996)")
    ax1.set_ylabel("Índice, escala log (ene. 1992 = 100)")
    ax1.legend(loc="lower right", fontsize=9)
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # ── Panel B: remonetización, jun-1994 = 100 ───────────────────────────────
    z = slice("1994-06-01", "1995-12-31")
    mz = 100 * m1.loc[z] / m1.loc["1994-06-01"]
    pz = 100 * ipc.loc[z] / ipc.loc["1994-06-01"]
    ax2.plot(mz.index, mz, color="#1b6ca8", linewidth=2.4, marker="o", markersize=4,
             label="M1 (jun. 1994 = 100)")
    ax2.plot(pz.index, pz, color="#1e8449", linewidth=2.4, marker="o", markersize=4,
             label="IPC (jun. 1994 = 100)")
    ax2.annotate(f"M1 se multiplica por {mz.iloc[-1]/100:.1f}\nen los 18 meses del Plan…",
                 xy=(mz.index[-1], mz.iloc[-1]), xytext=(-200, -40), textcoords="offset points",
                 fontsize=10, color="#1b6ca8", fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="#1b6ca8", lw=1))
    ax2.annotate(f"…los precios suben {pz.iloc[-1]-100:.0f}% en total:\nla inflación pasa de {ipca_m.loc['1994-06-01']:.0f}% AL MES\na {ipca_m.loc['1995-06-01':'1995-12-31'].mean():.1f}% al mes",
                 xy=(pz.index[-1], pz.iloc[-1]), xytext=(-215, 40), textcoords="offset points",
                 fontsize=10, color="#1e8449", fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="#1e8449", lw=1))
    ax2.set_title("B. Tras el real: remonetización masiva, inflación desplomada")
    ax2.set_ylabel("Índice (jun. 1994 = 100)")
    ax2.legend(loc="center right", fontsize=9)
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, _: (lambda d: f"{MES[d.month]}-{d.year % 100:02d}")(mdates.num2date(x))))

    caja_veredicto(fig,
        "TC: para parar una inflación del 47% mensual hay que frenar el dinero; lo observado es lo contrario — M1 se quintuplica mientras la inflación se desploma.\n"
        "FTPL: el real llegó con desindexación (URV), ajuste fiscal (FSE, feb-1994) y nueva ancla: restaurado el respaldo, la demanda de dinero renació y absorbió la remonetización\n"
        "— el mismo patrón que Alemania 1923 (e04). La inflación residual (~1,5%/mes) refleja el ajuste fiscal incompleto de los años noventa.")
    fig.subplots_adjust(bottom=0.22, wspace=0.24)

    df_out = pd.DataFrame({"M1_miles_reales_eq": m1, "IPC_indice": ipc, "IPCA_var_mensual": ipca_m}).loc[v]
    guardar(fig, df_out, outdir, "e05_brasil_1994",
            "Banco Central do Brasil (SGS 1824, 433; empalme de monedas propio) y FRED (BRACPIALLMINMEI)")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
    main(p.parse_args().outdir)
