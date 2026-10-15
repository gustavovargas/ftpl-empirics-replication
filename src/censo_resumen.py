# -*- coding: utf-8 -*-
"""Resumen del censo de estabilizaciones: la tabla de contingencia ancla-fiscal × resultado.

Produce el primer artefacto estadístico del paper: ¿cuántas estabilizaciones triunfan
sin ancla fiscal? ¿Cuántas fracasan con ella?
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import matplotlib.pyplot as plt
import pandas as pd

from src.utils import RAIZ, estilo, guardar

CSV = os.path.join(RAIZ, "data", "censo", "censo_episodios.csv")

ORDEN_RES = ["exito_duradero", "exito_gradual", "exito_en_curso", "exito_temporal", "fracaso"]
ETIQ_RES = {"exito_duradero": "Durable success", "exito_gradual": "Gradual success",
            "exito_en_curso": "Success (ongoing)", "exito_temporal": "Temporary success", "fracaso": "Failure"}
ETIQ_FIS = {2: "Strong fiscal anchor\n(adjustment ≥3pp or legal rule)",
            1: "Partial or transitory\nfiscal component", 0: "No credible\nfiscal component"}
COLORES = {"exito_duradero": "#1e8449", "exito_gradual": "#7cb342", "exito_en_curso": "#4dd0a0",
           "exito_temporal": "#e6a817", "fracaso": "#c0392b"}


def main(outdir):
    estilo()
    df = pd.read_csv(CSV, comment="#")
    df = df[df["tipo"] == "desinflacion"]  # la reflación (e07) se analiza aparte

    tabla = (df.groupby(["comp_fiscal", "resultado"]).size().unstack(fill_value=0)
               .reindex(columns=[c for c in ORDEN_RES if c in df["resultado"].unique()], fill_value=0)
               .sort_index(ascending=False))
    print("\nTabla de contingencia (desinflaciones):\n")
    print(tabla.rename(index=lambda i: ETIQ_FIS[i].replace("\n", " "), columns=ETIQ_RES).to_string())

    fig, ax = plt.subplots(figsize=(11.5, 6.2))
    izq = pd.Series(0.0, index=tabla.index)
    for res in tabla.columns:
        ax.barh([ETIQ_FIS[i] for i in tabla.index], tabla[res], left=izq.values,
                color=COLORES[res], label=ETIQ_RES[res], height=0.62)
        for y, (v, l) in enumerate(zip(tabla[res].values, izq.values)):
            if v > 0:
                ax.text(l + v / 2, y, str(v), ha="center", va="center",
                        color="white", fontweight="bold", fontsize=11)
        izq += tabla[res].values

    ax.set_title(f"A census of stabilisations (n={len(df)} disinflations, 1921-2025):\n"
                 "which component of the package predicts the outcome?")
    ax.set_xlabel("Number of episodes")
    ax.invert_yaxis()
    ax.legend(loc="lower right", fontsize=9)

    fig.subplots_adjust(left=0.22)

    guardar(fig, tabla, outdir, "censo_contingencia",
            "own elaboration from data/censo/censo_episodios.csv", etiqueta_fuente="Source")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=os.path.join(RAIZ, "data", "censo", "out"))
    main(p.parse_args().outdir)
