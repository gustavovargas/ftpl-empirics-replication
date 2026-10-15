# -*- coding: utf-8 -*-
"""Ensambla el apéndice online: prosa estática (A-E) + tablas generadas desde los CSV del
repositorio (el apéndice y los datos son la misma cosa). Produce apendice.md; build.sh lo
compila a online_appendix.pdf."""
import os
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = AQUI  # sube hasta encontrar la raíz del repo (donde vive data/censo)
while not os.path.isdir(os.path.join(RAIZ, "data", "censo")):
    padre = os.path.dirname(RAIZ)
    if padre == RAIZ:
        raise RuntimeError("no encuentro la raíz del repositorio (data/censo)")
    RAIZ = padre
OUT_EST = os.path.join(RAIZ, "src", "estimacion", "out")

PAIS = {"Austria": "Austria", "Hungria": "Hungary", "Polonia": "Poland", "Alemania": "Germany",
        "Francia": "France", "Belgica": "Belgium", "EEUU": "United States", "Italia": "Italy",
        "Bolivia": "Bolivia", "Israel": "Israel", "Argentina": "Argentina", "Brasil": "Brazil",
        "Peru": "Peru", "Mexico": "Mexico", "Chile": "Chile", "Yugoslavia": "Yugoslavia",
        "Bulgaria": "Bulgaria", "Ucrania": "Ukraine", "Rusia": "Russia", "Turquia": "Turkey",
        "Zimbabue": "Zimbabwe", "Ecuador": "Ecuador", "Nicaragua": "Nicaragua", "Japon": "Japan"}
PLAN = {"Protocolos Sociedad de Naciones": "League of Nations protocols",
        "Intento Hegedüs": "Hegedüs attempt", "Reconstrucción SdN": "League reconstruction",
        "Plan Grabski": "Grabski reform", "Rentenbank + reforma fiscal": "Rentenmark + fiscal reform",
        "Gobierno Poincaré": "Poincaré government", "Estabilización Francqui": "Francqui stabilisation",
        "Forint (tras el pengő)": "Forint (after the pengő)", "Reflación de FDR": "FDR reflation",
        "Estabilización Einaudi": "Einaudi squeeze", "DS 21060 (Paz Estenssoro)": "Decree 21060",
        "Plan de Estabilización Económica": "Economic Stabilization Plan", "Plan Austral": "Austral plan",
        "Plan Primavera": "Primavera plan", "Convertibilidad (Cavallo)": "Convertibility",
        "Ajuste Milei": "Milei adjustment", "Plan Cruzado": "Cruzado plan", "Plan Bresser": "Bresser plan",
        "Plan Verão": "Verão plan", "Plan Collor": "Collor plan", "Plano Real": "Real plan",
        "Fujishock": "Fujishock", "Pacto de Solidaridad": "Solidarity Pact", "Ajuste Cauas": "Cauas adjustment",
        "Plan Balcerowicz": "Balcerowicz plan", "Programa Avramović": "Avramović programme",
        "Caja de conversión": "Currency board", "Estabilización Kuchma (+ grivna 1996)": "Kuchma stabilisation",
        "Corredor cambiario": "Exchange-rate corridor", "Programa Derviş": "Derviş programme",
        "Dolarización": "Dollarisation", "Plan Lacayo (córdoba oro)": "Lacayo plan (córdoba oro)",
        "Reflación de Takahashi": "Takahashi reflation"}
RESULTADO = {"exito_duradero": "Durable", "exito_gradual": "Gradual",
             "exito_temporal": "Temporary", "exito_en_curso": "In progress", "fracaso": "Failure"}
DATOS = {"sargent_digitalizado": "Digitised (Sargent 1982)", "digitalizado_e04": "Digitised (Sargent 1982)",
         "nber_e06": "NBER via FRED", "fred_e07": "FRED", "fred_e08": "FRED/OECD",
         "fred_integrado": "FRED/OECD", "bcb_e05": "BCB + FRED", "bcb_integrado": "BCB",
         "bcrp_integrado": "BCRP", "ifs_dbnomics_integrado": "IMF IFS",
         "datosgobar_mendoza_integrado": "DEIE Mendoza", "bcra_datosgobar_integrado": "BCRA + INDEC",
         "frb_fraser_digitalizado": "Digitised (FRB Bulletin)", "kobe_shizume_integrado": "Shibamoto–Shizume 2014",
         "panoeconomicus_digitalizado": "Digitised (Bogetić et al. 2022)",
         "hanke_ifs_integrado": "Hanke–Kwok 2009 + IFS", "sachs_digitalizado": "Digitised (Sachs 1986)",
         "inexistente_mensual": "None exists", "fuente_de_pago_pendiente": "Paywalled sources only",
         "fuente_impresa_pendiente": "Print sources only"}


