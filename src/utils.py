# -*- coding: utf-8 -*-
"""Utilidades comunes del proyecto ftpl_empirics.

Convenciones heredadas de efecto_ricardo_validacion_macro: sin API keys,
etiquetas en español, dpi=150, PNG + CSV espejo en out/.
"""
import io
import os
import time
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import requests

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FRED = os.path.join(RAIZ, "data", "raw", "fred")

FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"


def ensure_output_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def fetch_fred(serie, refrescar=False):
    """Descarga una serie de FRED (sin API key) y la cachea en data/raw/fred.

    Devuelve un DataFrame con índice de fechas y una columna con el nombre de la serie.
    El cache se renueva si se pide `refrescar` o si el fichero no es del día.
    """
    ensure_output_dir(CACHE_FRED)
    fcache = os.path.join(CACHE_FRED, f"{serie}_{date.today().isoformat()}.csv")
    if not os.path.exists(fcache) or refrescar:
        r = requests.get(FRED_CSV.format(sid=serie), timeout=60)
        r.raise_for_status()
        if not r.text.startswith("observation_date"):
            raise ValueError(f"FRED no devolvió una serie válida para {serie!r}")
        with open(fcache, "w", encoding="utf-8") as f:
            f.write(r.text)
    df = pd.read_csv(fcache)
    df.columns = ["fecha", serie]
    df["fecha"] = pd.to_datetime(df["fecha"])
    df[serie] = pd.to_numeric(df[serie], errors="coerce")
    return df.set_index("fecha")


