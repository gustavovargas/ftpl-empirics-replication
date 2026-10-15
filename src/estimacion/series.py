# -*- coding: utf-8 -*-
"""Registro de series mensuales por episodio del censo.

Separa los DATOS de los TESTS: rupturas.py (Test 1) y event_study.py (Test 2) importan
de aquí y no saben de dónde salen las series. Cada cargador devuelve un dict estándar:

  censo_id  fila en data/censo/censo_episodios.csv (la Tabla 1 del paper)
  precio    serie mensual del índice de precios
  dinero    serie mensual del agregado monetario (None si no hay serie fiable)
  cambio    (opcional) tipo de cambio, proxy de expectativas donde falta el dinero
  reforma   fecha de la reforma fiscal (precisión diaria donde se conoce; el censo
            la lleva a precisión de mes — deben coincidir)
  rango     ventana del episodio (recorte de las series)
  label     etiqueta para figuras y tablas
  tipo      "desinflacion" | "reflacion"

Para extender los tests a un episodio nuevo del censo: escribir aquí su cargar_*()
con el censo_id correspondiente, añadirlo a CARGADORES, y actualizar la columna
datos_mensuales del censo. Los eXX del dossier conservan su nombre; los episodios
solo-censo usan cargar_c<censo_id>_<pais>.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import pandas as pd

from src.utils import (RAIZ, fetch_fred, fetch_bcb, fetch_bcrp, fetch_bcra,
                       fetch_datosgobar, fetch_dbnomics)


def _mensual(s):
    return s.resample("MS").mean()


# ── Brasil: series comunes a los cinco planes (Cruzado→Real) ──────────────────
def _brasil_m1_reales():
    """M1 del BCB (SGS 1824, saldo fin de mes, en la moneda corriente de cada periodo)
    empalmado a reales. Redenominaciones (verificadas contra los saltos de la serie):
    cruzado = 1000 cruzeiros (mar-1986), cruzado novo = 1000 cruzados (ene-1989),
    cruzeiro = cruzado novo 1:1 (mar-1990), cruzeiro real = 1000 cruzeiros (ago-1993),
    real = 2750 cruzeiros reais (jul-1994)."""
    m1 = fetch_bcb(1824)["sgs_1824"].astype(float).copy()
    m1.loc[:"1986-02-28"] /= 1000 * 1000 * 1000 * 2750   # cruzeiros antiguos
    m1.loc["1986-03-01":"1988-12-31"] /= 1000 * 1000 * 2750  # cruzados
    m1.loc["1989-01-01":"1993-07-31"] /= 1000 * 2750     # cruzados novos / cruzeiros
    m1.loc["1993-08-01":"1994-06-30"] /= 2750            # cruzeiros reais
    return _mensual(m1)


def _brasil_ipca_indice():
    """Índice de precios reconstruido del IPCA mensual (SGS 433, % a.m., desde 1980-01):
    la fuente primaria brasileña, que cubre los planes de los 80 (la serie OCDE de FRED
    usada en e05 empieza más tarde)."""
    pct = fetch_bcb(433)["sgs_433"].astype(float)
    idx = (1 + pct / 100).cumprod() * 100
    return _mensual(idx)


def cargar_e04():  # Alemania 1923 (censo #5)
    df = pd.read_csv(os.path.join(RAIZ, "data", "manual", "alemania_1923.csv"),
                     comment="#", parse_dates=["fecha"]).set_index("fecha")
    return dict(censo_id=5, precio=df["indice_precios_1913_100"], dinero=df["circulacion_marcos"],
                reforma="1923-11-15", rango=("1922-01-01", "1924-12-31"),
                label="e04 · Germany 1923", tipo="desinflacion", resultado="exito")


def cargar_e05():  # Brasil 1994, Plano Real (censo #21) — M1 empalmado a reales
    m1 = fetch_bcb(1824)["sgs_1824"].astype(float).copy()
    m1.loc[:"1993-07-31"] /= 1000 * 2750
    m1.loc["1993-08-01":"1994-06-30"] /= 2750
    ipc = fetch_fred("BRACPIALLMINMEI")["BRACPIALLMINMEI"]
    return dict(censo_id=21, precio=_mensual(ipc), dinero=_mensual(m1),
                reforma="1994-07-01", rango=("1992-01-01", "1997-12-31"),
                label="e05 · Brazil 1994", tipo="desinflacion", resultado="exito")


def cargar_e06():  # Francia 1926, Poincaré (censo #6) — sin serie monetaria fiable en FRED
    wpi = fetch_fred("M04057FRM360NNBR")["M04057FRM360NNBR"]
    fx = fetch_fred("M1404BUSM306NNBR")["M1404BUSM306NNBR"]
    return dict(censo_id=6, precio=_mensual(wpi), dinero=None, cambio=_mensual(fx),
                reforma="1926-07-23", rango=("1922-01-01", "1928-12-31"),
                label="e06 · France 1926", tipo="desinflacion", resultado="exito")


def cargar_e07():  # EE.UU. 1933, reflación de FDR (censo #9)
    wpi = fetch_fred("PPIACO")["PPIACO"]
    m2 = fetch_fred("M1444AUSM027SNBR")["M1444AUSM027SNBR"]
    return dict(censo_id=9, precio=_mensual(wpi), dinero=_mensual(m2),
                reforma="1933-04-01", rango=("1929-01-01", "1937-12-31"),
                label="e07 · US 1933", tipo="reflacion", resultado="exito")


def cargar_e08():  # Israel 1985 (censo #12)
    ipc = fetch_fred("ISRCPIALLMINMEI")["ISRCPIALLMINMEI"]
    m1 = fetch_fred("MANMM101ILM189S")["MANMM101ILM189S"]
    return dict(censo_id=12, precio=_mensual(ipc), dinero=_mensual(m1),
                reforma="1985-07-01", rango=("1983-01-01", "1990-12-31"),
                label="e08 · Israel 1985", tipo="desinflacion", resultado="exito")


def cargar_c01_austria():  # Austria 1922, protocolos SdN (censo #1) — digitalizado de Sargent (1982)
    df = pd.read_csv(os.path.join(RAIZ, "data", "manual", "austria_1922.csv"),
                     comment="#", parse_dates=["fecha"]).set_index("fecha")
    # la tabla impresa omite oct-dic 1921 en los billetes: la serie monetaria arranca
    # en 1922-01 para no calcular una log-diferencia a través del hueco
    return dict(censo_id=1, precio=df["indice_precios_ene1921_100"].dropna(),
                dinero=df["circulacion_miles_coronas"].loc["1922-01-01":].dropna(),
                cambio=df["coronas_por_dolar"].dropna(),
                reforma="1922-10-02", rango=("1921-01-01", "1924-06-30"),
                label="c01 · Austria 1922", tipo="desinflacion", resultado="exito")


def cargar_c03_hungria():  # Hungría 1924, reconstrucción SdN (censo #3) — digitalizado de Sargent (1982)
    df = pd.read_csv(os.path.join(RAIZ, "data", "manual", "hungria_1924.csv"),
                     comment="#", parse_dates=["fecha"]).set_index("fecha")
    return dict(censo_id=3, precio=df["indice_precios"].dropna(),
                dinero=df["billetes_millones_coronas"].dropna(),
                cambio=df["centavos_por_corona"].dropna(),
                reforma="1924-03-14", rango=("1921-07-01", "1925-03-31"),
                label="c03 · Hungary 1924", tipo="desinflacion", resultado="exito")


def cargar_c22_peru():  # Perú 1990, Fujishock (censo #22) — sin serie monetaria mensual pre-1992 en BCRPData
    ipc = fetch_bcrp("PN01270PM", desde="1986-1", hasta="1995-12")["PN01270PM"]
    return dict(censo_id=22, precio=_mensual(ipc), dinero=None,
                reforma="1990-08-08", rango=("1988-01-01", "1993-12-31"),
                label="c22 · Peru 1990", tipo="desinflacion", resultado="exito")


def cargar_c23_mexico():  # México 1987, Pacto de Solidaridad (censo #23)
    ipc = fetch_fred("MEXCPIALLMINMEI")["MEXCPIALLMINMEI"]
    m1 = fetch_fred("MANMM101MXM189S")["MANMM101MXM189S"]  # arranca dic-1985
    return dict(censo_id=23, precio=_mensual(ipc), dinero=_mensual(m1),
                reforma="1987-12-15", rango=("1985-12-01", "1992-12-31"),
                label="c23 · Mexico 1987", tipo="desinflacion", resultado="exito")


def cargar_c30_turquia():  # Turquía 2001, programa Derviş (censo #30)
    ipc = fetch_fred("TURCPIALLMINMEI")["TURCPIALLMINMEI"]
    m3 = fetch_fred("MABMM301TRM189S")["MABMM301TRM189S"]
    return dict(censo_id=30, precio=_mensual(ipc), dinero=_mensual(m3),
                reforma="2001-04-14", rango=("1998-01-01", "2005-12-31"),
                label="c30 · Turkey 2001", tipo="desinflacion", resultado="exito")


def cargar_c11_bolivia():  # Bolivia 1985, DS 21060 (censo #11) — digitalizado de Sachs (NBER WP 2073)
    # Índice reconstruido de la tasa mensual (Tabla 1c de Sachs; datos INE). Sin serie monetaria
    # mensual en la fuente: solo-precios. El +56,5% de sep-1985 es arrastre del promedio mensual
    # (los precios dejan de subir el 9-sep, nota de Sachs): la ruptura "real" es ago/sep-1985.
    df = pd.read_csv(os.path.join(RAIZ, "data", "manual", "bolivia_1985.csv"),
                     comment="#", parse_dates=["fecha"]).set_index("fecha")
    idx = (1 + df["inflacion_mensual_pct"] / 100).cumprod() * 100
    return dict(censo_id=11, precio=idx, dinero=None,
                reforma="1985-08-29", rango=("1984-01-01", "1986-09-30"),
                label="c11 · Bolivia 1985", tipo="desinflacion", resultado="exito")


def cargar_c07_belgica():  # Bélgica 1926, Francqui (censo #7) — digitalizado del Federal Reserve Bulletin (FRASER)
    # Reforma: plenos poderes del gobierno Jaspar-Francqui, 16-jul-1926 (fechado como Francia:
    # el cambio de régimen fiscal, no la estabilización de iure del 25-oct). Sin serie monetaria
    # mensual accesible: solo-precios.
    df = pd.read_csv(os.path.join(RAIZ, "data", "manual", "belgica_1926.csv"),
                     comment="#", parse_dates=["fecha"]).set_index("fecha")
    return dict(censo_id=7, precio=df["wpi_preguerra_100"].astype(float), dinero=None,
                reforma="1926-07-16", rango=("1924-04-01", "1928-12-31"),
                label="c07 · Belgium 1926", tipo="desinflacion", resultado="exito")


def cargar_c34_takahashi():  # Japón 1931, reflación de Takahashi (censo #34) — dataset Shibamoto-Shizume
    """Dataset mensual de entreguerras de Shibamoto & Shizume (2014, Explorations in Economic
    History), publicado por el CCSS de la Universidad de Kobe (data/raw/kobe_shibamoto_shizume_
    A2-01.xlsx): IPM (media 1934-36=100), M1 (10.000 yenes) y tipo de cambio efectivo (1917=100),
    1920M01-1936M12. Reforma: 13-dic-1931, Takahashi asume Finanzas y saca al yen del patrón oro;
    monetización por suscripción directa del BoJ desde nov-1932. Ventana hasta dic-1936 (Takahashi
    es asesinado en feb-1936 al intentar retirar el estímulo)."""
    df = pd.read_excel(os.path.join(RAIZ, "data", "raw", "kobe_shibamoto_shizume_A2-01.xlsx"),
                       sheet_name="macroeconomic indicators", skiprows=2,
                       names=["obs", "rail", "wpi", "futures", "fiscal", "fx", "m1"])
    df["fecha"] = pd.to_datetime(df["obs"], format="%YM%m")
    df = df.set_index("fecha")
    return dict(censo_id=34, precio=df["wpi"].astype(float), dinero=df["m1"].astype(float),
                cambio=df["fx"].astype(float),
                reforma="1931-12-13", rango=("1929-01-01", "1936-12-31"),
                label="c34 · Japan 1931", tipo="reflacion", resultado="exito")


def cargar_c27_bulgaria():  # Bulgaria 1997, caja de conversión (censo #27) — IPC del IFS vía DBnomics
    # La caja entra en vigor el 1-jul-1997, pero se anuncia con el acuerdo FMI/gobierno interino
    # en feb-mar-1997: esperar la ruptura ANTES de la fecha legal, como en Austria.
    # Sin agregado monetario mensual en IFS antes de 2005: solo-precios.
    ipc = fetch_dbnomics("IMF", "IFS", "M.BG.PCPI_IX")["M.BG.PCPI_IX"]
    return dict(censo_id=27, precio=ipc, dinero=None,
                reforma="1997-07-01", rango=("1995-01-01", "2001-12-31"),
                label="c27 · Bulgaria 1997", tipo="desinflacion", resultado="exito")


# ── Éxitos graduales / temporales / en curso (grupo intermedio del censo) ─────

def cargar_c10_italia():  # Italia 1947, "stretta di Einaudi" (censo #10) — digitalizado del FRB Bulletin (FRASER)
    # EL CASO ADVERSARIAL del censo: estabilización duradera cuyo instrumento próximo fue
    # MONETARIO (encaje obligatorio efectivo 30-sep-1947, tipo de descuento), con la
    # consolidación fiscal (Pella) y la ayuda Marshall llegando en su estela (comp_fiscal=1).
    # Se analiza en la tabla secundaria y se discute como tal en el paper. Solo-precios.
    df = pd.read_csv(os.path.join(RAIZ, "data", "manual", "italia_1947.csv"),
                     comment="#", parse_dates=["fecha"]).set_index("fecha")
    return dict(censo_id=10, precio=df["wpi_1938_100"].astype(float), dinero=None,
                reforma="1947-09-30", rango=("1947-01-01", "1949-09-30"),
                label="c10 · Italy 1947", tipo="desinflacion", resultado="exito")


def cargar_c25_balcerowicz():  # Polonia 1990, plan Balcerowicz (censo #25) — IPC del IFS vía DBnomics
    # Terapia de choque del 1-ene-1990: la ventana pre incluye la liberalización de precios de
    # los alimentos de ago-1989 y la hiperinflación de oct-1989/ene-1990. Solo-precios (sin
    # agregado monetario mensual en IFS para la ventana).
    ipc = fetch_dbnomics("IMF", "IFS", "M.PL.PCPI_IX")["M.PL.PCPI_IX"]
    return dict(censo_id=25, precio=ipc, dinero=None,
                reforma="1990-01-01", rango=("1988-01-01", "1994-12-31"),
                label="c25 · Poland 1990", tipo="desinflacion", resultado="exito")


def cargar_c32_ecuador():  # Ecuador 2000, dolarización (censo #32) — IPC del IFS vía DBnomics
    # Caso de ancla MONETARIA-CAMBIARIA extrema (comp_fiscal=1): la dolarización renuncia a la
    # imprenta de forma permanente — un cambio constitucional de las reglas, pero liderado por el
    # instrumento monetario; se analiza en la tabla secundaria como Italia-1947. La convergencia
    # de la inflación fue notoriamente lenta (96%% anual en 2000). Solo-precios.
    ipc = fetch_dbnomics("IMF", "IFS", "M.EC.PCPI_IX")["M.EC.PCPI_IX"]
    return dict(censo_id=32, precio=ipc, dinero=None,
                reforma="2000-01-09", rango=("1997-01-01", "2004-12-31"),
                label="c32 · Ecuador 2000", tipo="desinflacion", resultado="exito")


def cargar_c31_zimbabue():  # Zimbabue 2009, dolarización + presupuesto de caja (censo #31)
    # Pre: Tabla 1 de Hanke-Kwok (Cato Journal 2009; oficial RBZ hasta jul-08, OMIR después),
    # digitalizada a data/manual/zimbabue_2009.csv; termina el 14-nov-2008 cuando la moneda deja
    # de cotizar. dic-2008 SIN DATO: la guarda anti-huecos descarta la log-dif a través del hueco.
    # Post: IPC en USD del IFS desde ene-2009 (validado contra los valores del propio paper).
    # CAVEAT DE TIMING: la ruptura coincide con el hueco de medición (la moneda murió antes de
    # la reforma formal) — el estadístico informativo aquí es la durabilidad, no la distancia.
    df = pd.read_csv(os.path.join(RAIZ, "data", "manual", "zimbabue_2009.csv"),
                     comment="#", parse_dates=["fecha"]).set_index("fecha")
    pre = (1 + df["inflacion_mensual_pct"] / 100).cumprod() * 100
    post = fetch_dbnomics("IMF", "IFS", "M.ZW.PCPI_IX")["M.ZW.PCPI_IX"]
    post = pre.iloc[-1] * post / post.iloc[0]  # re-base arbitrario: el nivel a través del hueco
    precio = pd.concat([pre, post.loc["2009-01-01":]])  # no es informativo, el crecimiento sí
    return dict(censo_id=31, precio=precio, dinero=None,
                reforma="2009-02-13", rango=("2007-03-01", "2012-12-31"),
                label="c31 · Zimbabwe 2009", tipo="desinflacion", resultado="exito")


def cargar_c04_polonia():  # Polonia 1924, reforma Grabski (censo #4) — digitalizado de Sargent (1982)
    # El índice de precios TERMINA en abr-1924 (+3 meses tras la reforma) con la conversión al
    # złoty: el timing de la ruptura es calculable, la durabilidad a 12 meses no (de ahí que el
    # censo la codifique exito_temporal por la recaída de 1925, documentada en la literatura).
    df = pd.read_csv(os.path.join(RAIZ, "data", "manual", "polonia_1924.csv"),
                     comment="#", parse_dates=["fecha"]).set_index("fecha")
    # empalme marcos->złoty (1 zł = 1.800.000 marcos; la serie de marcos está en millones)
    dinero = pd.concat([df["circulacion_millones_marcos"].dropna() / 1.8,
                        df["circulacion_zloty"].dropna()])
    cambio = pd.concat([df["cents_por_marco"].dropna() * 1.8e6,
                        df["cents_por_zloty"].dropna()])
    return dict(censo_id=4, precio=df["wpi_1914_100"].dropna(), dinero=dinero, cambio=cambio,
                reforma="1924-01-11", rango=("1921-01-01", "1925-04-30"),
                label="c04 · Poland 1924", tipo="desinflacion", resultado="exito_temporal")


def _argentina_ipc_mendoza():
    """IPC de la provincia de Mendoza (DEIE, vía datos.gob.ar), mensual desde 1970 (metadatos dicen 1968, pero la API solo sirve desde 1970): la serie
    larga mensual accesible para los planes argentinos de los 80-90 (el IPC-GBA histórico del
    INDEC ya no está publicado en línea). Provincial pero fiel a la dinámica nacional: Austral
    jun-85 +28,9% -> jul +4,0%; validado contra los valores conocidos del INDEC GBA."""
    return fetch_datosgobar("195.1_NIVEL_GENERAL_0_0_13", desde="1970-01-01")["nivel_general"]


def cargar_c13_austral():  # Argentina 1985, Plan Austral (censo #13, exito_temporal) — sin M mensual accesible
    return dict(censo_id=13, precio=_argentina_ipc_mendoza(), dinero=None,
                reforma="1985-06-14", rango=("1983-06-01", "1988-07-31"),
                siguiente_plan="1988-08-03", resultado="exito_temporal",
                label="c13 · Argentina Austral 1985", tipo="desinflacion")


def cargar_c15_convertibilidad():  # Argentina 1991, Convertibilidad (censo #15, exito_temporal)
    # ventana desde abr-1990 (tras el pico Bonex/Erman) para aislar la Convertibilidad
    # de las hiperinflaciones de 1989-90
    return dict(censo_id=15, precio=_argentina_ipc_mendoza(), dinero=None,
                reforma="1991-04-01", rango=("1990-04-01", "1996-12-31"),
                resultado="exito_temporal",
                label="c15 · Argentina Convertibility 1991", tipo="desinflacion")

def cargar_c24_chile():  # Chile 1975, ajuste Cauas (censo #24, exito_gradual) — M mensual solo desde 1986
    # ventana desde 1974 para que la liberalización de precios de oct-1973 no domine la detección
    ipc = fetch_fred("CHLCPIALLMINMEI")["CHLCPIALLMINMEI"]
    return dict(censo_id=24, precio=_mensual(ipc), dinero=None,
                reforma="1975-04-24", rango=("1974-01-01", "1979-12-31"),
                label="c24 · Chile 1975", tipo="desinflacion", resultado="exito_gradual")


def cargar_c29_rusia():  # Rusia 1995, corredor cambiario + presupuesto sin financiación del CBR (censo #29, exito_temporal)
    # la ventana termina antes de la crisis de ago-1998 para no detectarla como "la" ruptura
    ipc = fetch_fred("RUSCPIALLMINMEI")["RUSCPIALLMINMEI"]
    return dict(censo_id=29, precio=_mensual(ipc), dinero=None,
                reforma="1995-07-06", rango=("1993-01-01", "1998-05-31"),
                label="c29 · Russia 1995", tipo="desinflacion", resultado="exito_temporal")


def cargar_c16_milei():  # Argentina 2023, ajuste Milei (censo #16, exito_en_curso)
    ipc = fetch_datosgobar("148.3_INIVELNAL_DICI_M_26")["ipc_nivel_general_nacional"]
    base = fetch_bcra(15, desde="2019-01-01")["bcra_15"]  # base monetaria, diaria -> media mensual
    return dict(censo_id=16, precio=ipc, dinero=_mensual(base),
                reforma="2023-12-12", rango=("2021-01-01", "2026-09-30"),
                label="c16 · Argentina 2023", tipo="desinflacion", resultado="exito_en_curso")


def cargar_c26_yugoslavia():  # RF Yugoslavia 1994, programa Avramović (censo #26) — digitalizado de Panoeconomicus 2022
    # Serie de la Tabla 1 de Bogetic-Dragutinovic-Petrovic (termina dic-1994: ventana post de
    # 11 meses). feb-1994 sobreestima por arrastre (los precios paran en UNA semana, dato
    # semanal de la fuente). El IFS de Serbia empieza feb-1994: sin pre-período alternativo.
    df = pd.read_csv(os.path.join(RAIZ, "data", "manual", "yugoslavia_1994.csv"),
                     comment="#", parse_dates=["fecha"]).set_index("fecha")
    idx = (1 + df["inflacion_mensual_pct"] / 100).cumprod() * 100
    return dict(censo_id=26, precio=idx, dinero=None,
                reforma="1994-01-24", rango=("1992-01-01", "1994-12-31"),
                label="c26 · Yugoslavia 1994", tipo="desinflacion", resultado="exito_temporal")


def cargar_c28_ucrania():  # Ucrania 1994, estabilización Kuchma (censo #28) — IPC del IFS vía DBnomics
    # Ventana desde feb-1992 (excluye el one-off de la liberalización de precios soviética de
    # ene-1992, +285%% en un mes) hasta may-1998 (excluye la crisis de ago-1998, como en Rusia).
    # Ojo interpretativo: la inflación pre-Kuchna de 1994 estaba comprimida por controles
    # administrativos; el programa de oct-1994 LIBERALIZA precios (salto en oct-nov) y luego
    # estabiliza. Validado contra la tabla mensual de Ukrstat (isc_m). Solo-precios.
    ipc = fetch_dbnomics("IMF", "IFS", "M.UA.PCPI_IX")["M.UA.PCPI_IX"]
    return dict(censo_id=28, precio=ipc, dinero=None,
                reforma="1994-10-11", rango=("1992-02-01", "1998-05-31"),
                label="c28 · Ukraine 1994", tipo="desinflacion", resultado="exito_temporal")


# ── Placebos: planes SIN ancla fiscal (censo: comp_fiscal débil, resultado=fracaso) ──
# Ventanas acotadas por el plan vecino (Brasil encadenó un plan cada 14-19 meses);
# `siguiente_plan` capa las métricas de durabilidad para no contaminarlas con el
# congelamiento del plan posterior.

def cargar_c14_primavera():  # Argentina 1988, Plan Primavera (censo #14) — sin ajuste fiscal, fracaso
    # la ventana termina antes del plan Bunge&Born (jul-1989); la hiperinflación de 1989
    # es el desenlace del propio Primavera
    return dict(censo_id=14, precio=_argentina_ipc_mendoza(), dinero=None,
                reforma="1988-08-03", rango=("1986-09-01", "1989-06-30"),
                siguiente_plan="1989-07-08", resultado="fracaso",
                label="c14 · Argentina Primavera 1988", tipo="desinflacion")


def cargar_c17_cruzado():  # Brasil, Plan Cruzado (censo #17) — congelación + moneda nueva, sin fiscal
    return dict(censo_id=17, precio=_brasil_ipca_indice(), dinero=_brasil_m1_reales(),
                reforma="1986-02-28", rango=("1984-03-01", "1987-05-31"),
                siguiente_plan="1987-06-12", resultado="fracaso",
                label="c17 · Brazil Cruzado 1986", tipo="desinflacion")


def cargar_c18_bresser():  # Brasil, Plan Bresser (censo #18) — congelación parcial, ajuste fiscal anunciado y abandonado
    return dict(censo_id=18, precio=_brasil_ipca_indice(), dinero=_brasil_m1_reales(),
                reforma="1987-06-12", rango=("1986-04-01", "1988-12-31"),
                siguiente_plan="1989-01-15", resultado="fracaso",
                label="c18 · Brazil Bresser 1987", tipo="desinflacion")


def cargar_c19_verao():  # Brasil, Plan Verão (censo #19) — congelación + cruzado novo, sin fiscal
    return dict(censo_id=19, precio=_brasil_ipca_indice(), dinero=_brasil_m1_reales(),
                reforma="1989-01-15", rango=("1987-07-01", "1990-02-28"),
                siguiente_plan="1990-03-16", resultado="fracaso",
                label="c19 · Brazil Verão 1989", tipo="desinflacion")


def cargar_c20_collor():  # Brasil, Plan Collor (censo #20) — confiscación de liquidez, sin ancla fiscal creíble
    # Ojo: la confiscación drenó los agregados AMPLIOS (overnight/ahorro); el M1 SUBE
    # x2,2 en mar-1990 por la conversión parcial a cruzeiros. La ventana incluye
    # Collor II (ene-1991); siguiente_plan la capa.
    return dict(censo_id=20, precio=_brasil_ipca_indice(), dinero=_brasil_m1_reales(),
                reforma="1990-03-16", rango=("1989-02-01", "1991-12-31"),
                siguiente_plan="1991-01-31", resultado="fracaso",
                label="c20 · Brazil Collor 1990", tipo="desinflacion")


# Grupos del censo:
#   CARGADORES  éxitos duraderos (+ la reflación de FDR) — Test 1 y 2 del paper
#   TEMPORALES  éxitos graduales / temporales / en curso — tabla secundaria
#   PLACEBOS    planes sin ancla fiscal (fracaso) — Test 1-placebo
CARGADORES = [cargar_c01_austria, cargar_e04, cargar_c03_hungria, cargar_c07_belgica,
              cargar_e06, cargar_c34_takahashi, cargar_e07, cargar_e08, cargar_c11_bolivia,
              cargar_c23_mexico, cargar_c25_balcerowicz, cargar_c22_peru, cargar_e05,
              cargar_c27_bulgaria, cargar_c30_turquia]
TEMPORALES = [cargar_c04_polonia, cargar_c10_italia, cargar_c24_chile, cargar_c13_austral,
              cargar_c32_ecuador, cargar_c31_zimbabue,
              cargar_c15_convertibilidad, cargar_c26_yugoslavia, cargar_c28_ucrania,
              cargar_c29_rusia, cargar_c16_milei]
PLACEBOS = [cargar_c17_cruzado, cargar_c18_bresser, cargar_c14_primavera,
            cargar_c19_verao, cargar_c20_collor]
