# -*- coding: utf-8 -*-
"""Presentación descriptiva de los datos usados en el paper (no de los resultados).

Genera docs/index.html: un HTML autocontenido (figuras embebidas en base64) con una
ficha por cada serie de episodio que usan los tests, más los tres datasets modernos
(cross-section COVID, diarios de Truss, velocidad). Se publica con GitHub Pages desde
docs/ en el repo de replicación. Es deliberadamente descriptivo: ventanas, cobertura,
picos y fuentes — las rupturas y los tests viven en src/estimacion/.
"""
import base64
import io
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.utils import RAIZ, estilo, fetch_fred
from src.estimacion.series import CARGADORES, TEMPORALES, PLACEBOS
from src.estimacion.rupturas import crecimiento_mensual
from src.estimacion.velocidad import velocidad_divisia

SALIDA = os.path.join(RAIZ, "docs", "index.html")

# Etiquetas en inglés (mismas convenciones que el apéndice del paper)
DATOS = {"sargent_digitalizado": "Digitised from Sargent (1982)", "digitalizado_e04": "Digitised from Sargent (1982)",
         "nber_e06": "NBER Macrohistory via FRED", "fred_e07": "FRED", "fred_e08": "FRED/OECD",
         "fred_integrado": "FRED/OECD", "bcb_e05": "Central Bank of Brazil (SGS) + FRED",
         "bcb_integrado": "Central Bank of Brazil (SGS)", "bcrp_integrado": "Central Reserve Bank of Peru",
         "ifs_dbnomics_integrado": "IMF IFS via DBnomics", "datosgobar_mendoza_integrado": "DEIE Mendoza (datos.gob.ar)",
         "bcra_datosgobar_integrado": "BCRA + INDEC (datos.gob.ar)", "frb_fraser_digitalizado": "Digitised from the Federal Reserve Bulletin (FRASER)",
         "kobe_shizume_integrado": "Shibamoto and Shizume (2014)", "panoeconomicus_digitalizado": "Digitised from Bogetić et al. (2022)",
         "hanke_ifs_integrado": "Hanke and Kwok (2009) + IMF IFS", "sachs_digitalizado": "Digitised from Sachs (1986)"}
RESULTADO = {"exito": "durable success", "exito_gradual": "gradual success", "exito_temporal": "temporary success",
             "exito_en_curso": "in progress", "fracaso": "failure"}
PLAN = {"Protocolos Sociedad de Naciones": "League of Nations protocols",
        "Reconstrucción SdN": "League reconstruction", "Plan Grabski": "Grabski reform",
        "Rentenbank + reforma fiscal": "Rentenmark + fiscal reform", "Gobierno Poincaré": "Poincaré government",
        "Estabilización Francqui": "Francqui stabilisation", "Reflación de FDR": "FDR reflation",
        "Estabilización Einaudi": "Einaudi squeeze", "DS 21060 (Paz Estenssoro)": "Decree 21060",
        "Plan de Estabilización Económica": "Economic Stabilization Plan", "Plan Austral": "Austral plan",
        "Plan Primavera": "Primavera plan", "Convertibilidad (Cavallo)": "Convertibility",
        "Ajuste Milei": "Milei adjustment", "Plan Cruzado": "Cruzado plan", "Plan Bresser": "Bresser plan",
        "Plan Verão": "Verão plan", "Plan Collor": "Collor plan", "Plano Real": "Real plan",
        "Fujishock": "Fujishock", "Pacto de Solidaridad": "Solidarity Pact", "Ajuste Cauas": "Cauas adjustment",
        "Plan Balcerowicz": "Balcerowicz plan", "Programa Avramović": "Avramović programme",
        "Caja de conversión": "Currency board", "Estabilización Kuchma (+ grivna 1996)": "Kuchma stabilisation",
        "Corredor cambiario": "Exchange-rate corridor", "Programa Derviş": "Derviş programme",
        "Dolarización": "Dollarisation", "Reflación de Takahashi": "Takahashi reflation"}