def tabla_censo():
    c = pd.read_csv(os.path.join(RAIZ, "data", "censo", "censo_episodios.csv"), comment="#")
    filas = ["| # | Episode | Reform | T | F | M | X | I | Outcome | Monthly data |",
             "|----|--------------------------------|----------|----|----|----|----|----|-----------|--------------------|"]
    for _, r in c.iterrows():
        tipo = "R" if r.tipo == "reflacion" else "D"
        filas.append(f"| {r.id} | {PAIS[r.pais]} — {PLAN[r.plan]} | {r.fecha} | {tipo} | "
                     f"{r.comp_fiscal} | {r.comp_monetaria} | {r.comp_cambiaria} | {r.comp_rentas} | "
                     f"{RESULTADO[r.resultado]} | {DATOS[r.datos_mensuales]} |")
    return "\n".join(filas)


def _fecha(v):
    if pd.isna(v):
        return "—"
    return pd.Timestamp(v).strftime("%b %Y")


def _n(v, dec=0):
    if pd.isna(v):
        return "—"
    return f"{v:+.{dec}f}" if dec == 0 else f"{v:.{dec}f}"


def tabla_rupturas(nombre_csv):
    t = pd.read_csv(os.path.join(OUT_EST, nombre_csv))
    filas = ["| Episode | Reform | BP dist. | ZA dist. | Money dist. | Inherited (log pts/m) | Settlement | Ratio |",
             "|----------------------------|----------|------|------|------|--------|--------|------|"]
    for _, r in t.iterrows():
        filas.append(f"| {r.episodio.split('· ')[1]} | {_fecha(r.reforma)} | "
                     f"{_n(r.dist_precio_reforma)} | {_n(r.dist_za_reforma)} | "
                     f"{_n(r.get('dist_dinero_reforma'))} | {_n(r.dur_pre, 1)} | "
                     f"{_n(r.dur_asentamiento, 1)} | {_n(r.dur_ratio_asentamiento, 2)} |")
    return "\n".join(filas)


def tabla_durabilidad():
    t = pd.read_csv(os.path.join(OUT_EST, "rupturas_durabilidad.csv"))
    grupo = {"exito": "Durable", "fracaso": "Failed", "exito_temporal": "Temporary",
             "exito_gradual": "Gradual", "exito_en_curso": "In progress"}
    filas = ["| Episode | Group | Inherited (log pts/m) | Freeze min. | Settlement | Ratio |",
             "|------------------------------|-----------|---------|---------|---------|------|"]
    for _, r in t.sort_values("ratio_asentamiento").iterrows():
        filas.append(f"| {r.episodio.split('· ')[1]} | {grupo[r.resultado]} | {_n(r.pre, 1)} | "
                     f"{_n(r.congelacion, 1)} | {_n(r.asentamiento, 1)} | {_n(r.ratio_asentamiento, 2)} |")
    return "\n".join(filas)


def tabla_covid():
    t = pd.read_csv(os.path.join(OUT_EST, "covid_cross_datos.csv"))
    filas = ["| Country | Euro | Infl. 20–23 (%) | Fiscal (% GDP) | Debt/GDP | Maturity (y) | B–B | Own M3 |",
             "|------------------|-----|--------|--------|-------|-------|------|------|"]
    for _, r in t.sort_values(["euro", "pais"], ascending=[False, True]).iterrows():
        m3 = "—" if pd.isna(r.get("fred_m3")) or str(r.get("fred_m3")) in ("", "nan") else ""
        filas.append(f"| {r.pais} | {'yes' if r.euro == 1 else 'no'} | {r.infl_acum_20_23:.1f} | "
                     f"{r.fiscal_covid:.1f} | {r.deuda_pib_2019:.0f} | {r.duracion_2019:.1f} | "
                     f"{r.f_bb:.2f} | {m3} |")
    return "\n".join(filas)


def main():
    yaml = ('---\ntitle: "Appendix — Whose Dates Do Prices Obey? Fiscal Regime Change '
            'and the Anchoring of Inflation"\nauthor: "Gustavo Eduardo Vargas Núñez — '
            'Universidad de las Hespérides"\ndate: "October 2026"\nlang: en-GB\n---\n\n')
    cuerpo = []
    for f in ["A_census.md", "B_specs.md", "C_intermediate.md", "D_covid.md", "E_repro.md"]:
        cuerpo.append(open(os.path.join(AQUI, f)).read())
    s = "\n\n".join(cuerpo)
    s = s.replace("{{TABLA_CENSO}}", tabla_censo())
    s = s.replace("{{TABLA_TEMPORALES}}", tabla_rupturas("rupturas_temporales.csv"))
    s = s.replace("{{TABLA_PLACEBOS}}", tabla_rupturas("rupturas_placebos.csv"))
    s = s.replace("{{TABLA_DURABILIDAD}}", tabla_durabilidad())
    s = s.replace("{{TABLA_COVID}}", tabla_covid())
    open(os.path.join(AQUI, "apendice.md"), "w").write(yaml + s)
    print("apendice.md generado")


if __name__ == "__main__":
    main()
