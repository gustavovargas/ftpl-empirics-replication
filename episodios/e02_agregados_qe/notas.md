# e02 — QE 2008-2019: ¿qué agregado monetario "explica" la inflación?

**Series**: FRED `BOGMBASE`, `M1SL`, `M2SL`, `CPIAUCSL` + Divisia M4 del Center for Financial
Stability (hoja Broad de `Divisia.xlsx`). Indexadas a dic. 2007 = 100, escala log.
**Gráfico**: `out/e02_agregados_qe.png`.

## Qué predice cada teoría

- **TC**: los precios siguen a "la cantidad de dinero". Entre 2007 y 2019: base ×4,1 (pico ×4,9),
  M1 ×2,9, M2 ×2,05, Divisia M4 ×1,45… y el IPC ×1,22. Cada agregado "predice" una inflación
  distinta; solo el más amplio queda cerca de lo observado.
- **FTPL / respaldo**: el QE es emisión de pasivos del banco central **contra activos** (deuda
  pública, MBS) en un contexto de demanda de liquidez disparada: no diluye el respaldo del dinero,
  así que no tiene por qué generar inflación, por grande que sea la cifra de emisión.

## Qué se observó

La base monetaria se multiplicó por casi cinco sin que la inflación se moviera del ~2%. Los
agregados intermedios (M1, M2) también se despegaron del IPC. Solo el Divisia M4 quedó
razonablemente cerca de la trayectoria de precios.

## Veredicto (neutral)

- **El punto de Castañeda es correcto en un sentido**: el agregado amplio se comportó mucho mejor
  que la base — de hecho el episodio 2008 es la razón de ser de su preferencia por M3/M4.
- **El problema es metodológico**: la elección del agregado se valida *ex post*. Si la base falla,
  se mira M2; si M2 falla, M4; si M4 falla (véase e03), se apela a la demanda de dinero. Una
  teoría con un grado de libertad en su variable central ("la cantidad de dinero... la que
  funcione") pierde capacidad de falsación. La TC no falla aquí estrepitosamente: se vuelve
  **inconcreta**.
- La FTPL da una razón *ex ante* de por qué esta emisión concreta no era inflacionista (compra de
  activos con demanda de liquidez alta), sin necesidad de elegir agregado.

## Réplica esperable de Castañeda

"No es ex post: los partidarios de la M amplia (Congdon) dijeron *en 2009* que no habría inflación
porque M3/M4 apenas crecía, y acertaron contra los que miraban la base." — Es verdad y hay que
concederlo. La respuesta está en e03: el mismo criterio (M2/M amplia) aplicado a 2020-2023 produce
predicciones erróneas en Japón y en la contracción de 2022-23, mientras que el criterio fiscal
discrimina bien ambos casos.
