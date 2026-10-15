# -*- coding: utf-8 -*-
"""Test 1 del paper — ¿a qué fecha obedecen los precios?

Detección endógena de rupturas estructurales (Bai-Perron vía dynamic programming;
Zivot-Andrews como robustez) sobre la inflación mensual y el crecimiento monetario mensual
de cada episodio, POR SEPARADO y sin decirle al algoritmo dónde está la reforma.

Predicción TC: la ruptura de la inflación coincide con una ruptura del dinero.
Predicción FTPL: la ruptura de la inflación coincide con la fecha de la reforma FISCAL,
sin ruptura contemporánea del dinero.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ruptures as rpt

from src.utils import RAIZ, estilo
from src.estimacion.series import CARGADORES, PLACEBOS, TEMPORALES

OUTDIR = os.path.join(RAIZ, "src", "estimacion", "out")


# ── Detección de rupturas ─────────────────────────────────────────────────────
def crecimiento_mensual(serie, rango):
    """Tasa de variación mensual (log-diff) recortada al rango del episodio.
    Si la serie tiene meses faltantes (p. ej. empalmes con hueco), la log-diferencia
    a través del hueco se descarta en vez de atribuirse a un solo mes."""
    s = serie.loc[rango[0]:rango[1]].dropna()
    g = np.log(s).diff()
    salto = s.index.to_series().dt.to_period("M").astype("int64").diff()
    return g[(salto == 1) & g.notna()]


def ruptura_dominante(g, min_size=3):
    """Ruptura única óptima (Bai-Perron exacto vía programación dinámica, coste rbf:
    capta cambios de media Y varianza, propios de un cambio de régimen inflacionario)."""
    x = g.values.reshape(-1, 1)
    if len(x) < 2 * min_size + 1:
        return None
    algo = rpt.Dynp(model="rbf", min_size=min_size, jump=1).fit(x)
    idx = algo.predict(n_bkps=1)[0]  # índice del primer punto del segundo régimen
    return g.index[idx]


def rupturas_multiples(g, pen=3.0, min_size=3):
    """Rupturas múltiples con penalización (PELT) — robustez / contexto."""
    x = g.values.reshape(-1, 1)
    algo = rpt.Pelt(model="rbf", min_size=min_size, jump=1).fit(x)
    idx = [i for i in algo.predict(pen=pen) if i < len(g)]
    return [g.index[i] for i in idx]


def meses(a, b):
    """Distancia en meses de calendario (periodos mensuales, no días/30,44: las series
    mezclan etiquetas de principio y fin de mes y el redondeo por días desplaza ±1)."""
    if a is None or b is None:
        return None
    return (pd.Timestamp(a).to_period("M") - pd.Timestamp(b).to_period("M")).n


def za_ruptura(g, trim=0.15):
    """Fecha de ruptura estilo Zivot-Andrews: argmin del t-estadístico del coeficiente
    autorregresivo entre todas las fechas de ruptura candidatas (modelo con quiebre de
    nivel + un rezago aumentado). Robustez independiente de Bai-Perron.
    """
    y = g.values.astype(float)
    n = len(y)
    if n < 12:
        return None
    lo, hi = int(trim * n), int((1 - trim) * n)
    dy = np.diff(y)               # Δy_t
    ylag = y[:-1]                 # y_{t-1}
    dylag = dy[:-1]              # Δy_{t-1} (aumento AR(1))
    dyt = dy[1:]                 # Δy_t alineado
    m = len(dyt)                 # muestra efectiva
    t = np.arange(1, m + 1)
    mejor_t, mejor_k = np.inf, None
    for k in range(lo, hi):
        du = (np.arange(m) >= (k - 1)).astype(float)  # quiebre de nivel en k
        X = np.column_stack([np.ones(m), t, du, ylag[1:], dylag])
        beta, *_ = np.linalg.lstsq(X, dyt, rcond=None)
        resid = dyt - X @ beta
        dof = m - X.shape[1]
        if dof <= 0:
            continue
        s2 = resid @ resid / dof
        xtx_inv = np.linalg.pinv(X.T @ X)
        se_alpha = np.sqrt(s2 * xtx_inv[3, 3])       # coef de y_{t-1}
        if se_alpha == 0:
            continue
        t_alpha = beta[3] / se_alpha
        if t_alpha < mejor_t:
            mejor_t, mejor_k = t_alpha, k
    if mejor_k is None:
        return None
    return g.index[mejor_k + 1]   # +1 por el doble diff/lag


# ── Durabilidad (placebos vs. éxitos) ─────────────────────────────────────────
def _por_offset(g, reforma):
    """Reindexa la serie de crecimiento a offset entero de meses respecto a la reforma."""
    ref = pd.Timestamp(reforma).to_period("M")
    s = g.copy()
    s.index = (s.index.to_period("M") - ref).map(lambda x: x.n)
    return s[~s.index.duplicated(keep="first")]


def durabilidad(cfg, gp):
    """¿El giro de los precios es duradero o se deshace? Tres estadísticos de la
    inflación mensual (log-dif. x100) alrededor de la reforma:
      pre          mediana en [-6, -1]   (la inflación que el plan hereda)
      congelacion  mínimo en [0, +6]     (el efecto mecánico del congelamiento/anuncio)
      asentamiento mediana en [cap-5, cap] (dónde queda la inflación al año),
                   cap = min(+12, plan siguiente - 1)
    Predicción: en los planes sin ancla fiscal asentamiento ~ pre (el congelamiento
    se deshace); en las reformas fiscales asentamiento ~ 0."""
    o = 100 * _por_offset(gp, cfg["reforma"])
    cap = 12
    if cfg.get("siguiente_plan"):
        hasta_sig = (pd.Timestamp(cfg["siguiente_plan"]).to_period("M")
                     - pd.Timestamp(cfg["reforma"]).to_period("M")).n - 1
        cap = min(cap, hasta_sig)
    pre = o.loc[-6:-1].median()
    cong = o.loc[0:6].min() if len(o.loc[0:6]) else np.nan
    ventana = o.loc[cap - 5:cap]
    asent = ventana.median() if len(ventana) else np.nan  # serie corta (p. ej. Polonia): sin dato
    return dict(pre=pre, congelacion=cong, asentamiento=asent, cap=cap,
                ratio_asentamiento=asent / pre if pre and not np.isnan(asent) else np.nan)


def figura_durabilidad(filas, outdir):
    """Dot plot del ratio rebrote/pre por episodio: ~1 = el plan se deshizo; ~0 = duradero."""
    estilo()
    filas = [f for f in filas if not np.isnan(f["ratio_asentamiento"])]
    filas = sorted(filas, key=lambda f: f["ratio_asentamiento"])
    fig, ax = plt.subplots(figsize=(10.5, max(5.2, 0.42 * len(filas) + 1.8)))
    estetica = {"exito": ("#1e8449", "o"), "fracaso": ("#c0392b", "X")}
    for i, f in enumerate(filas):
        color, marca = estetica.get(f["resultado"], ("#d68910", "^"))  # ámbar: gradual/temporal/en curso
        ax.scatter(f["ratio_asentamiento"], i, s=150, color=color, zorder=3, marker=marca)
        ax.annotate(f"  pre {f['pre']:.0f} → a year on {f['asentamiento']:.0f} log-pts/mo.",
                    xy=(f["ratio_asentamiento"], i), xytext=(8, 0), textcoords="offset points",
                    fontsize=8, color="#555", va="center")
    ax.axvline(1.0, color="#c0392b", linestyle="--", linewidth=1.2, alpha=0.7)
    ax.axvline(0.0, color="#999", linewidth=0.8)
    ax.annotate("inflation a year on = inherited\n(the plan unravelled)", xy=(1.0, len(filas) - 1.1),
                xytext=(-8, 0), textcoords="offset points", ha="right", va="top",
                fontsize=9, color="#c0392b")
    ax.set_yticks(range(len(filas)))
    ax.set_yticklabels([f["episodio"] for f in filas])
    ax.set_xlabel("Median inflation one year on / median pre-reform inflation")
    ax.set_title("Durability: only plans with a fiscal anchor keep prices quiet")
    ax.grid(axis="x", alpha=0.25)
    fig.subplots_adjust(left=0.22)
    fig.savefig(os.path.join(outdir, "rupturas_durabilidad.png"), bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"OK -> {os.path.join(outdir, 'rupturas_durabilidad.png')}")


# ── Ejecución ─────────────────────────────────────────────────────────────────
def analizar(cfg):
    ref = pd.Timestamp(cfg["reforma"])
    gp = crecimiento_mensual(cfg["precio"], cfg["rango"])
    rp = ruptura_dominante(gp)
    za = za_ruptura(gp)
    fila = dict(episodio=cfg["label"], tipo=cfg["tipo"], reforma=ref.date(),
                ruptura_precio=rp.date() if rp is not None else None,
                dist_precio_reforma=meses(rp, ref),
                za_precio=za.date() if za is not None else None,
                dist_za_reforma=meses(za, ref))
    if cfg.get("dinero") is not None:
        gm = crecimiento_mensual(cfg["dinero"], cfg["rango"])
        rm = ruptura_dominante(gm)
        fila["ruptura_dinero"] = rm.date() if rm is not None else None
        fila["dist_dinero_reforma"] = meses(rm, ref)
        fila["dist_precio_dinero"] = meses(rp, rm)
    else:
        gm, rm = None, None
    if cfg.get("cambio") is not None:
        gc = crecimiento_mensual(cfg["cambio"], cfg["rango"])
        rc = ruptura_dominante(gc)
        fila["ruptura_cambio"] = rc.date() if rc is not None else None
        fila["dist_cambio_reforma"] = meses(rc, ref)
    return fila, gp, rp, gm, rm


def figura_episodio(cfg, gp, rp, gm, rm, outdir):
    estilo()
    ref = pd.Timestamp(cfg["reforma"])
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.plot(gp.index, 100 * gp, color="#1e8449", linewidth=1.6, label="Monthly inflation (log-diff. of prices)")
    if gm is not None:
        ax.plot(gm.index, 100 * gm, color="#1b6ca8", linewidth=1.4, alpha=0.8,
                label="Monthly money growth")
    # Contexto: rupturas múltiples (PELT) de la serie de precios, como líneas tenues
    try:
        for b in rupturas_multiples(gp):
            ax.axvline(b, color="#1e8449", linestyle="-", linewidth=0.6, alpha=0.25)
    except Exception:
        pass
    ax.axvline(ref, color="#c0392b", linestyle="--", linewidth=1.6)
    ax.annotate("reform\n(actual date)", xy=(ref, ax.get_ylim()[1]), xytext=(5, -4),
                textcoords="offset points", fontsize=9, color="#c0392b", va="top")
    if rp is not None:
        ax.axvline(rp, color="#1e8449", linestyle=":", linewidth=2.0)
        ax.annotate(f"price break\n(detected: {rp.strftime('%b-%y')})", xy=(rp, ax.get_ylim()[0]),
                    xytext=(-4, 8), textcoords="offset points", fontsize=9, color="#1e8449",
                    ha="right", va="bottom")
    if rm is not None:
        ax.axvline(rm, color="#1b6ca8", linestyle=":", linewidth=2.0)
        ax.annotate(f"money break\n({rm.strftime('%b-%y')})", xy=(rm, ax.get_ylim()[0]),
                    xytext=(4, 8), textcoords="offset points", fontsize=9, color="#1b6ca8", va="bottom")
    sufijo = (" — plan without a fiscal anchor (failure)" if cfg.get("resultado") == "fracaso"
              else ": the detected price break against the date of the reform")
    ax.set_title(f"{cfg['label']}{sufijo}")
    ax.set_ylabel("% per month")
    ax.legend(loc="upper right", fontsize=9)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    nombre = cfg["label"].split(" ")[0]
    fig.savefig(os.path.join(outdir, f"rupturas_{nombre}.png"), bbox_inches="tight", dpi=150)
    plt.close(fig)


def figura_resumen(filas, outdir):
    """Dot plot: distancia (meses) de la ruptura de precios y de dinero respecto a la reforma."""
    estilo()
    fig, ax = plt.subplots(figsize=(11, 5.5))
    y = range(len(filas))
    labels = [f["episodio"] for f in filas]
    vistos = set()
    def _lab(clave, texto):
        if clave in vistos:
            return ""
        vistos.add(clave)
        return texto
    for i, f in enumerate(filas):
        dp = f.get("dist_precio_reforma")
        dm = f.get("dist_dinero_reforma")
        dc = f.get("dist_cambio_reforma")
        dz = f.get("dist_za_reforma")
        if dp is not None:
            ax.scatter(dp, i, s=140, color="#1e8449", zorder=3, label=_lab("p", "Price break (Bai–Perron)"))
        if dz is not None:
            ax.scatter(dz, i, s=90, facecolors="none", edgecolors="#145a32", linewidths=2.0,
                       marker="o", zorder=4, label=_lab("z", "Price break (Zivot–Andrews)"))
        if dm is not None:
            ax.scatter(dm, i, s=140, color="#1b6ca8", zorder=3, marker="s",
                       label=_lab("m", "Money break"))
        if dc is not None:
            ax.scatter(dc, i, s=120, color="#8e44ad", zorder=3, marker="D",
                       label=_lab("c", "Exchange-rate break"))
    ax.axvline(0, color="#c0392b", linestyle="--", linewidth=1.6)
    ax.axvspan(-2, 2, color="#c0392b", alpha=0.07)
    # El eje cubre TODAS las distancias (sin recortar extremos como Japón +25 o Turquía -14)
    vals = [f.get(k) for f in filas
            for k in ("dist_precio_reforma", "dist_za_reforma", "dist_dinero_reforma",
                      "dist_cambio_reforma") if f.get(k) is not None]
    ax.set_xlim(min(vals) - 1.5, max(vals) + 1.5)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels)
    ax.set_ylim(-0.6, len(filas) - 0.4)
    ax.invert_yaxis()
    ax.annotate("fiscal reform", xy=(0, len(filas) - 0.55), xytext=(6, 0),
                textcoords="offset points", fontsize=9, color="#c0392b", va="center")
    ax.set_xlabel("Months from the reform (0 = reform month; negative = before)")
    ax.set_title("Test 1: the price break lands on the fiscal reform, not on a break in money")
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    ax.grid(axis="x", alpha=0.25)
    fig.subplots_adjust(left=0.16)
    fig.savefig(os.path.join(outdir, "rupturas_resumen.png"), bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"OK -> {os.path.join(outdir, 'rupturas_resumen.png')}")


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    filas = []
    for cargar in CARGADORES:
        cfg = cargar()
        fila, gp, rp, gm, rm = analizar(cfg)
        filas.append(fila)
        figura_episodio(cfg, gp, rp, gm, rm, outdir)
    df = pd.DataFrame(filas)
    df.to_csv(os.path.join(outdir, "rupturas_resumen.csv"), index=False)
    pd.set_option("display.width", 160, "display.max_columns", 20)
    print("\nTest 1 — rupturas endógenas vs fecha de la reforma (distancias en meses):\n")
    print(df.to_string(index=False))

    # Estadísticos-resumen para el texto del paper
    dp = df["dist_precio_reforma"].dropna()
    dza = df["dist_za_reforma"].dropna()
    print("\n--- Resumen ---")
    print(f"Bai-Perron |ruptura precios - reforma|: mediana {dp.abs().median():.0f} meses, "
          f"máx {dp.abs().max():.0f}; en {(dp.abs() <= 3).sum()}/{len(dp)} episodios es <= 1 trimestre.")
    print(f"Zivot-Andrews (robustez) |ruptura precios - reforma|: mediana {dza.abs().median():.0f} meses, "
          f"máx {dza.abs().max():.0f}; en +-2 meses: {(dza.abs() <= 2).sum()}/{len(dza)}.")
    pares = df.dropna(subset=["dist_precio_dinero"])
    lidera = (pares["dist_precio_dinero"] <= 0).sum()
    print(f"Precios vs dinero (episodios con ambas series, n={len(pares)}): "
          f"la ruptura de precios precede o coincide con la del dinero en {lidera}/{len(pares)} "
          f"(la excepción: Alemania, dinero -1 mes).")
    figura_resumen(filas, outdir)

    # ── Grupos secundarios: temporales/graduales/en curso y placebos sin ancla fiscal ──
    def analizar_grupo(cargadores, nombre_csv, titulo):
        filas_g = []
        for cargar in cargadores:
            cfg = cargar()
            fila, gp, rp, gm, rm = analizar(cfg)
            d = durabilidad(cfg, gp)
            fila.update({f"dur_{k}": round(v, 2) if isinstance(v, float) else v
                         for k, v in d.items()})
            filas_g.append(fila)
            dur.append(dict(episodio=cfg["label"], resultado=cfg["resultado"], **d))
            figura_episodio(cfg, gp, rp, gm, rm, outdir)
        dfg = pd.DataFrame(filas_g)
        dfg.to_csv(os.path.join(outdir, nombre_csv), index=False)
        print(f"\n{titulo}\n")
        print(dfg.to_string(index=False))

    dur = []
    analizar_grupo(TEMPORALES, "rupturas_temporales.csv",
                   "Éxitos graduales / temporales / en curso (ruptura dominante y durabilidad):")
    analizar_grupo(PLACEBOS, "rupturas_placebos.csv",
                   "Placebos — planes SIN ancla fiscal (ruptura dominante y durabilidad):")

    # Durabilidad comparada: placebos vs desinflaciones con ancla fiscal
    for cargar in CARGADORES:
        cfg = cargar()
        if cfg["tipo"] != "desinflacion":
            continue
        gp = crecimiento_mensual(cfg["precio"], cfg["rango"])
        dur.append(dict(episodio=cfg["label"], resultado=cfg["resultado"],
                        **durabilidad(cfg, gp)))
    ddur = pd.DataFrame(dur)
    ddur.to_csv(os.path.join(outdir, "rupturas_durabilidad.csv"), index=False)
    print("\nDurabilidad (inflación %/mes: mediana pre [-6,-1], mínimo congelación [0,+6], "
          "mediana de asentamiento [cap-5,cap]):\n")
    print(ddur.round(2).to_string(index=False))
    rf = ddur[ddur.resultado == "fracaso"]["ratio_asentamiento"]
    re_ = ddur[ddur.resultado == "exito"]["ratio_asentamiento"]
    rt = ddur[~ddur.resultado.isin(["exito", "fracaso"])]["ratio_asentamiento"]
    print(f"\nRatio asentamiento/pre — fracasos: mediana {rf.median():.2f} (n={len(rf)}); "
          f"éxitos duraderos: mediana {re_.median():.2f} (n={len(re_)}); "
          f"graduales/temporales/en curso: mediana {rt.median():.2f} (n={len(rt)}).")
    figura_durabilidad(ddur.to_dict("records"), outdir)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=OUTDIR)
    main(p.parse_args().outdir)
