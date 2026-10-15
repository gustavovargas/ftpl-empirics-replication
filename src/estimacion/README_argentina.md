# Caso-objeción: Argentina kirchnerista (2003-2015) — `argentina.py`

**La objeción** (de un interlocutor cuantitativista): el superávit gemelo del kirchnerismo convivió
con inflación porque *se emitía para comprar dólares y sostener un tipo de cambio competitivo; se
inunda la plaza de pesos y se va al dólar y a bienes*. Mecánica correcta (trilema de Mundell:
intervención cambiaria no esterilizada = emisión). La cuestión es si eso salva a la teoría
cuantitativa o si el mismo hecho es mejor explicado por la demanda de dinero / el respaldo.

## Los dos hechos que reinterpretan la objeción

**1. El desacople dinero/precios (Panel A).** M2 creció de forma bastante estable (~25-40%
interanual) durante todo el periodo, sin tendencia clara. La inflación corregida, en cambio, se
aceleró de ~6% (2004) a ~38% (2014). La misma emisión (~30% M2) dio 6% de inflación en 2004 y 38%
en 2014. Si la cantidad de dinero gobernara los precios con velocidad estable, ~30% de M debería
dar una inflación parecida siempre. No la dio → lo que cambió fue la **demanda** de dinero.

**2. La secuencia temporal (Panel B).** La fase de MÁXIMA compra de dólares (2003-2011, reservas de
9.000 a 50.000 M USD) fue la de MENOR inflación; la inflación se disparó cuando el respaldo se
deterioró y las reservas se DRENARON hacia fines fiscales (2011-2015, pago de deuda con reservas,
cepo). La objeción predice lo contrario: más compra de dólares → más inflación.

## La lectura de la teoría del respaldo

- Comprar dólares emite pesos **contra un activo de calidad** (reservas). Eso, en la teoría del
  respaldo, *estabiliza* el peso — es lo opuesto a monetizar déficit. La emisión cambiaria de
  2003-07 fue absorbida por una demanda de pesos que se recuperaba tras el colapso de 2001
  (**remonetización**), con el respaldo (reservas) creciendo.
- La inflación llegó cuando (a) el superávit fiscal se volvió déficit, (b) las reservas se drenaron
  hacia el Tesoro, (c) se destruyó la credibilidad (INDEC 2007, nacionalización de AFJP 2008, YPF
  2012, cepo 2011). La demanda de pesos cayó (**desmonetización**) y la misma emisión se tradujo en
  inflación creciente.
- "Emitir para mantener el peso barato" es, además, un subsidio a exportadores financiado con
  señoreaje: política cuasi-fiscal. La objeción monetarista y la lectura fiscal describen el mismo
  hecho; la diferencia es qué variable manda — la cantidad (que fue estable) o el respaldo/demanda
  (que colapsó).
- El test de la **esterilización** lo refuerza: el BCRA reabsorbió pesos con LEBAC a mansalva
  (contrayendo M) y la inflación no cedió — porque esterilizar solo cambia la composición del
  pasivo, no mejora el respaldo.

## Matiz de rigor (confesado)

Parte del desacople de 2004 se explica por el **crecimiento del PIB real** (~9% en el rebote
post-crisis absorbía más dinero; en 2014 el PIB estaba estancado). Es decir, la "demanda de dinero"
incluye el efecto renta, no solo la confianza. Pero el ajuste por PIB real refina, no revierte: con
crecimiento nulo en 2014 y M2 +30%, la inflación de 38% implica velocidad al alza; con +9% en 2004 y
M2 +40%, la inflación de 6% implica velocidad a la baja. El giro de la velocidad es el hecho central.

## Calidad de los datos

- Inflación: la oficial (INDEC) está falsificada 2007-2015. Serie corregida empalmada de fuentes
  creíbles (INDEC≤2006, Santa Fe, IPC Congreso, CABA) — ver `data/manual/argentina_inflacion*`.
  Fuentes heterogéneas y con discrepancias entre sí; la cifra anual es incierta, la tendencia no.
- M2 y reservas: FRED (`MYAGM2ARM189N`, `TRESEGARM052N`), limpios.

## Uso en el paper

Encaja en la **sección de concesiones** como el caso-objeción más difícil (superávit + inflación),
tratado con honestidad. Contraste natural: Milei 2023- (superávit estructural y creíble →
desinflación), ya en el censo. Mismo país, resultado opuesto según la credibilidad del respaldo.