CSS = """
body { font-family: Georgia, 'Times New Roman', serif; max-width: 980px; margin: 2em auto;
       padding: 0 1.2em; color: #222; line-height: 1.55; }
h1 { font-size: 1.7em; margin-bottom: 0.1em; }
h2 { border-bottom: 2px solid #1e8449; padding-bottom: 0.15em; margin-top: 2.2em; }
h3 { margin-bottom: 0.2em; margin-top: 1.6em; }
.sub { color: #666; font-style: italic; margin-top: 0; }
.meta { font-size: 0.86em; color: #555; margin: 0.2em 0 0.5em 0; }
.meta b { color: #333; }
img { max-width: 100%; border: 1px solid #e3e0d8; }
table { border-collapse: collapse; font-size: 0.86em; margin: 0.8em 0; }
th, td { border: 1px solid #ccc; padding: 3px 9px; text-align: right; }
th { background: #f3f1ea; } td:first-child, th:first-child { text-align: left; }
.nota { background: #f7f5f0; border-left: 4px solid #1e8449; padding: 0.6em 1em; font-size: 0.92em; }
footer { margin-top: 3em; border-top: 1px solid #ccc; padding-top: 0.8em; font-size: 0.85em; color: #666; }
"""


def b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def ficha(cfg, censo):
    """Ficha descriptiva de un episodio: gráfico de tasas mensuales + metadatos."""
    fila = censo.loc[cfg["censo_id"]]
    gp = crecimiento_mensual(cfg["precio"], cfg["rango"])
    gm = crecimiento_mensual(cfg["dinero"], cfg["rango"]) if cfg.get("dinero") is not None else None
    ref = pd.Timestamp(cfg["reforma"])

    fig, ax = plt.subplots(figsize=(9.2, 2.7))
    ax.plot(gp.index, 100 * gp, color="#1e8449", linewidth=1.4, label="Monthly inflation (log-diff, %)")
    if gm is not None:
        ax.plot(gm.index, 100 * gm, color="#1b6ca8", linewidth=1.1, alpha=0.8, label="Monthly money growth (%)")
    ax.axvline(ref, color="#c0392b", linestyle="--", linewidth=1.3)
    ax.axhline(0, color="#999", linewidth=0.6)
    ax.legend(loc="upper right", fontsize=7.5)
    ax.tick_params(labelsize=8)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    pre = 100 * gp[(gp.index >= ref - pd.DateOffset(months=6)) & (gp.index < ref)].median()
    meta = (f"<b>Reform:</b> {ref.strftime('%d %b %Y')} (dashed red) &nbsp;·&nbsp; "
            f"<b>Outcome:</b> {RESULTADO[cfg['resultado']]} &nbsp;·&nbsp; "
            f"<b>Price series:</b> {gp.index.min().strftime('%b %Y')}–{gp.index.max().strftime('%b %Y')}, "
            f"n = {len(gp)} monthly rates"
            + (f" &nbsp;·&nbsp; <b>Money series:</b> n = {len(gm)}" if gm is not None else "")
            + f"<br><b>Peak monthly inflation in window:</b> {100 * gp.max():,.1f}% &nbsp;·&nbsp; "
            f"<b>Median in the six months before the reform:</b> {pre:,.1f}%/m &nbsp;·&nbsp; "
            f"<b>Source:</b> {DATOS[fila.datos_mensuales]}")
    return (f"<h3>{cfg['label'].split('· ')[1]} — {PLAN.get(fila.plan, fila.plan)}</h3>"
            f"<p class='meta'>{meta}</p>"
            f"<img alt='{cfg['label']}' src='data:image/png;base64,{b64(fig)}'>")


