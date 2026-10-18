# -*- coding: utf-8 -*-
"""Presentación descriptiva de los datos usados en el paper (no de los resultados).

Genera docs/index.html: un HTML autocontenido (figuras embebidas en base64) con una
ficha por cada serie de episodio que usan los tests, más los tres datasets modernos
(cross-section COVID, diarios de Truss, velocidad). Se publica con GitHub Pages desde
docs/ en el repo de replicación. Es deliberadamente descriptivo: ventanas, cobertura,
picos y fuentes — las rupturas y los tests viven en src/estimacion/.

Convenciones (revisadas tras la auditoría externa de oct-2026):
- Los gráficos trazan 100·Δln (log-puntos); los resúmenes de las fichas se dan en
  porcentaje convencional, 100·(exp(Δln)−1), y la introducción da la fórmula puente.
- La mediana pre-reforma usa los seis meses de calendario ANTERIORES al mes de la
  reforma (periodos mensuales, nunca comparación por días).
- Las líneas se cortan en los meses sin dato (reindexado a calendario mensual).
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
         "ifs_dbnomics_integrado": "IMF IFS via DBnomics", "datosgobar_mendoza_integrado": "CPI of Mendoza province (DEIE, via datos.gob.ar)",
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
PAIS_EN = {"Estados Unidos": "United States", "Reino Unido": "United Kingdom", "Japon": "Japan",
           "Canada": "Canada", "Australia": "Australia", "Corea del Sur": "South Korea",
           "Noruega": "Norway", "Suecia": "Sweden", "Suiza": "Switzerland", "Polonia": "Poland",
           "Dinamarca": "Denmark", "Nueva Zelanda": "New Zealand", "Alemania": "Germany",
           "Francia": "France", "Italia": "Italy", "Espana": "Spain", "Paises Bajos": "Netherlands",
           "Belgica": "Belgium", "Portugal": "Portugal"}

# Contexto histórico por episodio (censo_id) — fechas y magnitudes verificadas contra
# las cabeceras de data/manual/, las notas del censo y la auditoría externa de oct-2026
HISTORIA = {
    1: "Austria left the First World War with a collapsing crown and a budget financed by the printing press. "
       "The crown actually steadied in late August 1922, on the news that the League of Nations would take the "
       "reconstruction in hand; the Geneva Protocols of October formalised the package — a guaranteed foreign "
       "loan, a commissioner with authority over the budget, and a central bank barred from lending to the "
       "government, operating from January 1923. Prices peaked in September — while the note circulation went "
       "on rising for two more years.",
    5: "The classic hyperinflation: the occupation of the Ruhr in 1923 was met with 'passive resistance' paid for "
       "by the printing press, and by November prices were doubling in days. Passive resistance had ended on "
       "26 September; the Rentenmark of 15 November 1923 arrived together with the fiscal reform — budget cuts "
       "and a cap on the Reichsbank's credit to the government. Stabilisation came within weeks.",
    3: "Hungary's post-war inflation accelerated through 1923. The League of Nations reconstruction of March 1924 "
       "repeated the Austrian template — foreign loan, budget control, a new National Bank (opened in June) "
       "forbidden to finance the Treasury — and monthly inflation slowed sharply that spring.",
    7: "Belgium's franc slid after a failed stabilisation attempt in 1925-26 left the Treasury unable to roll its "
       "short-term debt. From July 1926 the Jaspar government — with Francqui directing the stabilisation — used "
       "emergency powers to raise taxes earmarked for debt service and consolidate the short-term debt; the legal "
       "stabilisation and the return to gold came on 25 October 1926.",
    6: "France's franc fell through the first half of 1926 as cabinets failed to close the deficit. Poincaré's "
       "return in July 1926, with new taxes and a fund dedicated to retiring debt, turned the franc around within "
       "days; wholesale prices broke in the months that followed, and the de jure gold parity came in 1928.",
    34: "A reflation: Japan entered 1931 in deflation under the gold standard. Takahashi Korekiyo, finance minister "
        "from December 1931, took the yen off gold and ran deficits for recovery, with the Bank of Japan "
        "underwriting government bonds directly from November 1932. Prices turned up and the deflation ended.",
    9: "The other reflation: over March-April 1933 Roosevelt took the United States off gold and announced "
       "deficits with the declared purpose of raising the price level (the card dates the episode to April). "
       "Prices turned upward with the announcements while broad money was still depressed from the banking crisis.",
    12: "Israel's inflation passed 400 per cent a year by 1984-85 under full indexation. The Economic Stabilization "
        "Plan of July 1985 combined a large budget cut, a fixed shekel-dollar exchange rate after a step "
        "devaluation, wage-price pacts and, soon after, a law forbidding the central bank to finance the "
        "government. Within a year inflation was running at an annual rate of about 20 per cent.",
    11: "Bolivia's hyperinflation peaked in mid-1985 after years of monetised deficits. Decree 21060 of 29 August "
        "1985 (Paz Estenssoro) closed the deficit — hydrocarbon prices became fiscal revenue, public wages were "
        "frozen, spending was rationed to cash — and unified the exchange rate, with no price freeze and no new "
        "currency. Sachs dates the halt in price rises to 9 September, within days of the decree.",
    23: "Mexico's inflation reached about 160 per cent a year after the 1987 crash and devaluation. The Solidarity "
        "Pact of December 1987 paired fiscal adjustment with an exchange-rate anchor and economy-wide price-wage "
        "agreements; inflation fell through 1988-89 and stayed low until the 1994-95 crisis.",
    25: "Poland left communism in late 1989 amid a hyperinflationary burst after food prices were freed. The "
        "Balcerowicz plan of 1 January 1990 — fiscal discipline, an anchored złoty, hard limits on enterprise "
        "credit — itself spiked measured prices in January as administered prices were freed (79 per cent in the "
        "month); monthly inflation then fell to 4 per cent by March, though single digits annually took most of "
        "the decade.",
    22: "Peru's hyperinflation under García accelerated through 1988-90. The 'Fujishock' of 8 August 1990 "
        "corrected public prices overnight — 84-octane petrol rose about thirty-fold — pushing the August figure "
        "to its measured peak near 400 per cent; central-bank financing ended, and inflation collapsed in the "
        "following months.",
    21: "Brazil's fifth plan in this census's sequence arrived with an executed fiscal leg its predecessors "
        "lacked: an emergency fiscal fund alongside the URV (a transitional unit of account), with the real "
        "introduced on 1 July 1994. Monthly inflation fell from around 45 per cent to low single digits, durably.",
    27: "Bulgaria's banking collapse and monetised deficits produced hyperinflation that peaked in February 1997. "
        "Inflation collapsed in the spring, as the caretaker government and the IMF agreed the currency board "
        "that entered into force on 1 July 1997: the lev pegged to the Deutsche Mark and central-bank credit to "
        "the government outlawed.",
    30: "Turkey's crawling peg collapsed in the February 2001 crisis and the lira floated, the depreciation "
        "passing through to prices for the rest of the year. The Derviş programme announced on 14 April 2001 — a "
        "large primary-surplus target (the budget balance before interest payments), bank restructuring and legal "
        "central-bank independence, IMF-backed — brought inflation down decisively from early 2002.",
    4: "Poland's first stabilisation: the Grabski programme of January 1924 closed the deficit with a property "
       "tax and no foreign loan; the Bank Polski opened and the złoty entered circulation in April. The "
       "hyperinflation stopped — but the budget slipped in 1925, the złoty fell, and a 'second inflation' forced "
       "a new stabilisation in 1926-27.",
    10: "Italy's post-war inflation was broken by a monetary act: Einaudi's credit squeeze of August-September "
        "1947 (higher reserve requirements, credit restriction), with the fiscal consolidation and Marshall aid "
        "arriving in its wake. The census codes it as a monetary-led stabilisation.",
    24: "Chile's inflation ran in the hundreds of per cent after 1973. The Cauas adjustment of April 1975 "
        "intensified a fiscal correction already under way; inflation declined over years rather than months — a "
        "gradual disinflation, with contract indexation the standard explanation for its slowness.",
    13: "Argentina's Austral plan of 14 June 1985 froze prices and wages, created the austral and promised an end "
        "to money-financed deficits. Inflation stayed low for about eighteen months; as the fiscal promise eroded "
        "through 1987-88 it returned, and the economy slid into the 1989 hyperinflation.",
    32: "Ecuador announced dollarisation on 9 January 2000, in the middle of a banking crisis and a collapsing "
        "sucre, and implemented it over the year — a complete renunciation of the printing press, with only a "
        "weak fiscal component. Inflation fell slowly, reaching single digits (year on year) only in 2002.",
    31: "Zimbabwe's hyperinflation — among the worst ever measured — ended when the Zimbabwe dollar ceased to "
        "trade in late 2008. The multicurrency regime authorised over January-February 2009 and the cash budget "
        "adopted from March ('we eat what we kill', in finance minister Biti's phrase) formalised a stop the "
        "market had already made; prices then stayed stable for a decade, until a local currency returned in 2019.",
    15: "Convertibility, April 1991: Cavallo fixed the exchange rate by law — 10,000 australes per US dollar, "
        "with the peso replacing the austral at one-to-one with the dollar in January 1992 — and turned the "
        "central bank into a near currency board. Annual inflation reached single digits by 1993 and hovered "
        "near zero for the rest of the decade, until the regime collapsed into default and devaluation in 2001-02.",
    26: "Yugoslavia's 1993-94 hyperinflation peaked at an official 313 million per cent a month. The Avramović "
        "programme of 24 January 1994 introduced a new dinar pegged to the Deutsche Mark with a promise of no "
        "monetary financing; prices stopped within a week (February's monthly average still shows carry-over), "
        "and the stabilisation eroded from late 1995 as the fiscal side gave way — after this card's window, "
        "which ends in December 1994.",
    28: "Ukraine's post-Soviet inflation peaked in 1993. Kuchma's IMF-backed package of October 1994 liberalised "
        "prices (spiking the measured rate that autumn), unified the exchange rate and began a gradual — and "
        "incomplete — fiscal adjustment; inflation fell from about 400 per cent in 1994 to 10 per cent by 1997 "
        "(December on December), before the 1998 Russian crisis forced a relapse, beyond this card's window.",
    29: "Russia's stabilisation of July 1995 anchored the rouble in an exchange-rate corridor and moved deficit "
        "financing from the printing press to the bond market. Inflation fell steadily until the sovereign "
        "default and devaluation of August 1998 undid it; the window here ends just before.",
    16: "The census's live entry: Milei's adjustment of 12 December 2023 devalued the peso and anchored itself to "
        "an explicit zero-deficit rule — in 2024 the national public sector posted its first full-year overall "
        "(cash) surplus since 2010. Monthly inflation fell from 25 per cent in the month of the announcement to "
        "about 2 per cent by late 2025.",
    17: "The Cruzado plan of February 1986 froze prices and wages and created the cruzado, with no fiscal "
        "adjustment behind it. End-of-month M1 rose about 64 per cent in March 1986 alone (≈49 in the chart's "
        "log units) while measured inflation sat near zero under the freeze; the freeze crumbled and inflation "
        "returned within the year.",
    18: "The Bresser plan of June 1987 repeated the freeze with an announced fiscal adjustment that was not "
        "delivered. By mid-1988 monthly inflation was back above 20 per cent, around its pre-plan rate.",
    14: "Argentina's Primavera plan of August 1988 combined price agreements and a managed crawl (a pre-announced "
        "slow devaluation), again without a fiscal leg. The exchange-rate arrangement collapsed in February 1989, "
        "and inflation surged into hyperinflation over May-July 1989.",
    19: "The Verão plan of January 1989 created the cruzado novo and froze prices once more; its announced fiscal "
        "measures were abandoned. Inflation accelerated again through 1989, reaching hyperinflation in early 1990, "
        "beyond this card's window.",
    20: "The Collor plan of March 1990 sequestered most of the financial system's liquid assets — yet narrow "
        "money, converted at the frozen rate, actually rose (about 124 per cent in March); the plotted M1 does "
        "not measure the frozen broad assets. Inflation was back around 20 per cent a month by early 1991.",
}

CSS = """
body { font-family: Georgia, 'Times New Roman', serif; max-width: 980px; margin: 2em auto;
       padding: 0 1.2em; color: #222; line-height: 1.55; }
h1 { font-size: 1.7em; margin-bottom: 0.1em; }
h2 { border-bottom: 2px solid #1e8449; padding-bottom: 0.15em; margin-top: 2.2em; }
h3 { margin-bottom: 0.2em; margin-top: 1.6em; }
.sub { color: #666; font-style: italic; margin-top: 0; }
.historia { font-size: 0.95em; margin: 0.3em 0 0.4em 0; }
.meta { font-size: 0.86em; color: #555; margin: 0.2em 0 0.5em 0; }
.meta b { color: #333; }
img { max-width: 100%; border: 1px solid #e3e0d8; }
.tabla { overflow-x: auto; }
table { border-collapse: collapse; font-size: 0.86em; margin: 0.8em 0; }
th, td { border: 1px solid #ccc; padding: 3px 9px; text-align: right; }
th { background: #f3f1ea; } td:first-child, th:first-child { text-align: left; }
.nota { background: #f7f5f0; border-left: 4px solid #1e8449; padding: 0.6em 1em; font-size: 0.92em; }
.toc { font-size: 0.88em; columns: 3; column-gap: 2em; margin: 0.6em 0 0 0; }
.toc a { text-decoration: none; }
@media (max-width: 640px) { .toc { columns: 2; } }
footer { margin-top: 3em; border-top: 1px solid #ccc; padding-top: 0.8em; font-size: 0.85em; color: #666; }
"""


def b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def _mes_inicio(g):
    """Normaliza el índice al primer día del mes y reindexa al calendario mensual completo,
    de modo que los meses faltantes queden como NaN y la línea se corte en los huecos."""
    s = g.copy()
    s.index = s.index.to_period("M").to_timestamp()
    return s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="MS"))


def _conv(logdiff):
    """De log-diferencia a porcentaje convencional."""
    return 100 * (np.exp(logdiff) - 1)


def ficha(cfg, censo):
    """Ficha descriptiva de un episodio: contexto, gráfico de tasas mensuales y metadatos."""
    fila = censo.loc[cfg["censo_id"]]
    gp = crecimiento_mensual(cfg["precio"], cfg["rango"])
    gm = crecimiento_mensual(cfg["dinero"], cfg["rango"]) if cfg.get("dinero") is not None else None
    gc = crecimiento_mensual(cfg["cambio"], cfg["rango"]) if cfg.get("cambio") is not None else None
    ref = pd.Timestamp(cfg["reforma"])

    fig, ax = plt.subplots(figsize=(9.2, 2.7))
    pp = _mes_inicio(gp)
    ax.plot(pp.index, 100 * pp, color="#1e8449", linewidth=1.4, label="Prices (monthly log change ×100)")
    if gm is not None:
        mm = _mes_inicio(gm)
        ax.plot(mm.index, 100 * mm, color="#1b6ca8", linewidth=1.2, linestyle="--", alpha=0.9,
                label="Money (monthly log change ×100)")
    if gc is not None:
        cc = _mes_inicio(gc)
        ax.plot(cc.index, 100 * cc, color="#999", linewidth=1.0, linestyle=":",
                label="Exchange rate (monthly log change ×100)")
    ax.axvline(ref, color="#c0392b", linestyle="--", linewidth=1.3)
    ax.axhline(0, color="#999", linewidth=0.6)
    ax.legend(loc="upper right", fontsize=8)
    ax.tick_params(labelsize=8.5)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # Mediana de los seis meses de calendario ANTERIORES al mes de la reforma
    om = gp.index.to_period("M").astype("int64") - ref.to_period("M").ordinal
    pre_log = gp[(om >= -6) & (om <= -1)]
    huecos = int(pp.isna().sum())
    cobertura = f"{gp.index.min().strftime('%b %Y')}–{gp.index.max().strftime('%b %Y')}"
    meta = (f"<b>Dated policy event:</b> {ref.strftime('%d %b %Y')} (dashed red) &nbsp;·&nbsp; "
            f"<b>Census outcome:</b> {RESULTADO[cfg['resultado']]}<br>"
            f"<b>Analysis window:</b> {pd.Timestamp(cfg['rango'][0]).strftime('%b %Y')}–"
            f"{pd.Timestamp(cfg['rango'][1]).strftime('%b %Y')} &nbsp;·&nbsp; "
            f"<b>Price series:</b> {cobertura}, n = {len(gp)} monthly rates"
            + (f" ({huecos} months missing inside the range; the line breaks there)" if huecos else "")
            + (f" &nbsp;·&nbsp; <b>Money series:</b> n = {len(gm)}" if gm is not None
               else " &nbsp;·&nbsp; <b>Money series:</b> none usable for this window")
            + (f" &nbsp;·&nbsp; <b>Exchange-rate series:</b> n = {len(gc)}" if gc is not None else "")
            + f"<br><b>Peak monthly inflation in this window:</b> {_conv(gp.max()):,.1f}% (conventional) "
            + (f"&nbsp;·&nbsp; <b>Median of the six months before the reform month:</b> "
               f"{_conv(pre_log.median()):,.1f}%/m (n = {len(pre_log)}) " if len(pre_log) else "")
            + f"&nbsp;·&nbsp; <b>Source:</b> {DATOS[fila.datos_mensuales]}")
    cov_alt = f"{cfg['label'].split('· ')[1]}: monthly log changes in prices and money, {cobertura}"
    return (f"<h3 id='ep-{cfg['censo_id']}'>{cfg['label'].split('· ')[1]} — {PLAN.get(fila.plan, fila.plan)}</h3>"
            f"<p class='historia'>{HISTORIA.get(cfg['censo_id'], '')}</p>"
            f"<p class='meta'>{meta}</p>"
            f"<img alt='{cov_alt}' src='data:image/png;base64,{b64(fig)}'>")


def bloque_covid():
    d = pd.read_csv(os.path.join(RAIZ, "data", "censo", "covid_cross.csv"), comment="#")
    d["pais_en"] = d.pais.map(PAIS_EN).fillna(d.pais)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for euro, color, marca, lab in [(1, "#1e8449", "o", "Euro area (n = 7)"), (0, "#1b6ca8", "s", "Own currency (n = 12)")]:
        e = d[d.euro == euro]
        x = e.fiscal_covid / ((e.deuda_pib_2019 / 100) * e.duracion_2019)
        ax.scatter(x, e.infl_acum_20_23, s=46, color=color, marker=marca, label=lab)
        for _, r in e.iterrows():
            ax.annotate(r.pais_en, (r.fiscal_covid / ((r.deuda_pib_2019 / 100) * r.duracion_2019),
                                    r.infl_acum_20_23), fontsize=6.5, xytext=(3, 2), textcoords="offset points")
    ax.set_xlabel("fiscal_impulse / [(debt-to-GDP ÷ 100) × maturity]  (scaled indicator)", fontsize=9)
    ax.set_ylabel("Cumulative inflation 2020–23 (%)", fontsize=9)
    ax.legend(fontsize=8)
    ax.tick_params(labelsize=8)

    filas = "".join(
        f"<tr><td>{r.pais_en}</td><td>{'yes' if r.euro == 1 else 'no'}</td><td>{r.infl_acum_20_23:.1f}</td>"
        f"<td>{r.fiscal_covid:.1f}</td><td>{r.deuda_pib_2019:.0f}</td><td>{r.duracion_2019:.1f}</td></tr>"
        for _, r in d.sort_values(["euro", "pais_en"], ascending=[False, True]).iterrows())
    return f"""
<h2 id="covid">The COVID cross-section (19 countries)</h2>
<p>One row per country. Cumulative inflation is consumer-price inflation compounded over 2020–23
(Eurostat/OECD/World Bank). The fiscal impulse is the IMF Fiscal Monitor's above-the-line COVID
measure — additional spending plus forgone revenue, per cent of GDP, October 2021 vintage. Debt
and average maturity are end-2019 values (national debt offices, the ECB and IMF WEO); the
scatter's horizontal axis divides the impulse by debt-to-GDP (as a fraction) times maturity in
years, a scaled indicator rather than a forecast. Maturity definitions are not perfectly
homogeneous across countries. The scatter shows the data as used; estimates are in the paper, not
here.</p>
<img alt='COVID cross-section: scaled fiscal impulse against cumulative inflation 2020-23, 19 countries' src='data:image/png;base64,{b64(fig)}'>
<div class="tabla"><table><tr><th>Country</th><th>Euro</th><th>Infl. 20–23 (%)</th><th>Fiscal (% GDP)</th>
<th>Debt/GDP 2019 (%)</th><th>Maturity (years)</th></tr>{filas}</table></div>"""


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
    n = {c: int(t[c].notna().sum()) for c in t.columns}
    return f"""
<h2 id="uk2022">The 2022 UK episode (daily data)</h2>
<p>1 September to 31 October 2022: the pound against the dollar (FRED DEXUSUK) and the ten-year
nominal and real zero-coupon yields on gilts — UK government bonds — from the Bank of England's
database (IUDMNZC and IUDMRZC; the real yield is derived from index-linked gilts, not from
realised inflation). The file holds {len(t)} dated rows across both calendars: GBP/USD
n = {n['GBP_USD']}, nominal gilt n = {n['gilt_nominal_10y']}, real gilt n = {n['gilt_real_10y']}.
Dotted lines: the 'mini-budget' of unfunded tax cuts (23 September), the Bank of England's
temporary gilt purchases (28 September) and the withdrawal of the package (17 October).</p>
<img alt='UK 2022: pound and ten-year gilt yields, daily, September-October 2022' src='data:image/png;base64,{b64(fig)}'>"""


def bloque_velocidad():
    m2v = fetch_fred("M2V")["M2V"].dropna().loc[:"2025-12-31"]
    dm4v = velocidad_divisia().loc[:"2025-12-31"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.1))
    ax1.plot(m2v.index, m2v, color="#1b6ca8", linewidth=1.3)
    ax1.set_title(f"M2 velocity (n = {len(m2v)})", fontsize=9.5)
    ax2.plot(dm4v.index, dm4v, color="#8e44ad", linewidth=1.3)
    ax2.set_title(f"GDP / Divisia M4 index (n = {len(dm4v)}; arbitrary scale)", fontsize=9.5)
    for ax in (ax1, ax2):
        ax.tick_params(labelsize=7.5)
    rango = lambda s: f"{s.index.min().year}Q{s.index.min().quarter}–{s.index.max().year}Q{s.index.max().quarter}"
    return f"""
<h2 id="velocidad">US velocity series</h2>
<p>Velocity is nominal GDP divided by a money measure. Left: M2 velocity from FRED (M2V),
{rango(m2v)}, n = {len(m2v)} quarters. Right: nominal GDP divided by the Center for Financial
Stability's Divisia M4 — a broad aggregate that weights assets by their monetary services — which
is an <em>index</em> (January 1967 = 100), so the level of this ratio has an arbitrary scale and
only its movements are informative; {rango(dm4v)}, n = {len(dm4v)}. The paper's section 7 runs the
stationarity battery on exactly these two series.</p>
<img alt='US velocity: M2 velocity and GDP over Divisia M4 index, quarterly' src='data:image/png;base64,{b64(fig)}'>"""


def main():
    estilo()
    censo = pd.read_csv(os.path.join(RAIZ, "data", "censo", "censo_episodios.csv"),
                        comment="#").set_index("id")
    grupos = [
        ("tabla1", "The Table 1 sample: fifteen stabilisations with a fiscal anchor", CARGADORES,
         "The episodes behind the paper's main timing test (its Table 1): monthly price indices, and a "
         "monthly money series where a usable one exists — banknotes in circulation for the 1920s, the "
         "monetary base, M1, M2 or M3 later; each card names its source. 'Fiscal anchor' follows the "
         "census coding protocol (appendix A of the paper, reproduced in this repository): an executed "
         "or statutory fiscal component, coded from acts of policy, never from the inflation outcome."),
        ("intermedios", "Intermediate episodes, treated separately in the paper", TEMPORALES,
         "Eleven further episodes: six temporary successes, three durable successes outside the main "
         "sample (Italy and Ecuador, the census's monetary-led cases, and Zimbabwe, whose turn falls in "
         "a measurement gap), one gradual (Chile) and one in progress (Argentina 2023). Same series "
         "construction, same descriptive view."),
        ("fallidos", "The failed plans", PLACEBOS,
         "The five failures with monthly data — three plans with no credible fiscal component (Cruzado, "
         "Verão, Primavera) plus Bresser and Collor, whose announced adjustments were not delivered. A "
         "sixth census failure, Hungary's 1921 Hegedüs attempt, predates the country's price index. "
         "These episodes serve as the comparison group in the paper's durability exercise."),
    ]
    con_datos = sum(len(c) for _, _, c, _ in grupos)
    fichas, toc, n_series = [], [], 0
    for ancla, titulo, cargadores, intro in grupos:
        cfgs = sorted([c() for c in cargadores], key=lambda cfg: pd.Timestamp(cfg["reforma"]))
        fichas.append(f"<h2 id='{ancla}'>{titulo}</h2><p>{intro}</p>")
        toc.append(f"<p style='column-span:all;margin:0.4em 0 0.1em'><b><a href='#{ancla}'>{titulo.split(':')[0]}</a></b></p><div class='toc'>")
        for cfg in cfgs:
            fichas.append(ficha(cfg, censo))
            n_series += 1 + (cfg.get("dinero") is not None)
            toc.append(f"<a href='#ep-{cfg['censo_id']}'>{cfg['label'].split('· ')[1]}</a><br>")
        toc.append("</div>")
    hoy = pd.Timestamp.today().strftime("%d %B %Y")

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The data — Whose Dates Do Prices Obey?</title><style>{CSS}</style></head><body>
<h1>The data behind the paper</h1>
<p class="sub">A descriptive tour of every series used in “Whose Dates Do Prices Obey? Fiscal
Regime Change and the Anchoring of Inflation” (Gustavo Vargas, 2026; presented at the <i>Economic
Affairs</i> Research Workshop, Vinson Centre, University of Buckingham)</p>
<div class="nota"><b>How to read this page.</b> It presents the <b>data</b>, not the results:
what each series is, where it comes from, what window the paper uses and what the raw monthly
rates look like. Each episode card gives a short historical note, the dated policy event (the red
dashed line; a day of 1 means only the month is dated), the census outcome label — durable,
gradual, temporary, failure or in progress, coded under the protocol in the paper's appendix A —
the analysis window, coverage and source, and a chart. <b>Charts plot 100 × the monthly log
change</b>, which keeps hyperinflations on a readable scale; the card summaries convert to
conventional percentages (100 × (e<sup>Δln</sup> − 1) — at low rates the two are close, at
hyperinflation rates they differ enormously). Lines break where months are missing. Two episodes
are deliberate <b>reflations</b> (United States 1933, Japan 1931): there the policy's objective
was to <i>raise</i> the price level. The break tests and estimates live in
<code>src/estimacion/</code> and in the paper's appendix.</div>
{''.join(toc)}
<p>The census counts <b>34 stabilisation programmes launched between 1921 and 2023</b> (the
study's universe closes in 2025), of which <b>{con_datos} have usable monthly data</b> — the
three without are Hungary's 1921 Hegedüs attempt (the price index begins as it died), Hungary's
1946 forint and Nicaragua 1991 (print sources only). That makes {n_series} episode-window series
({con_datos} price, {n_series - con_datos} money; several episodes cut different windows from the
same underlying national series), plus three daily series for the 2022 UK episode, a 19-country
cross-section for the COVID inflation and two quarterly US velocity series. Hand-digitised series
carry their source, page numbers, splices and known printing errata in the file headers under
<code>data/manual/</code>; the rest load from public APIs without keys (FRED, the IMF, and the
central banks of Brazil, Peru and Argentina), cached with date stamps under <code>data/raw/</code>.</p>
{''.join(fichas)}
{bloque_covid()}
{bloque_truss()}
{bloque_velocidad()}
<footer>Generated on {hoy} by <code>src/datos_descriptivos.py</code> from this repository's data
(the UK panel reads <code>src/estimacion/out/truss_event_study.csv</code>, produced by
<code>src/estimacion/truss.py</code>; API series load from the dated caches in
<code>data/raw/</code>, so regenerating on a later date may fetch newer vintages) ·
<a href="https://github.com/gustavovargas/ftpl-empirics-replication">Replication repository</a> ·
Code and compilation MIT-licensed; underlying series remain subject to their sources' terms.</footer>
</body></html>"""
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w") as f:
        f.write(html)
    print(f"OK -> {SALIDA} ({os.path.getsize(SALIDA) / 1e6:.1f} MB, {con_datos} fichas)")


if __name__ == "__main__":
    main()
