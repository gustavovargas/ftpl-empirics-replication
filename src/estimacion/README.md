# Test 1 — ¿a qué fecha obedecen los precios? (Bai-Perron)

Sección 4 del paper (el núcleo). Detección **endógena** de rupturas estructurales sobre la
inflación mensual y el crecimiento monetario mensual de cada episodio con datos mensuales
(c01 Austria, e04-e08, c03 Hungría), por separado, **sin informar al algoritmo de la fecha de la reforma**. Después se mide
la distancia (en meses) de cada ruptura respecto a la reforma fiscal.

## Método

- **Serie**: tasa de variación mensual (log-diferencia) del índice de precios y del agregado
  monetario. Un cambio de régimen inflacionario es un cambio en la **media y la varianza** de esta
  tasa, así que se usa el coste `rbf` (kernel) que capta ambos.
- **Ruptura dominante**: `ruptures.Dynp(model="rbf", n_bkps=1)` — programación dinámica exacta, la
  versión moderna del estimador de Bai-Perron para una sola ruptura óptima. Es el titular.
- **Robustez**: rupturas múltiples con PELT penalizado (líneas tenues en las figuras por episodio)
  y Zivot-Andrews como estimador de ruptura endógena alternativo (implementado; ver tabla).
- **Ejecutar**: `.venv/bin/python src/estimacion/rupturas.py` → `out/` (figura por episodio +
  `rupturas_resumen.png` + `rupturas_resumen.csv`).

## Resultados (v2) — Test 1: `out/rupturas_resumen.png`

