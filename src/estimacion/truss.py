# -*- coding: utf-8 -*-
"""Nivel B, test 6b — el 'Poincaré moderno': event study del mini-budget de Truss (2022).

Un anuncio fiscal puro (recorte de impuestos de ~45.000 M£ sin financiar, 23-sep-2022) bajo una
política monetaria que se estaba ENDURECIENDO. Predicción TC: si lo que mueve a la libra es el
dinero, un banco central que sube tipos la fortalece. Observado: la libra se hunde a un mínimo
histórico y los rendimientos de la deuda se disparan en la ventana del anuncio — el mercado
repreció el respaldo fiscal, no la cantidad de dinero. El BoE tuvo que intervenir el 28-sep.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import requests

from src.utils import RAIZ, fetch_fred, estilo

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
MINIBUDGET = pd.Timestamp("2022-09-23")
BOE_INTERV = pd.Timestamp("2022-09-28")
UTURN = pd.Timestamp("2022-10-17")   # Hunt retira el paquete
INI, FIN = "2022-09-01", "2022-10-31"  # cubre la reversión tras el U-turn
PRE = "2022-09-22"                     # último cierre antes del anuncio (base del salto)

BOE_URL = ("https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp"
           "?csv.x=yes&Datefrom={d0}&Dateto={d1}&SeriesCodes={codes}&CSVF=TN&UsingCodes=Y&VPD=Y&VFD=N")


def fetch_boe(codes, d0="01/Sep/2022", d1="01/Nov/2022"):
    """Descarga series diarias del Banco de Inglaterra (IADB) con cache local."""
    cache = os.path.join(RAIZ, "data", "raw", f"boe_{'_'.join(codes.split(','))}.csv")
    if not os.path.exists(cache):
        r = requests.get(BOE_URL.format(d0=d0, d1=d1, codes=codes),
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
        r.raise_for_status()
        with open(cache, "w") as f:
            f.write(r.text)
    df = pd.read_csv(cache)
    df["DATE"] = pd.to_datetime(df["DATE"], format="%d %b %Y")
    return df.set_index("DATE")


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    estilo()
    gbp = fetch_fred("DEXUSUK")["DEXUSUK"].loc[INI:FIN]           # USD por GBP (bajar = libra débil)
    nom = fetch_boe("IUDMNZC")["IUDMNZC"].loc[INI:FIN]            # gilt nominal 10y (zero coupon)
    real = fetch_boe("IUDMRZC")["IUDMRZC"].loc[INI:FIN]          # gilt real 10y (zero coupon)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 6.0), sharex=True)

    # ── Panel A: la libra ─────────────────────────────────────────────────────
    ax1.plot(gbp.index, gbp, color="#c0392b", linewidth=2.2, marker="o", markersize=3.5)
    minfecha = gbp.idxmin()
    ax1.annotate(f"lowest close since 1985: {gbp.min():.3f} $/£\n({minfecha.strftime('%d %b')}; "
                 "intraday 1.035, an all-time low)",
                 xy=(minfecha, gbp.min()), xytext=(10, 10), textcoords="offset points",
                 fontsize=9, color="#c0392b", fontweight="bold")
    ax1.set_title("A. The pound (US dollars per pound)")
    ax1.set_ylabel("USD / GBP  (lower = weaker pound)")

    # ── Panel B: los rendimientos de la deuda ──────────────────────────────────
    ax2.plot(nom.index, nom, color="#1b6ca8", linewidth=2.2, marker="o", markersize=3.5,
             label="10-year nominal gilt")
    ax2.plot(real.index, real, color="#8e44ad", linewidth=2.2, marker="s", markersize=3.5,
             label="10-year real gilt (real cost of debt)")
    salto_real = real.loc["2022-09-23":"2022-09-27"].max() - real.loc[PRE]
    ax2.annotate(f"the real yield jumps +{100*salto_real:.0f} bp\nover three sessions\n(from the 22 Sep close)",
                 xy=(pd.Timestamp("2022-09-27"), real.loc["2022-09-27"]), xytext=(-150, -40),
                 textcoords="offset points", fontsize=9, color="#8e44ad", fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="#8e44ad", lw=1))
    ax2.set_title("B. Government bond yields (gilts)")
    ax2.set_ylabel("% per annum")
    ax2.legend(loc="upper left", fontsize=9)

    for ax in (ax1, ax2):
        ax.axvline(MINIBUDGET, color="#333", linestyle="--", linewidth=1.4)
        ax.axvline(BOE_INTERV, color="#1e8449", linestyle=":", linewidth=1.4)
        ax.axvline(UTURN, color="#8e6f3e", linestyle="-.", linewidth=1.4)
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    ax1.annotate("mini-budget\n(23 Sep)", xy=(MINIBUDGET, ax1.get_ylim()[1]), xytext=(-52, -4),
                 textcoords="offset points", fontsize=8.5, color="#333", va="top")
    ax2.annotate("mini-budget\n(23 Sep)", xy=(MINIBUDGET, ax2.get_ylim()[0]), xytext=(-52, 8),
                 textcoords="offset points", fontsize=8.5, color="#333", va="bottom")
    ax2.annotate("BoE intervenes\n(28 Sep)", xy=(BOE_INTERV, ax2.get_ylim()[0]), xytext=(4, 8),
                 textcoords="offset points", fontsize=8.5, color="#1e8449", va="bottom")
    ax2.annotate("package withdrawn\n(17 Oct)", xy=(UTURN, ax2.get_ylim()[1]), xytext=(4, -4),
                 textcoords="offset points", fontsize=8.5, color="#8e6f3e", va="top")

    fig.suptitle("A fiscal announcement moves the pound and gilts while monetary policy is tightening",
                 fontsize=12.5, fontweight="bold")
    fig.subplots_adjust(top=0.88, wspace=0.22)

    fpng = os.path.join(outdir, "truss_event_study.png")
    fig.savefig(fpng, bbox_inches="tight", dpi=150)
    plt.close(fig)
    pd.DataFrame({"GBP_USD": gbp, "gilt_nominal_10y": nom, "gilt_real_10y": real}).to_csv(
        os.path.join(outdir, "truss_event_study.csv"))

    print("Test 6b — mini-budget de Truss (base: cierre 22-sep, previo al anuncio):")
    print(f"  GBP/USD: {gbp.loc[PRE]:.3f} (22-sep) -> {gbp.min():.3f} (mínimo de cierre, {gbp.idxmin().strftime('%d-%b')})")
    nmax = nom.loc['2022-09-23':'2022-09-27'].max()
    print(f"  Gilt nominal 10y: {nom.loc[PRE]:.2f}% -> {nmax:.2f}% (+{100*(nmax-nom.loc[PRE]):.0f} pb en tres sesiones)")
    print(f"  Gilt real 10y: {real.loc[PRE]:+.2f}% -> {real.loc['2022-09-23':'2022-09-27'].max():+.2f}% (+{100*salto_real:.0f} pb)")
    for d in ("2022-10-14", "2022-10-21", "2022-10-31"):
        if d in nom.index.strftime("%Y-%m-%d").tolist():
            print(f"  {d}: nominal {nom.loc[d]:.2f}%, real {real.loc[d]:+.2f}%, GBP {gbp.get(pd.Timestamp(d), float('nan')):.3f}")
    print(f"OK -> {fpng}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=OUTDIR)
    main(p.parse_args().outdir)
