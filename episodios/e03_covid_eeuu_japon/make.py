# -*- coding: utf-8 -*-
"""e03 — COVID 2020-2023: la contracción de M2 que no bajó los precios (EE.UU.)
y la inflación que llegó con el dinero ya normalizado (Japón)."""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import matplotlib.pyplot as plt
import pandas as pd

from src.utils import fetch_fred, estilo, anotar_evento, caja_veredicto, guardar

INICIO, FIN = "2015-01-01", "2025-12-31"


def main(outdir):
    estilo()
    m2 = fetch_fred("M2SL")["M2SL"]
    ipc = fetch_fred("CPIAUCSL")["CPIAUCSL"]
    m3jp = fetch_fred("MABMM301JPM189S")["MABMM301JPM189S"]     # M3 Japón (OCDE), hasta nov-2023
    infjp = fetch_fred("FPCPITOTLZGJPN")["FPCPITOTLZGJPN"]      # inflación anual Japón (Banco Mundial)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 6.0))

    # ── Panel A: EE.UU., niveles indexados dic-2019 = 100 ─────────────────────
    base = "2019-12-01"
    m2i = (100 * m2 / m2.loc[base]).loc[INICIO:FIN]
    ipci = (100 * ipc / ipc.loc[base]).loc[INICIO:FIN]
    ax1.plot(m2i.index, m2i, color="#1b6ca8", linewidth=2.0, label="M2 (dic. 2019 = 100)")
    ax1.plot(ipci.index, ipci, color="#1e8449", linewidth=2.4, label="IPC (dic. 2019 = 100)")

    pico = m2i.loc[:"2022-12-31"].idxmax()          # pico local de 2022, no el máximo de la ventana
    valle = m2i.loc[pico:"2024-06-30"].idxmin()     # valle de la contracción 2022-23
    ax1.axvspan(pico, valle, color="#c0392b", alpha=0.10)
    caida = 100 * (m2i.loc[valle] / m2i.loc[pico] - 1)
    subida_ipc = 100 * (ipci.loc[valle] / ipci.loc[pico] - 1)
    ax1.annotate(f"M2 cae {abs(caida):.1f}%\n(mayor contracción desde 1933)…",
                 xy=(pico, m2i.loc[pico]), xytext=(-175, 10), textcoords="offset points",
                 fontsize=9, color="#c0392b",
                 arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1))
    ax1.annotate(f"…y el IPC sube {subida_ipc:.1f}% mientras tanto:\nla 'reversión' de M no revierte los precios",
                 xy=(valle, ipci.loc[valle]), xytext=(-215, -48), textcoords="offset points",
                 fontsize=9, color="#1e8449")
    ax1.annotate("+41% de M2 en dos años\n(déficit federal 2020: 14,7% del PIB)",
                 xy=(pd.Timestamp("2020-09-01"), 128), fontsize=9, color="#1b6ca8", ha="right")
    ax1.set_title("EE.UU.: el nivel de precios no devuelve nada")
    ax1.set_ylabel("Nivel (dic. 2019 = 100)")
    ax1.legend(loc="lower right")

    # ── Panel B: Japón, tasas interanuales ────────────────────────────────────
    m3jp_yoy = (100 * m3jp.pct_change(12)).loc[INICIO:FIN]
    infjp_a = infjp.loc[INICIO:FIN]
    ax2.plot(m3jp_yoy.index, m3jp_yoy, color="#6c3483", linewidth=2.0,
             label="M3 Japón, crecimiento interanual (mensual)")
    ax2.plot(infjp_a.index, infjp_a, color="#1e8449", linewidth=2.2, marker="o",
             label="Inflación media anual (Banco Mundial)")
    ax2.axhline(0, color="#999999", linewidth=0.8)

    ax2.set_ylim(-1, 9.6)
    pico_m3 = m3jp_yoy.idxmax()
    ax2.annotate(f"pico monetario: +{m3jp_yoy.max():.1f}%\n(pandemia; déficit 2020 ≈ 9% del PIB)",
                 xy=(pico_m3, m3jp_yoy.max()), xytext=(14, -26), textcoords="offset points",
                 fontsize=9, color="#6c3483",
                 arrowprops=dict(arrowstyle="->", color="#6c3483", lw=1))
    imax = infjp_a.idxmax()
    ax2.annotate(f"la mayor inflación desde 1991 ({infjp_a.max():.1f}%)\nllega cuando M3 ya crece al ~2%",
                 xy=(imax, infjp_a.max()), xytext=(-150, 26), textcoords="offset points",
                 fontsize=9, color="#1e8449",
                 arrowprops=dict(arrowstyle="->", color="#1e8449", lw=1))
    ax2.set_title("Japón: la inflación llega con el dinero normalizado")
    ax2.set_ylabel("% interanual")
    ax2.legend(loc="upper left", fontsize=9)

    caja_veredicto(fig,
        "TC (M amplia + reversión a la media): la contracción de M2 2022-23 debía traer desinflación rápida o deflación (así lo advirtieron los monetaristas de M amplia); el IPC siguió subiendo y no hubo recesión.\n"
        "En Japón, la mayor inflación desde 1991 llega en 2022-23 con crecimiento monetario ya normal. FTPL: transferencias fiscales financiadas con emisión elevan el nivel de precios de forma permanente;\n"
        "sin deterioro fiscal comparable (Japón), el mismo instrumento monetario no produce la misma inflación.")
    fig.subplots_adjust(bottom=0.22, wspace=0.22)

    df_out = pd.DataFrame({"M2_EEUU_idx": m2i, "IPC_EEUU_idx": ipci,
                           "M3_Japon_yoy": m3jp_yoy, "Inflacion_Japon_anual": infjp_a})
    guardar(fig, df_out, outdir, "e03_covid_eeuu_japon",
            "FRED (M2SL, CPIAUCSL, MABMM301JPM189S, FPCPITOTLZGJPN, FYFSGDA188S); déficit Japón: FMI WEO")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
    main(p.parse_args().outdir)
