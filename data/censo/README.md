# Censo de estabilizaciones — v0.2 (Tabla 1 del paper)

34 episodios (32 desinflaciones + 2 reflaciones: EE.UU. 1933 y Japón-Takahashi 1931), 1921-2025,
codificados por componentes del paquete. **v0.2 = 32 de 34 filas verificadas contra fuentes
primarias (jul-2026); quedan 2 en `confianza=media`: Hungría-Hegedüs (dating 1920-21 genuinamente
incierto en la literatura) y Argentina-Plan Primavera (pendiente).**

Cambios de v0.1 → v0.2 (verificación): Ucrania re-fechada a 1994-10, cambiaria 1→0 y resultado
degradado a éxito temporal (la desinflación precede a la grivna; recaída 1998-2000); Grabski
confirmado como fiscal fuerte (cierre de la línea de crédito al gobierno, feb-1924); Yugoslavia
duración 24→20 meses; Italia-Einaudi confirmado como caso de ancla NO primariamente fiscal;
añadida la reflación de Japón-Takahashi 1931 (Nanto & Takagi 1985, AER).

## Definiciones de codificación

- **fecha**: mes del anuncio/entrada en vigor del paquete principal (no de sus efectos).
- **tipo**: `desinflacion` | `reflacion` (el test debe funcionar en ambas direcciones).
- **comp_fiscal** (el tratamiento de interés):
  - `2` = ajuste fuerte o regla: recorte del déficit ≥3 pp del PIB en ~1 año, presupuesto
    equilibrado, o prohibición legal de financiación del gobierno por el banco central.
  - `1` = ajuste parcial, transitorio o solo prometido.
  - `0` = sin componente fiscal creíble.
- **comp_monetaria**: `1` = moneda nueva, reforma del banco central o tope/prohibición legal de
  emisión (nota: la moneda nueva *sin* regla — p. ej. cruzado — cuenta como 1 igualmente:
  interesa separar cosmética de fiscalidad).
- **comp_cambiaria**: `1` = ancla explícita (peg, banda, caja de conversión, dolarización).
- **comp_rentas**: `1` = congelación o pacto de precios y salarios.
- **resultado**:
  - `exito_duradero` = inflación por debajo de ~20% anual (o del 2%/mes) sostenida ≥5 años.
  - `exito_temporal` = ≥18 meses con inflación < ⅓ de la previa, con recaída posterior
    (`duracion_meses_apx` = duración del éxito).
  - `exito_gradual` = desinflación lograda pero lenta (>3 años) — se discute aparte.
  - `fracaso` = recaída en <18 meses.
  - `exito_en_curso` = episodio aún abierto.
- **datos_mensuales**: disponibilidad para los tests de rupturas (fred / nber / bcb / ocde /
  digitalizado / por_localizar).

## Predicciones a contrastar con esta tabla

1. **FTPL**: `comp_fiscal = 2` ≈ suficiente para el éxito; `comp_fiscal = 0` → fracaso aunque
   haya moneda nueva, ancla o congelación (Cruzado, Verão, Primavera).
2. **Los casos frontera** hacen el trabajo fino: Convertibilidad argentina y Rusia 1995 (regla
   monetaria dura con fiscal débil → éxito temporal que muere por la vía fiscal); Perú 1990 y
   Turquía 2001 (fiscal fuerte SIN ancla cambiaria → éxito); Collor (contracción monetaria
   brutal sin reforma fiscal → fracaso).
3. **Anomalías confesadas**: Chile 1975 (fiscal fuerte, desinflación lenta — indexación);
   Italia 1947 (peso fiscal discutido en la literatura).

## La objeción seria a esta tabla (confesarla en el paper)

**Riesgo de circularidad en la codificación**: la literatura tiende a describir como "ajuste
fiscal fuerte" los planes que triunfaron — el resultado puede contaminar la codificación del
tratamiento. Mitigación para v1.0: codificar `comp_fiscal` con **datos cuantitativos del déficit**
(variación del déficit primario/PIB en los 12 meses posteriores al plan, desde fuentes primarias:
FMI, Mitchell, anuarios), no con adjetivos de la literatura, y con umbral fijado ex ante (≥3 pp).
Los casos frontera (Convertibilidad, Rusia-95, Collor) son la mejor defensa: su codificación no es
discutible y llevan la carga discriminante.

## Pendiente para v1.0

- Verificar filas con confianza media/baja contra fuentes primarias (Végh 1992 y Calvo-Végh 1999
  tienen las fechas canónicas de los planes latinoamericanos).
- Completar `infl_previa` con la tasa exacta 12m antes del plan (para el event study).
- Localizar series mensuales (`por_localizar`) — candidatos: Global Financial Data (de pago),
  FMI IFS histórico, bancos centrales nacionales.
- Añadir 2-3 reflaciones más si las hay documentadas (¿Japón 1932, Takahashi? — candidato claro).