def bloque_covid():
    d = pd.read_csv(os.path.join(RAIZ, "data", "censo", "covid_cross.csv"), comment="#")
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for euro, color, marca, lab in [(1, "#1e8449", "o", "Euro area (n = 7)"), (0, "#1b6ca8", "s", "Own currency (n = 12)")]:
        e = d[d.euro == euro]
        x = e.fiscal_covid / ((e.deuda_pib_2019 / 100) * e.duracion_2019)
        ax.scatter(x, e.infl_acum_20_23, s=46, color=color, marker=marca, label=lab)
        for _, r in e.iterrows():
            ax.annotate(r.pais, (r.fiscal_covid / ((r.deuda_pib_2019 / 100) * r.duracion_2019),
                                 r.infl_acum_20_23), fontsize=6.5, xytext=(3, 2), textcoords="offset points")
    ax.set_xlabel("COVID fiscal impulse / (debt-to-GDP × average maturity)", fontsize=9)
    ax.set_ylabel("Cumulative inflation 2020–23 (%)", fontsize=9)
    ax.legend(fontsize=8)
    ax.tick_params(labelsize=8)

    filas = "".join(
        f"<tr><td>{r.pais}</td><td>{'yes' if r.euro == 1 else 'no'}</td><td>{r.infl_acum_20_23:.1f}</td>"
        f"<td>{r.fiscal_covid:.1f}</td><td>{r.deuda_pib_2019:.0f}</td><td>{r.duracion_2019:.1f}</td></tr>"
        for _, r in d.sort_values(["euro", "pais"], ascending=[False, True]).iterrows())
    return f"""
<h2>The COVID cross-section (19 countries)</h2>
<p>One row per country: cumulative inflation 2020–23 (Eurostat/OECD/World Bank), the raw COVID
fiscal impulse (IMF Fiscal Monitor, October 2021 vintage) and the 2019 debt stock and average
maturity used for the Barro–Bianchi scaling (national debt offices and the ECB). The scatter shows
the data as used; estimates are in the paper, not here.</p>
<img alt='COVID cross-section' src='data:image/png;base64,{b64(fig)}'>
<table><tr><th>Country</th><th>Euro</th><th>Infl. 20–23 (%)</th><th>Fiscal (% GDP)</th>
<th>Debt/GDP 2019</th><th>Maturity (y)</th></tr>{filas}</table>"""


def bloque_truss():
    t = pd.read_csv(os.path.join(RAIZ, "src", "estimacion", "out", "truss_event_study.csv"),
                    index_col=0, parse_dates=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.1))
    ax1.plot(t.index, t.GBP_USD, color="#c0392b", linewidth=1.5)
    ax1.set_title("GBP/USD (daily close)", fontsize=9.5)
    ax2.plot(t.index, t.gilt_nominal_10y, color="#1b6ca8", linewidth=1.5, label="10y nominal gilt")
    ax2.plot(t.index, t.gilt_real_10y, color="#8e44ad", linewidth=1.5, label="10y real gilt")
    ax2.set_title("Zero-coupon gilt yields (%)", fontsize=9.5)
    ax2.legend(fontsize=7.5)
    for ax in (ax1, ax2):
        for fecha in ("2022-09-23", "2022-09-28", "2022-10-17"):
            ax.axvline(pd.Timestamp(fecha), color="#777", linestyle=":", linewidth=0.9)
        ax.tick_params(labelsize=7.5)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    return f"""
<h2>The 2022 UK episode (daily data)</h2>
<p>1 September to 31 October 2022: the pound (FRED DEXUSUK) and the ten-year nominal and real
zero-coupon gilt yields (Bank of England IADB, IUDMNZC and IUDMRZC); n = {len(t)} trading days.
Dotted lines: the mini-budget (23 September), the Bank's intervention (28 September) and the
U-turn (17 October).</p>
<img alt='UK 2022 daily data' src='data:image/png;base64,{b64(fig)}'>"""


