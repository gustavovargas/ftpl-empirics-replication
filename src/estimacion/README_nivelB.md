# Nivel B — identificación moderna (secciones 6a y 6b del paper)

## 6b — El "Poincaré moderno": el mini-budget de Truss (`truss.py`)

Event study de alta frecuencia (diario) del mini-budget británico del 23 de septiembre de 2022:
~45.000 M£ de recortes fiscales **sin financiar**, anunciados mientras el Banco de Inglaterra
endurecía la política monetaria.

**El test**: si lo que gobierna el valor de la libra fuera la cantidad de dinero, un banco central
que sube tipos debería *fortalecerla*. La FTPL predice lo contrario: un anuncio fiscal que deteriora
el respaldo hunde la moneda y dispara el coste de la deuda, de inmediato.

**Observado** (ventana 20–27 sep):
- **GBP/USD**: 1,141 → **1,070** (mínimo histórico, 26-sep).
- **Gilt nominal 10 años**: 3,34% → 4,43% (**+110 pb**).
- **Gilt real 10 años** (coste real de la deuda): −0,57% → **+1,06% (+163 pb)**.

Todo en la ventana del anuncio, con el BoE en modo restrictivo. El 28-sep el Banco de Inglaterra
tuvo que intervenir con compras de emergencia de gilts para frenar la espiral de los fondos LDI.
Es el experimento más limpio del dossier: política monetaria y fiscal empujando en direcciones
opuestas, y ganó la fiscal.

**Fuentes**: FRED (`DEXUSUK`, diario) y Banco de Inglaterra IADB (`IUDMNZC` nominal, `IUDMRZC` real,
zero-coupon 10 años). Réplica del método de Hazell & Hobler (2025) para el runoff de Georgia;
el componente mecánico LDI está documentado en Pinter (BoE SWP 1019, 2023).

## 6a — La carrera de caballos del COVID (`covid_cross.py`)

Extiende Barro–Bianchi (2023): ¿ordena mejor la inflación acumulada 2020–23 el impulso fiscal o el
crecimiento de la M amplia? Datos verificados (jul-2026): inflación (Eurostat/OCDE/BM), impulso
fiscal (IMF Fiscal Monitor Oct-2021), M amplia (FRED, solo países con moneda propia).

**El diseño clave — la eurozona como experimento de política monetaria constante.** La carrera de
caballos en el pool de 19 países está confundida: mezcla regímenes monetarios distintos y outliers
(Polonia, shock energético de Europa del Este). El test limpio usa la eurozona: 7 países con LA
MISMA M3 y el mismo BCE, así que la política monetaria es constante por construcción y cualquier
variación de inflación entre ellos no puede ser de cantidad de dinero.

**Resultados (v1, con la variable de Barro-Bianchi = gasto / (deuda/PIB 2019 × duración 2019)):**
- **Panel A — dentro del euro (misma M3, n=7): inflación ~ fiscal-BB → R² = 0,77 (r = +0,88).**
  Con el dinero literalmente constante, el fiscal explica el 77% de la varianza de la inflación.
  Alemania y P. Bajos (fiscal-BB alto) arriba; Portugal, Francia, España (bajo) abajo.
- Panel B — fuera del euro (n=7): inflación ~ M amplia → R² = 0,43. La M amplia correlaciona, pero
  no dice nada del euro (donde es constante).
- Pool completo (n=19): fiscal crudo R² = 0,00; fiscal Barro-Bianchi R² = 0,11. El ruido
  cross-country es grande (como en el propio Barro-Bianchi), por mezclar regímenes monetarios.

**Progresión honesta reportada** (fiscal sobre inflación, pool de 19): crudo R²=0,00 → escalado por
deuda R²=0,03 → Barro-Bianchi completo R²=0,11. La variable escalada arregla los casos clave (Japón:
gasto alto pero deuda 206% PIB → shock real pequeño → inflación 5,6%, coherente) y no es post-hoc:
es la variable teóricamente correcta de la FTPL, publicada antes. Pero el resultado que manda es el
del control monetario (eurozona), no el del pool.

**Caveats de datos**: la duración/ATM no es perfectamente homogénea entre países (letras incl./excl.,
ajuste por swaps); Suiza (10,7) no pudo reverificarse (servidor EFV bloquea). Detalle en la cabecera
de `data/censo/covid_cross.csv`.