def fetch_bcb(codigo, refrescar=False):
    """Descarga una serie del SGS del Banco Central de Brasil (sin API key) con cache.

    Devuelve un DataFrame con índice de fechas y una columna 'sgs_<codigo>'.
    Ojo: muchas series históricas del SGS vienen en la moneda corriente de cada
    periodo (cruzeiros, cruzeiros reais, reales); los empalmes son cosa del llamante.
    """
    cache_dir = os.path.join(RAIZ, "data", "raw", "bcb")
    ensure_output_dir(cache_dir)
    fcache = os.path.join(cache_dir, f"sgs_{codigo}_{date.today().isoformat()}.csv")
    col = f"sgs_{codigo}"
    if not os.path.exists(fcache) or refrescar:
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json"
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        datos = r.json()
        if not isinstance(datos, list) or not datos:
            raise ValueError(f"SGS {codigo}: respuesta inesperada del BCB")
        df = pd.DataFrame(datos)
        df["fecha"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
        df[col] = pd.to_numeric(df["valor"], errors="coerce")
        df[["fecha", col]].to_csv(fcache, index=False)
    df = pd.read_csv(fcache, parse_dates=["fecha"])
    return df.set_index("fecha")


def fetch_bcrp(codigo, desde="1980-1", hasta="2026-12", refrescar=False):
    """Descarga una serie mensual de BCRPData (Banco Central de Reserva del Perú, sin API key)
    con cache en data/raw/bcrp. Devuelve un DataFrame con índice de fechas y una columna <codigo>.

    La API devuelve un pseudo-CSV con filas separadas por <br> y meses en español abreviado."""
    cache_dir = os.path.join(RAIZ, "data", "raw", "bcrp")
    ensure_output_dir(cache_dir)
    fcache = os.path.join(cache_dir, f"{codigo}_{date.today().isoformat()}.csv")
    if not os.path.exists(fcache) or refrescar:
        url = f"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{codigo}/csv/{desde}/{hasta}"
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        meses = dict(Ene=1, Feb=2, Mar=3, Abr=4, May=5, Jun=6, Jul=7,
                     Ago=8, Sep=9, Set=9, Oct=10, Nov=11, Dic=12)
        filas = []
        for linea in r.text.split("<br>")[1:]:  # la primera es la cabecera
            partes = [p.strip().strip('"') for p in linea.split('","')]
            if len(partes) != 2 or not partes[1]:
                continue
            mes, anio = partes[0].replace('"', "").split(".")
            try:
                filas.append((pd.Timestamp(int(anio), meses[mes[:3]], 1), float(partes[1])))
            except (KeyError, ValueError):
                continue
        if not filas:
            raise ValueError(f"BCRP {codigo}: respuesta sin datos")
        pd.DataFrame(filas, columns=["fecha", codigo]).to_csv(fcache, index=False)
    df = pd.read_csv(fcache, parse_dates=["fecha"])
    return df.set_index("fecha")


def fetch_bcra(idvariable, desde="2016-01-01", refrescar=False):
    """Descarga una variable monetaria del BCRA (API v4.0, sin key, frecuencia diaria)
    con cache en data/raw/bcra_api. Devuelve un DataFrame con columna 'bcra_<id>'."""
    cache_dir = os.path.join(RAIZ, "data", "raw", "bcra_api")
    ensure_output_dir(cache_dir)
    fcache = os.path.join(cache_dir, f"bcra_{idvariable}_{date.today().isoformat()}.csv")
    col = f"bcra_{idvariable}"
    if not os.path.exists(fcache) or refrescar:
        filas, offset = [], 0
        while True:
            url = (f"https://api.bcra.gob.ar/estadisticas/v4.0/monetarias/{idvariable}"
                   f"?desde={desde}&hasta={date.today().isoformat()}&limit=1000&offset={offset}")
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            js = r.json()
            detalle = js["results"][0]["detalle"] if js.get("results") else []
            filas += [(d["fecha"], d["valor"]) for d in detalle]
            if len(detalle) < 1000:
                break
            offset += 1000
        if not filas:
            raise ValueError(f"BCRA {idvariable}: respuesta sin datos")
        df = pd.DataFrame(filas, columns=["fecha", col]).sort_values("fecha")
        df.to_csv(fcache, index=False)
    df = pd.read_csv(fcache, parse_dates=["fecha"])
    return df.set_index("fecha")


def fetch_datosgobar(serie_id, desde="1900-01-01", refrescar=False):
    """Descarga una serie de apis.datos.gob.ar (sin key) con cache en data/raw/datosgobar.
    Devuelve un DataFrame con índice de fechas y la columna nombrada por la API.

    Ojo con esta API: el máximo real es limit=1000 (pedir más devuelve una respuesta CON
    HUECOS en vez de un error), y algunas series (p. ej. las de la DEIE Mendoza) devuelven
    vacío en formato CSV o sin start_date — por eso se usa JSON + start_date + paginación."""
    cache_dir = os.path.join(RAIZ, "data", "raw", "datosgobar")
    ensure_output_dir(cache_dir)
    fcache = os.path.join(cache_dir, f"{serie_id.replace('.', '_')}_{date.today().isoformat()}.csv")
    if not os.path.exists(fcache) or refrescar:
        # El backend de la API es poco fiable: la misma consulta devuelve a veces vacío o
        # una copia con valores nulos intermitentes. Se reintenta y se FUSIONAN los valores
        # no nulos de cada intento hasta completar la serie (o agotar los intentos).
        valores, col = {}, None

        def _una_pasada():
            nonlocal col
            start = 0
            while True:
                url = (f"https://apis.datos.gob.ar/series/api/series/?ids={serie_id}&format=json"
                       f"&start_date={desde}&limit=1000&start={start}&metadata=full")
                r = requests.get(url, timeout=60)
                r.raise_for_status()
                js = r.json()
                if col is None:
                    try:
                        col = js["meta"][1]["field"]["title"]
                    except (KeyError, IndexError):
                        col = serie_id.replace(".", "_")
                datos = js.get("data", [])
                for fecha, valor in datos:
                    if valor is not None:
                        valores[fecha] = valor
                    else:
                        valores.setdefault(fecha, None)
                if len(datos) < 1000:
                    break
                start += 1000

        for intento in range(6):
            _una_pasada()
            if valores and not any(v is None for v in valores.values()):
                break
            time.sleep(2)
        filas = sorted(valores.items())
        huecos = sum(1 for _, v in filas if v is None)
        if huecos:
            print(f"AVISO datos.gob.ar {serie_id}: {huecos} valores nulos tras 6 intentos")
        if not filas:
            raise ValueError(f"datos.gob.ar no devolvió datos para {serie_id!r}")
        pd.DataFrame(filas, columns=["fecha", col]).to_csv(fcache, index=False)
    df = pd.read_csv(fcache, parse_dates=["fecha"])
    return df.set_index("fecha")


def fetch_dbnomics(provider, dataset, codigo, refrescar=False):
    """Descarga una serie de DBnomics (api.db.nomics.world, sin API key) con cache en
    data/raw/dbnomics. Útil para el IFS del FMI (p. ej. IMF/IFS/M.BG.PCPI_IX).
    Devuelve un DataFrame con índice de fechas y una columna con el código."""
    cache_dir = os.path.join(RAIZ, "data", "raw", "dbnomics")
    ensure_output_dir(cache_dir)
    slug = f"{provider}_{dataset}_{codigo}".replace(".", "_").replace("/", "_")
    fcache = os.path.join(cache_dir, f"{slug}_{date.today().isoformat()}.csv")
    if not os.path.exists(fcache) or refrescar:
        url = f"https://api.db.nomics.world/v22/series/{provider}/{dataset}/{codigo}?observations=1"
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        docs = r.json().get("series", {}).get("docs", [])
        if not docs:
            raise ValueError(f"DBnomics sin datos para {provider}/{dataset}/{codigo}")
        s = docs[0]
        df = pd.DataFrame({"fecha": pd.to_datetime(s["period"]), codigo: s["value"]})
        df[codigo] = pd.to_numeric(df[codigo], errors="coerce")
        df.dropna().to_csv(fcache, index=False)
    df = pd.read_csv(fcache, parse_dates=["fecha"])
    return df.set_index("fecha")


def estilo():
    """Estilo común de los gráficos del dossier."""
    plt.rcParams.update({
        "figure.figsize": (11, 6.5),
        "figure.dpi": 110,
        "savefig.dpi": 150,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "legend.frameon": False,
    })


def anotar_evento(ax, fecha, texto, y_frac=0.92, color="#444444", rotacion=0):
    """Línea vertical + etiqueta para marcar un acontecimiento en una serie temporal."""
    f = pd.Timestamp(fecha)
    ax.axvline(f, color=color, linestyle="--", linewidth=1.1, alpha=0.8)
    ax.annotate(
        texto,
        xy=(f, ax.get_ylim()[0] + y_frac * (ax.get_ylim()[1] - ax.get_ylim()[0])),
        xytext=(6, 0), textcoords="offset points",
        fontsize=9, color=color, rotation=rotacion, va="top",
    )


def sombrear(ax, desde, hasta, etiqueta=None, color="#d95f02", alpha=0.10):
    """Sombreado de un tramo temporal (p. ej. una ruptura de la velocidad)."""
    d, h = pd.Timestamp(desde), pd.Timestamp(hasta)
    ax.axvspan(d, h, color=color, alpha=alpha)
    if etiqueta:
        centro = d + (h - d) / 2
        ax.annotate(etiqueta, xy=(centro, ax.get_ylim()[1]), xytext=(0, -12),
                    textcoords="offset points", ha="center", fontsize=9, color="#7a3d02")


def caja_veredicto(fig, texto):
    """Caja de texto al pie del gráfico con el veredicto del episodio (encima de la fuente)."""
    fig.text(0.01, 0.045, texto, fontsize=9, style="italic", color="#333333",
             wrap=True, va="bottom")


def guardar(fig, df, outdir, nombre, fuente, etiqueta_fuente="Fuente"):
    """Guarda PNG + CSV espejo, con pie de fuente, y cierra la figura."""
    ensure_output_dir(outdir)
    fig.text(0.99, 0.005, f"{etiqueta_fuente}: {fuente}", fontsize=8, color="#666666",
             ha="right", va="bottom")
    fpng = os.path.join(outdir, f"{nombre}.png")
    fig.savefig(fpng, bbox_inches="tight")
    plt.close(fig)
    df.to_csv(os.path.join(outdir, f"{nombre}.csv"))
    print(f"OK -> {fpng}")
    return fpng