def bloque_velocidad():
    m2v = fetch_fred("M2V")["M2V"].dropna().loc[:"2025-12-31"]
    dm4v = velocidad_divisia().loc[:"2025-12-31"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.1))
    ax1.plot(m2v.index, m2v, color="#1b6ca8", linewidth=1.3)
    ax1.set_title(f"M2 velocity, quarterly (n = {len(m2v)})", fontsize=9.5)
    ax2.plot(dm4v.index, dm4v, color="#8e44ad", linewidth=1.3)
    ax2.set_title(f"Divisia M4 velocity, quarterly (n = {len(dm4v)})", fontsize=9.5)
    for ax in (ax1, ax2):
        ax.tick_params(labelsize=7.5)
    return f"""
<h2>US velocity series (1959–2025)</h2>
<p>M2 velocity (FRED M2V) and the velocity of Divisia M4 — nominal GDP over the Center for
Financial Stability's Divisia M4 — as plain levels. The paper's section 7 runs the stationarity
battery on exactly these two series.</p>
<img alt='Velocity series' src='data:image/png;base64,{b64(fig)}'>"""


def main():
    estilo()
    censo = pd.read_csv(os.path.join(RAIZ, "data", "censo", "censo_episodios.csv"),
                        comment="#").set_index("id")
    grupos = [
        ("The Table 1 sample: fifteen stabilisations with a fiscal anchor", CARGADORES,
         "The episodes behind the paper's main timing test: monthly price indices (and the broadest "
         "monthly money aggregate where one exists) around each fiscal reform."),
        ("Intermediate episodes: gradual, temporary, monetary-led and in progress", TEMPORALES,
         "The eleven episodes between durable success and failure, treated separately in the paper "
         "(appendix C): same series construction, same descriptive view."),
        ("The failed plans", PLACEBOS,
         "The five failures with monthly data — three plans with no credible fiscal component plus "
         "Bresser and Collor. They enter the durability comparison as the control group."),
    ]
    con_datos = sum(len(c) for _, c, _ in grupos)
    fichas, n_series = [], 0
    for titulo, cargadores, intro in grupos:
        fichas.append(f"<h2>{titulo}</h2><p>{intro}</p>")
        for cargar in cargadores:
            cfg = cargar()
            fichas.append(ficha(cfg, censo))
            n_series += 1 + (cfg.get("dinero") is not None)
    hoy = pd.Timestamp.today().strftime("%d %B %Y")

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The data — Whose Dates Do Prices Obey?</title><style>{CSS}</style></head><body>
<h1>The data behind the paper</h1>
<p class="sub">A descriptive tour of every series used in “Whose Dates Do Prices Obey? Fiscal
Regime Change and the Anchoring of Inflation” (Gustavo Vargas, 2026)</p>
<div class="nota">This page presents the <b>data</b>, not the results: what each series is, where
it comes from, what window the paper uses and what the raw monthly rates look like, with the
reform date marked. Every chart regenerates from the sources in this repository with
<code>python src/datos_descriptivos.py</code>; the break tests and estimates live in
<code>src/estimacion/</code> and in the paper's appendix.</div>
<p>The census counts <b>34 stabilisations</b> (1921–2025), of which <b>{con_datos} have usable
monthly data</b> — {n_series} monthly series in all, plus three daily series for the 2022 UK
episode, a 19-country cross-section for the COVID inflation and two quarterly US velocity series.
Hand-digitised series carry their source, page numbers, splices and known printing errata in the
file headers under <code>data/manual/</code>; the rest load from public APIs without keys (FRED,
IMF, and the central banks of Brazil, Peru and Argentina), cached under <code>data/raw/</code>.</p>
{''.join(fichas)}
{bloque_covid()}
{bloque_truss()}
{bloque_velocidad()}
<footer>Generated on {hoy} by <code>src/datos_descriptivos.py</code> ·
<a href="https://github.com/gustavovargas/ftpl-empirics-replication">Replication repository</a> ·
MIT licence.</footer>
</body></html>"""
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w") as f:
        f.write(html)
    print(f"OK -> {SALIDA} ({os.path.getsize(SALIDA) / 1e6:.1f} MB, {con_datos} fichas)")


if __name__ == "__main__":
    main()