v2 añade **Austria 1922 y Hungría 1924** (censo #1 y #3), los dos casos de Sargent que faltaban,
digitalizados de las tablas A2-A4 y H2-H3 del propio Sargent (1982) en
`data/manual/austria_1922.csv` y `hungria_1924.csv` (ver notas de fuente/erratas en las cabeceras).

v3 añade los éxitos duraderos modernos con datos accesibles sin API key: **México 1987** (Pacto,
FRED/OCDE), **Perú 1990** (Fujishock, BCRPData — sin serie monetaria mensual pre-1992) y **Turquía
2001** (Derviş, FRED/OCDE); y un grupo intermedio de **graduales/temporales/en curso**: Chile 1975,
Rusia 1995 y **Argentina 2023** (IPC de datos.gob.ar + base monetaria del BCRA v4). Fetchers nuevos
en `src/utils.py` (`fetch_bcrp`, `fetch_bcra`, `fetch_datosgobar`).

| Episodio | Reforma | Precios (Bai-Perron) | dist. | Precios (Zivot-Andrews) | dist. | Dinero | dist. |
|---|---|---|---|---|---|---|---|
| c01 Austria 1922 | 1922-10 | **1922-10** | **0** | **1922-10** | **0** | 1923-01 | +3 |
| e04 Alemania 1923 | 1923-11 | 1924-01 | +3 | 1923-12 | +2 | 1923-12 | +2 |
| c03 Hungría 1924 | 1924-03 | 1924-04 | +1 | **1924-03** | **0** | 1924-11 | +8 |
| c07 Bélgica 1926 | 1926-07 | 1926-10 | +3 | **1926-08** | **+1** | (sin serie) | — |
| e06 Francia 1926 | 1926-07 | 1927-01 | +5 | **1926-08** | **0** | (cambio) | +5 |
| c34 Japón 1931 (reflación) | 1931-12 | 1934-01 | +25* | **1931-11** | **−1** | 1932-08 | +8 |
| e07 EE.UU. 1933 | 1933-04 | 1933-03 | −1 | 1933-03 | −1 | 1933-05 | +1 |
| e08 Israel 1985 | 1985-07 | 1985-11 | +4 | **1985-08** | **+1** | 1986-05 | +10 |
| c11 Bolivia 1985 | 1985-08 | **1985-10** | **+1** | 1984-12 | −9* | (sin serie) | — |
| c23 México 1987 | 1987-12 | 1988-04 | +4 | 1988-02 | +2 | 1988-04 | +4 |
| c25 Polonia 1990 | 1990-01 | 1991-04 | +15* | 1989-04 | −9* | (sin serie) | — |
| c22 Perú 1990 | 1990-08 | **1990-09** | **+1** | 1990-10 | +2 | (sin serie) | — |
| e05 Brasil 1994 | 1994-07 | **1994-07** | **0** | **1994-07** | **0** | 1995-01 | +6 |
| c27 Bulgaria 1997 | 1997-07 | 1997-10 | +3 | **1997-04** | **−3** | (sin serie) | — |
| c30 Turquía 2001 | 2001-04 | 2002-02 | +10 | 2002-02 | +10 | 2000-02 | −14 |

**Titulares (n=15):**

- *Polonia-Balcerowicz 1990 (IPC del IFS, completo desde 1988): el caso gradual gemelo de
  Turquía — tres regímenes en la ventana (liberalización ago-1989, brote hiperinflacionario,
  desinflación de dos años: 586%% anual en 1990, 70%% en 1991) y los detectores de ruptura única
  aterrizan en los bordes del régimen central (+15/−9). Durabilidad: 23,9%%/mes → 5,2 al año
  (ratio 0,22). Nicaragua-Lacayo 1991 (censo #33) queda en fuente impresa pendiente: el IFS tiene
  hueco feb-1988/dic-1993 y el BCN online no llega atrás; Hanke-Krus fecha el pico (261%%/mes) en
  el propio mes del plan.
- *Bélgica (digitalizada de las tablas mensuales del Federal Reserve Bulletin en FRASER, con los
  solapes entre números validados idénticos, a `data/manual/belgica_1926.csv`): el gemelo de
  Francia. Re-fechada en el censo a jul-1926 (plenos poderes Jaspar-Francqui, 16-jul) por simetría
  con el criterio francés. BP da +3 (¡octubre: la estabilización de iure!) y ZA +1 (agosto, tras
  los plenos poderes): los dos detectores acotan las fechas de facto y de iure. Durabilidad
  5,5%/mes → 0,0 (ratio 0,00). Hegedüs (censo #2) queda CERRADO como inexistente-mensual: el
  índice húngaro empieza en jul-1921, con el intento ya muerto.
- *Bulgaria (IPC del IFS vía DBnomics, `fetch_dbnomics` nuevo en utils): ZA fecha la ruptura en
  abr-1997, TRES MESES ANTES de la entrada en vigor legal de la caja de conversión (1-jul): los
  precios giraron con el anuncio del acuerdo FMI/gobierno interino de feb-mar — el patrón de
  Austria. Durabilidad: 4,7%/mes pre → −0,3 al año (deflación), ratio −0,06.
- *Japón-Takahashi (dataset mensual de Shibamoto & Shizume 2014/Univ. de Kobe, en `data/raw/`):
  la segunda reflación del censo. ZA fecha la ruptura de precios en nov-1931, un mes ANTES de que
  Takahashi asuma y saque al yen del oro (13-dic-1931) — anticipación del mercado tras la salida
  británica del oro en sep-1931, el hallazgo de los propios Shibamoto-Shizume. El M1 rompe a +8
  (la ley de suscripción directa del BoJ es de jun-1932, ejecutada desde nov-1932). El +25 de
  Bai-Perron fecha el FINAL del brote reflacionista (ene-1934): la serie tiene tres regímenes
  (deflación / reflación / aterrizaje deliberado de Takahashi) y el detector de ruptura única
  elige el segundo corte; el multi-break (PELT) marca ambos.
- La ruptura de precios cae a una **mediana de 1 mes** de la reforma tanto con Bai-Perron como
  con Zivot-Andrews; ZA queda dentro de ±2 meses en 9 de 11.
- *Bolivia (digitalizada de la Tabla 1c de Sachs, NBER WP 2073, a `data/manual/bolivia_1985.csv`):
  Bai-Perron clava +1 (oct-1985; el +56,5%% de sep es arrastre del promedio — los precios dejan de
  subir el 9-sep, nota del propio Sachs); ZA en cambio se engancha a la ACELERACIÓN de dic-1984,
  como en Rusia: es el modo de fallo conocido del estimador en hiperinflaciones con rampa. Sin
  serie monetaria mensual en la fuente. Durabilidad de libro: 40,7%%/mes pre → 1,4 al año (0,03).
- La ruptura del **dinero** llega después de la de precios (o el mismo mes) en **6 de 9** episodios
  con serie monetaria (Austria +3, Hungría +8, Brasil +6, Israel +10, EE.UU. +1, México 0);
  excepciones: Alemania (−1 mes), Turquía y Japón (BP).
- **Turquía 2001 es el caso flojo y hay que contarlo así**: la flotación de feb-2001 dispara la
  inflación durante 2001 y la desinflación solo consolida en 2002 (+10 desde el anuncio de abril); su ruptura de dinero (−14)
  es el crawling peg del programa ANTERIOR (2000). Desinflación genuinamente gradual (ratio de
  asentamiento 0,94 — con pre de solo 2,8%/mes, el ratio es ruidoso; en niveles, 2,6%/mes al año), más parecida a Chile 1975 que a Austria 1922.
- **Austria es el caso de libro**: precios rompen en el mes exacto de los protocolos de la SdN
  (oct-1922) y el **tipo de cambio rompe un mes ANTES** (sep-1922), cuando llega la noticia de la
  intervención de la Sociedad de Naciones — la "estabilización por noticia" que narra Sargent,
  detectada endógenamente.
- **Zivot-Andrews resuelve el caso flojo de Francia**: donde Bai-Perron (single-break rbf) situaba
  la ruptura un trimestre tarde (por confundir la deflación de H2-1926 con la estabilización), ZA
  la clava en agosto-1926, justo tras la vuelta de Poincaré. También afina Israel (+1 vs +4).

## Resultados — grupo intermedio: graduales, temporales y en curso (`out/rupturas_temporales.csv`)

| Episodio | Censo | Ruptura precios (BP/ZA) | pre | al año | ratio |
|---|---|---|---|---|---|
| Polonia 1924 (Grabski) | exito_temporal | (−15 / −7)* | 64,2%/mes | s.d. | s.d. |
| **Italia 1947 (Einaudi)** | exito (ancla monetaria) | **0 / 0** | 7,1%/mes | −0,4 | −0,06 |
| **Ecuador 2000 (dolarización)** | exito (ancla monetaria) | +16 / +13 | 3,6%/mes | 2,6 | 0,72 |
| Zimbabue 2009 (dolarización) | exito | (0 / +2)* | 1.029%/mes | 0,6 | 0,00 |
| Chile 1975 (Cauas) | exito_gradual | +18 / +14 | 14,2%/mes | 9,8 | 0,69 |
| Argentina 1985 (Austral) | exito_temporal | **+1 / +1** | 20,0 | 4,0 | 0,20 |
| Argentina 1991 (Convertibilidad) | exito_temporal | +13 / +2 | 7,1 | 1,8 | 0,26 |
| Rusia 1995 (corredor) | exito_temporal | **0** / −17 | 8,4 | 1,9 | 0,22 |
| **Argentina 2023 (Milei)** | exito_en_curso | +9 / +5 | 9,9 | 3,0 | **0,31** |

Los planes argentinos usan el IPC de Mendoza (DEIE, vía datos.gob.ar, mensual desde 1970): la
serie larga accesible tras la desaparición del histórico GBA del INDEC de la web, validada contra
los valores conocidos del INDEC en los meses de los planes. Sin agregado monetario mensual
accesible pre-1996. OJO interpretativo: el Austral pasa el test de timing (+1) y el de durabilidad
a 12 meses (0,20) — su fracaso es de 1987-88, cuando el ancla fiscal se disolvió; la ventana de
un año no captura deshielos lentos, y así hay que contarlo.

- **Argentina 2023, el caso en tiempo real del paper**: la propia reforma incluye una devaluación
  que dispara la inflación a +25% en dic-2023 (el "Fujishock" de Milei), así que la ruptura de
  precios detectada cae cuando la desinflación consolida (mediados de 2024). La base monetaria no
  rompe hasta sep-2025 (+21): desinflación de ~10%/mes a ~2-3%/mes con la base creciendo — otra
  remonetización. Ancla fiscal explícita (superávit financiero desde ene-2024).
- Chile 1975 y Rusia 1995 son desinflaciones graduales/frágiles: el test de ruptura único les
  sienta mal (Rusia tiene varios regímenes 1993-98 y ZA se va a la desinflación fallida de 1994),
  y se reportan aquí por honestidad, no en la tabla principal.
- **Italia-Einaudi 1947, EL CASO ADVERSARIAL del censo** (digitalizada del FRB Bulletin/FRASER
  a `data/manual/italia_1947.csv`, última revisión entre números): estabilización DURADERA cuya
  ruptura (0/0, oct-1947) cae sobre una medida MONETARIA — el encaje obligatorio de Einaudi
  efectivo el 30-sep-1947 — con comp_fiscal=1 en el censo. El contexto de respaldo (gobierno De
  Gasperi sin PCI desde may-1947, anuncio del Plan Marshall jun-1947, consolidación Pella 1948)
  acompaña pero no lidera el timing. Es la mejor carta del lado monetarista dentro del censo y el
  paper debe citarla como tal. Hungría-forint 1946 (censo #8) queda pendiente por fuente de pago
  (Bomberger-Makinen 1983; Siklos 1991); KSH solo publica anual.
- Ecuador 2000 (IPC del IFS): el segundo caso de ancla monetaria del censo, y el espejo de
  Bolivia: la reforma monetaria más pura (dolarización, renuncia permanente a la imprenta)
  produjo la desinflación MÁS LENTA del censo — ruptura a +16/+13 y 2,5%/mes de inflación un año
  después del anuncio (la convergencia a un dígito anual tardó hasta 2002-03). Bolivia, con ancla
  fiscal y sin reforma monetaria alguna, paró los precios en once días. El contraste es un
  resultado en sí mismo.
- Zimbabue 2009 (pre digitalizado de la Tabla 1 de Hanke-Kwok, Cato Journal 29(2), a
  `data/manual/zimbabue_2009.csv`; post del IFS; dic-2008 sin dato — la guarda anti-huecos
  descarta la log-dif a través del hueco): el caso límite del censo — los precios pararon cuando
  LA MONEDA MISMA murió (la RBZ cerró la bolsa el 20-nov-2008 y la economía se dolarizó
  espontáneamente en semanas), antes de que hubiera reforma formal que fechar (GNU y presupuesto
  de caja: feb-2009, criterio Francia/Bélgica). El timing detectado (0/+2) coincide con el hueco
  de medición y NO es evidencia; la durabilidad sí: mediana pre ~1.029%%/mes (log) → 0,6 al año
  (ratio 0,00), con el régimen fiscal de caja sosteniéndola después.
- Yugoslavia-Avramović 1994 (Tabla 1 de Bogetic-Dragutinovic-Petrovic, Panoeconomicus 2022, a
  `data/manual/yugoslavia_1994.csv`): ruptura a +1 del programa (24-ene-1994) y la durabilidad
  más extrema del censo: mediana pre de 299%/mes → 1,4 al año (ratio 0,005). La serie termina en
  dic-1994 (ventana post de 11 meses); feb-1994 sobreestima por arrastre (los precios paran en
  UNA semana según los datos semanales de la fuente). exito_temporal: el programa se erosiona
  desde finales de 1995.
- Ucrania-Kuchma 1994 (IPC del IFS, validado dígito a dígito contra la tabla de Ukrstat): el caso
  que la métrica de durabilidad LEE MAL a sabiendas (ratio 1,10) — la inflación pre-Kuchma de
  1994 estaba comprimida por controles administrativos y el programa de oct-1994 liberalizó
  precios (salto oct-nov) antes de estabilizar; la desinflación es real pero gradual (1996: un
  dígito mensual; grivna sep-1996). Ventana sin el one-off de ene-1992 ni la crisis de ago-1998.
- *Polonia 1924 (digitalizada de las tablas P2-P4 de Sargent a `data/manual/polonia_1924.csv`):
  el índice de precios TERMINA en abr-1924, 3 meses después de la reforma Grabski (la base
  estadística murió con el marco polaco), así que el detector de ruptura única no puede fechar un
  régimen pegado al borde de la ventana y la durabilidad a 12 meses no es calculable (s.d.). La
  señal limpia es el TIPO DE CAMBIO, que sí continúa: ruptura detectada a **+1 mes** (feb-1924),
  el patrón de Austria. La inflación pasa de 64%/mes (mediana pre) a −1,3% en el trimestre
  post-reforma, con los billetes multiplicándose ×3,2 en 1924 (validación del empalme
  marcos→złoty en el propio texto de Sargent, p. 72). Erratas del libro documentadas en el CSV
  (fila dic-1920 duplicada; jun-1924 del cambio impreso 10,29 por 19,29).
- Hungría-Hegedüs 1921 (censo #2): NO testeable — las tablas de Sargent empiezan en jul-1921 y
  el intento es de ago-1921: sin ventana pre. Bélgica-Francqui 1926 (censo #7): sin serie mensual
  digitalizada accesible (pendiente de digitalización de boletines SdN / BNB histórico).

## Resultados — Test 1-placebo: los planes brasileños sin ancla fiscal (`out/rupturas_placebos.csv`, `out/rupturas_durabilidad.png`)

Extensión del censo (filas 17-20): Cruzado 1986, Bresser 1987, Verão 1989 y Collor 1990 — los
cuatro planes brasileños con congelación/moneda nueva pero **sin ancla fiscal** (datos: IPCA
SGS 433 y M1 SGS 1824 empalmado a reales a través de las 5 monedas; ver `series.py`).

v2 añade el **Plan Primavera argentino** (censo #14, IPC Mendoza): el peor fracaso de la tabla
(asentamiento 27%/mes a +10, ratio 1,90 — desemboca en la hiperinflación de 1989).

**El hallazgo — las rupturas existen pero se deshacen.** Zivot-Andrews detecta la ruptura de
precios en el mes del plan en 3/4 brasileños (Bresser +1, Verão +1, Collor +1): los precios *obedecen al
decreto* en el impacto, igual que en las reformas de verdad. La diferencia es la **durabilidad**,
medida con tres estadísticos de la inflación mensual (`rupturas_durabilidad.csv`): mediana pre
[−6,−1], mínimo del congelamiento [0,+6], y mediana de *asentamiento* en los últimos 6 meses de la
ventana de un año (capada al plan siguiente — Brasil encadenó un plan cada 14-19 meses):

| Plan | pre | congelación | al año | ratio |
|---|---|---|---|---|
| Cruzado 1986 | 12,2%/mes | 0,8 | 8,2 | 0,67 |
| Bresser 1987 | 13,8 | 4,8 | 16,8 | 1,22 |
| Verão 1989 | 23,5 | 6,6 | 36,3 | 1,54 |
| Collor 1990 | 40,3 | 7,3 | 13,4 (cap +9, Collor II) | 0,33 |
| *Éxitos duraderos (n=9)* | 1,6-194 | — | **−0,6 a 7,4** | **mediana 0,06** |

Mediana del ratio asentamiento/pre: **1,22 en los fracasos (n=5) vs. 0,06 en los éxitos
duraderos (n=9)**, con el grupo gradual/temporal/en curso en 0,26 (n=5). En niveles:
ningún plan sin ancla fiscal dejó la inflación por debajo del 8%/mes al año; ninguna reforma con
ancla fiscal la dejó por encima del 2,3%/mes.

**Las dos piezas incómodas para la TC**: (1) en el Cruzado el M1 *se multiplica* (+48% en un mes)
durante el congelamiento y la inflación igualmente vuelve — remonetización sin respaldo; (2) en
Collor, la contracción de liquidez más brutal del censo (confiscación de ~2/3 de los activos
financieros; ojo: drena los agregados amplios — el M1 medido sube ×2,2 por la conversión parcial)
no evita que la inflación esté en 13%/mes al año. Ni dinero disparado con precios quietos, ni
dinero confiscado con precios quietos: la cantidad no es la que manda.

## Resultados — Test 2: `out/event_study.png`

Event study de panel (7 desinflaciones con serie monetaria mensual — Austria 1922, Alemania 1923,
Hungría 1924, Israel 1985, México 1987, Brasil 1994, Turquía 2001 — alineadas en la reforma=100):
- Saldos reales M/P medios: 112 (t−12) → 84 (t−1, mínimo: la víspera) → 100 (t=0) → 153 (t+6)
  → **188 (t+12)**.
- Es decir, los saldos reales se **multiplican por 1,9** en el año posterior a la reforma mientras
  la inflación se desploma. Predicción de la TC estricta: frenar los precios exige frenar el
  dinero → saldos reales planos o a la baja. Observado: lo contrario (remonetización).

## Interpretación (neutral)

- **Contra la TC estricta**: si los precios siguieran a la cantidad de dinero, la ruptura de
  precios debería coincidir con —o seguir a— una ruptura del dinero. Ocurre lo contrario: los
  precios rompen con la reforma fiscal y el dinero rompe después.
- **A favor de la FTPL**: la fecha que ancla la ruptura de precios es la del cambio de régimen
  fiscal, no la monetaria.
- **Limitaciones confesadas**:
  1. n=5. Este test se generaliza en el paper al censo completo (los ~15 episodios con datos
     mensuales localizables).
  2. Francia es el caso más flojo: la ruptura dominante de precios llega un trimestre tarde
     (ene-1927), porque la deflación de H2-1926 y la estabilización posterior son dos regímenes;
     el multi-break (PELT) sí marca el giro de jul-1926, y el tipo de cambio corrobora. No hay
     serie monetaria mensual francesa fiable en FRED (pendiente: circulación del Banco de Francia).
  3. La reforma y el cambio monetario a veces distan pocas semanas (Alemania): con datos mensuales
     no siempre se pueden separar. Los casos limpios (Brasil, EE.UU., Israel) llevan la carga.

## Sección 7 — La reversión a la media de la velocidad, testada (`velocidad.py`)

Ataca la cláusula de defensa del dinero amplio: "la demanda de dinero varía pero revierte a la
media". Si eso fuera cierto, la velocidad (inversa de la demanda) sería estacionaria alrededor de
una media constante. Batería de tests sobre la velocidad de M2 (FRED `M2V`, trimestral 1959-2025):

| Test | Resultado | Lectura |
|---|---|---|
| ADF (H0 = raíz unitaria) | p = 0,77 | NO rechaza → **no** estacionaria |
| Zivot-Andrews (raíz unitaria + 1 ruptura) | p = 0,51 | NO rechaza ni permitiendo una ruptura |
| Semivida de reversión AR(1) | **77 años** | reversión inexistente en horizontes de política |
| Bai-Perron sobre el nivel | medias 1,77 → 2,12 → 1,96 → 1,63 → 1,35 | la "media" salta a regímenes distintos |

**Robustez con Divisia M4** (el agregado amplio que prefiere la escuela del dinero amplio):
ADF p = 0,21 (tampoco rechaza la raíz unitaria), semivida 10 años. El resultado no depende del
agregado.

**Conclusión**: "reversión a la media" exige una media fija, y no la hay — la velocidad es (o se
comporta como) un proceso con raíz unitaria cuya media salta en fechas identificables. Una media
que hay que reestimar tras cada ruptura no es un ancla, es un ajuste ex post. Es la formalización
del episodio e01. `out/velocidad.png`.
