# -*- coding: utf-8 -*-
"""e02 — QE 2008-2019: ¿qué agregado monetario "explica" la inflación?

Base ×5, M1 y M2 duplicadas, Divisia M4 tibio, CPI plano. La TC "acierta" solo si
se elige el agregado correcto ex post: el M se convierte en grado de libertad.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import matplotlib.pyplot as plt
import pandas as pd

from src.utils import RAIZ, fetch_fred, estilo, anotar_evento, caja_veredicto, guardar

DIVISIA_XLSX = os.path.join(RAIZ, "data", "raw", "divisia_cfs.xlsx")

INICIO, FIN, BASE = "2007-01-01", "2019-12-31", "2007-12-01"


def cargar_divisia_m4():
    """Divisia M4 (nivel) de la hoja Broad del CFS; devuelve Serie mensual."""
    df = pd.read_excel(DIVISIA_XLSX, sheet_name="Broad", skiprows=1)
    df = df.iloc[:, [0, 1]]
    df.columns = ["fecha", "DM4"]
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["DM4"] = pd.to_numeric(df["DM4"], errors="coerce")
    return df.dropna().set_index("fecha")["DM4"]


def main(outdir):
    estilo()
    series = {
        "Base monetaria": fetch_fred("BOGMBASE")["BOGMBASE"],
        "M1": fetch_fred("M1SL")["M1SL"],
        "M2": fetch_fred("M2SL")["M2SL"],
        "IPC": fetch_fred("CPIAUCSL")["CPIAUCSL"],
    }
    try:
        series["Divisia M4 (CFS)"] = cargar_divisia_m4()
    except Exception as e:  # si el xlsx no está, el episodio funciona igual
        print(f"AVISO: sin Divisia M4 ({e})")

    colores = {
        "Base monetaria": "#c0392b", "M1": "#e67e22", "M2": "#1b6ca8",
        "Divisia M4 (CFS)": "#6c3483", "IPC": "#1e8449",
    }

    idx = pd.date_range(INICIO, FIN, freq="MS")
    fig, ax = plt.subplots()
    df_out = pd.DataFrame(index=idx)
    for nombre, s in series.items():
        s = s.resample("MS").mean().reindex(idx).ffill()
        s = 100 * s / s.loc[BASE]
        df_out[nombre] = s
        grosor = 2.4 if nombre == "IPC" else 1.7
        ax.plot(s.index, s, color=colores[nombre], linewidth=grosor)
        ax.annotate(f"{nombre}  ×{s.iloc[-1]/100:.2f}", xy=(s.index[-1], s.iloc[-1]),
                    xytext=(8, 0), textcoords="offset points",
                    color=colores[nombre], fontsize=10, va="center", fontweight="bold")

    ax.set_yscale("log")
    ax.set_yticks([100, 150, 200, 300, 400, 500])
    ax.get_yaxis().set_major_formatter(plt.matplotlib.ticker.ScalarFormatter())

    anotar_evento(ax, "2008-09-15", "quiebra de Lehman;\narranca el QE", y_frac=0.97)

    ax.set_title("QE 2008-2019: cinco 'cantidades de dinero', una sola inflación — ¿qué M elijo?")
    ax.set_ylabel("Nivel indexado (dic. 2007 = 100, escala log)")
    ax.set_xlim(pd.Timestamp(INICIO), pd.Timestamp("2022-06-01"))  # aire para las etiquetas

    caja_veredicto(fig,
        "TC: 'el dinero determina los precios' — pero ¿qué dinero? La base acabó 2019 en ×4,1 (pico ×4,9) y el IPC subió un 22% en 12 años.\n"
        "El agregado que 'funciona' (el amplio) se conoce ex post: elegir el M tras ver la inflación no es una predicción, es un ajuste.")
    fig.subplots_adjust(bottom=0.20)

    guardar(fig, df_out, outdir, "e02_agregados_qe",
            "FRED (BOGMBASE, M1SL, M2SL, CPIAUCSL) y Center for Financial Stability (Divisia M4)")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
    main(p.parse_args().outdir)
