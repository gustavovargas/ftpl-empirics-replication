# -*- coding: utf-8 -*-
"""Genera informe/index.html: autocontenido (PNGs en base64), recogiendo automáticamente
los episodios de episodios/eXX_*/ que tengan PNG en out/ y notas.md."""
import base64
import glob
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EPISODIOS = os.path.join(RAIZ, "episodios")
SALIDA = os.path.join(RAIZ, "informe", "index.html")

CABECERA = """<!-- generado por informe/build.py — no editar a mano -->
<meta charset="utf-8">
<title>¿Dónde falla la teoría cuantitativa? Episodios para el debate TC vs. FTPL</title>
<style>
  body { font-family: Georgia, 'Times New Roman', serif; max-width: 980px; margin: 2rem auto;
         padding: 0 1rem; line-height: 1.55; color: #222; }
  h1 { font-size: 1.7rem; } h2 { font-size: 1.25rem; margin-top: 2.2rem; border-bottom: 2px solid #ddd; padding-bottom: .3rem; }
  img { max-width: 100%; border: 1px solid #e0e0e0; margin: .8rem 0; }
  .intro, .sintesis { background: #f7f5f0; padding: 1rem 1.2rem; border-left: 4px solid #b8860b; }
  .notas { font-size: .95rem; }
  .notas h1 { display: none; } .notas h2 { font-size: 1.02rem; border: none; margin-top: 1.1rem; }
  code { background: #f0f0f0; padding: 0 4px; font-size: .85em; }
  blockquote { color: #555; border-left: 3px solid #ccc; margin-left: 0; padding-left: 1rem; }
  footer { margin-top: 3rem; font-size: .85rem; color: #777; border-top: 1px solid #ddd; padding-top: .8rem; }
</style>
"""

INTRO = """
<h1>¿Dónde falla la teoría cuantitativa? Episodios para el debate TC&nbsp;vs.&nbsp;FTPL</h1>
<div class="intro">
<p><strong>El debate.</strong> La teoría cuantitativa (TC) sostiene que el nivel de precios lo
gobierna la cantidad de dinero. Frente a los contraejemplos, sus defensores modernos (la escuela
del dinero amplio) añaden dos cláusulas: (1)&nbsp;la demanda de dinero varía pero <em>revierte a la
media</em>, y (2)&nbsp;hay que medir con <em>agregados amplios</em> (M3/M4). La teoría fiscal del
nivel de precios (FTPL) responde que el dinero fiat es un pasivo del Estado consolidado y su valor
depende del <em>respaldo fiscal esperado</em>: la cantidad importa solo en relación con lo que la
respalda.</p>
<p><strong>El método.</strong> Cada episodio compara de forma neutral qué predice cada teoría
(incluidas las dos cláusulas) con lo observado, y concede explícitamente lo que cada una explica
bien. Los gráficos se generan con scripts reproducibles (<code>episodios/eXX_*/make.py</code>)
desde fuentes públicas (FRED, CFS, Sargent 1982).</p>
</div>
"""

SINTESIS = """
<h2>Síntesis</h2>
<div class="sintesis">
<p>Los episodios dibujan el mismo patrón. La TC funciona cuando la demanda de dinero es
estable y el shock es puramente monetario (EE.UU. 1959-1990, la subida de la hiperinflación
alemana, la Gran Contracción de 1929-33, el arranque de 2020-21). Falla —o solo se salva con
cláusulas ad&nbsp;hoc— exactamente donde el régimen fiscal cambia: la velocidad no revierte a
ninguna media (e01), el agregado "correcto" solo se conoce ex&nbsp;post (e02), la mayor
contracción de M2 desde 1933 no devolvió nada del nivel de precios (e03), la hiperinflación
alemana terminó en seco con la imprenta multiplicando por cuatro la circulación (e04), y en 1933
la misma lógica funcionó en dirección contraria: los precios arrancaron al alza con M2 clavada en
su mínimo, en cuanto FDR anunció déficits sin respaldo (e07). La FTPL explica todos los casos con una sola
variable —el respaldo fiscal esperado del dinero— sin necesidad de elegir agregado ni de postular
medias móviles. Brasil 1994 (e05) replica el patrón alemán setenta años después: remonetización
masiva tras un ancla fiscal creíble, sin inflación. Y Francia 1926 (e06) es el caso límite: giro de
precios y tipo de cambio fechable en un cambio de gobierno, <em>sin reforma monetaria alguna</em> y
con la emisión creciendo durante la desinflación. El coste de salvar la TC en estos episodios es
incorporar la solvencia esperada del emisor a la demanda de dinero: en ese momento deja de ser una
teoría de la <em>cantidad</em>.</p>
<p>Israel 1985 (e08) es la tercera repetición del patrón de remonetización (M1&nbsp;×7 con la
inflación desplomándose), y Somalia (e09) cierra el dossier con el caso límite ontológico: sin
emisor, el valor del dinero no lo ancló ninguna cantidad sino el coste de producir el billete.</p>
<p><strong>Posibles ampliaciones:</strong> Argentina 2024-25 (ajuste fiscal y desinflación en
curso), el <em>cross-section</em> COVID completo (Barro-Bianchi extendido) y el event study del
mini-budget británico de 2022.</p>
</div>
"""


# Los notas.md son material de trabajo y nombran a interlocutores concretos; el HTML
# se comparte y debe leerse como discusión de la teoría en general, no como réplica personal.
SANEAR = [
    ("Réplica esperable de Castañeda", "Réplica esperable de un cuantitativista"),
    ("El punto de Castañeda", "El punto de la escuela del dinero amplio"),
    ("versión Castañeda:", "versión moderna:"),
    ("y hay que reconocérselo a Castañeda de entrada", "y hay que reconocérselo de entrada"),
    ("Congdon y el IIMR lo predijeron", "Los monetaristas del dinero amplio lo predijeron"),
    ("que el IIMR y los monetaristas de M amplia advirtieron", "que los monetaristas de M amplia advirtieron"),
    ("los partidarios de la M amplia (Congdon) dijeron", "los partidarios de la M amplia dijeron"),
    ("(así lo advirtió el IIMR)", "(así lo advirtieron los monetaristas de M amplia)"),
    ("Castañeda", "un cuantitativista"),   # red de seguridad para menciones futuras
    ("Congdon", "la escuela del dinero amplio"),
    ("el IIMR", "la escuela del dinero amplio"),
    ("IIMR", "escuela del dinero amplio"),
]


def sanear(texto):
    for viejo, nuevo in SANEAR:
        texto = texto.replace(viejo, nuevo)
    return texto


def _inline(s):
    """Formato inline: negrita, cursiva y código."""
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def _unwrap(md):
    """Une las líneas de continuación (word-wrap) en una sola por párrafo/ítem, para que
    negritas y cursivas que cruzan un salto de línea se procesen correctamente."""
    def es_bloque(s):
        return (not s or re.match(r"^#{1,3} ", s) or re.match(r"^[-*] ", s)
                or re.match(r"^\d+\. ", s))
    out = []
    for linea in md.splitlines():
        s = linea.strip()
        if out and not es_bloque(s) and out[-1].strip() and not re.match(r"^#{1,3} ", out[-1].strip()):
            out[-1] = out[-1].rstrip() + " " + s
        else:
            out.append(linea)
    return out


def md_a_html(md):
    """Conversión mínima de Markdown a HTML (títulos, negrita, cursiva, listas, párrafos)."""
    html, en_lista = [], False
    for linea in _unwrap(md):
        l = linea.rstrip()
        if re.match(r"^#{1,3} ", l):
            n = len(l) - len(l.lstrip("#"))
            l = f"<h{n}>{_inline(l.lstrip('# '))}</h{n}>"
        elif re.match(r"^\s*[-*] ", l.strip()) or re.match(r"^\s*\d+\. ", l.strip()):
            item = re.sub(r"^\s*([-*]|\d+\.) ", "", l)
            l = ("<ul>" if not en_lista else "") + f"<li>{_inline(item)}</li>"
            en_lista = True
            html.append(l)
            continue
        elif not l.strip():
            l = "</ul><p>" if en_lista else "<p>"
            en_lista = False
        else:
            l = _inline(l)
        html.append(l)
    return "\n".join(html) + ("</ul>" if en_lista else "")


def _img(ruta):
    if not os.path.exists(ruta):
        return None
    with open(ruta, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def seccion_test1():
    """Sección de tests formales: embebe las figuras de rupturas y event study."""
    b1 = _img(os.path.join(RAIZ, "src", "estimacion", "out", "rupturas_resumen.png"))
    b2 = _img(os.path.join(RAIZ, "src", "estimacion", "out", "event_study.png"))
    if not b1 and not b2:
        return ""
    html = ["""
<h2>Del relato al test: dos pruebas formales</h2>
<p>Los episodios anteriores son narrativos. El paso siguiente es formalizarlos con dos tests
reproducibles sobre los episodios con datos mensuales.</p>
<h3>Test 1 — ¿a qué fecha obedecen los precios?</h3>
<p>Se detecta de forma <strong>endógena</strong> —Bai-Perron y Zivot-Andrews, sin decirle al
algoritmo dónde está la reforma— la ruptura estructural de la inflación y del crecimiento del
dinero, y se mide a qué distancia cae cada una de la reforma fiscal.</p>"""]
    if b1:
        html.append(f'<img src="data:image/png;base64,{b1}" alt="rupturas_resumen.png">')
    html.append("""<p>La ruptura de precios cae a una mediana de <strong>3 meses</strong> de la
reforma con Bai-Perron y de <strong>1 mes</strong> con Zivot-Andrews (las cinco dentro de ±2 meses);
la ruptura del dinero llega sistemáticamente después (Brasil +6, Israel +10), porque el dinero sigue
creciendo tras la estabilización. Si los precios siguieran a la cantidad de dinero, el orden sería el
inverso.</p>
<h3>Test 2 — el hecho de la remonetización</h3>
<p>Alineando los episodios en la reforma, los saldos reales (dinero/precios) tocan fondo en la
reforma y <strong>se multiplican por 2,2</strong> en el año siguiente, mientras la inflación se
desploma — lo contrario de lo que exigiría frenar los precios por la vía de la cantidad de dinero.</p>""")
    if b2:
        html.append(f'<img src="data:image/png;base64,{b2}" alt="event_study.png">')
    html.append("<p>Ambos tests están validados con n pequeño (los episodios con serie mensual "
                "cargada); el paper los extiende al censo. Detalle y limitaciones en "
                "<code>src/estimacion/README.md</code>.</p>")
    # Nivel B — Truss (alta frecuencia)
    b3 = _img(os.path.join(RAIZ, "src", "estimacion", "out", "truss_event_study.png"))
    if b3:
        html.append("""<h3>Test moderno — el "Poincaré" de 2022</h3>
<p>El experimento más limpio del dossier ocurrió en tiempo real. El 23 de septiembre de 2022 el
gobierno de Truss anunció ~45.000 millones de libras de recortes fiscales <strong>sin financiar</strong>,
mientras el Banco de Inglaterra <em>subía</em> tipos. Si lo que gobierna a la libra fuera la cantidad
de dinero, una política monetaria restrictiva debería fortalecerla.</p>""")
        html.append(f'<img src="data:image/png;base64,{b3}" alt="truss_event_study.png">')
        html.append("""<p>Ocurrió lo contrario: la libra cayó a un mínimo histórico y el coste real de
la deuda británica saltó <strong>+163 puntos básicos</strong> en cuatro sesiones — en la ventana del
anuncio fiscal, no de ninguna decisión monetaria. El mercado repreció el respaldo fiscal. El Banco de
Inglaterra tuvo que intervenir cinco días después con compras de emergencia.</p>""")
    # Nivel B — cross-section COVID
    b4 = _img(os.path.join(RAIZ, "src", "estimacion", "out", "covid_cross.png"))
    if b4:
        html.append("""<h3>Test moderno — la inflación del COVID y la eurozona</h3>
<p>El episodio EE.UU.-Japón (e03) sugería que, a igual crecimiento del dinero, la fiscalidad
separa las inflaciones. La eurozona lo convierte en un experimento casi de laboratorio: sus países
<strong>comparten la misma moneda y el mismo banco central</strong>, así que la política monetaria es
idéntica por construcción. Cualquier diferencia de inflación entre ellos no puede ser de cantidad de
dinero.</p>""")
        html.append(f'<img src="data:image/png;base64,{b4}" alt="covid_cross.png">')
        html.append("""<p>Y dentro del euro, la inflación 2020-2023 queda ordenada por el impulso
fiscal —escalado por la deuda y su duración, como en Barro-Bianchi (2023)— con un
<strong>R²&nbsp;=&nbsp;0,77</strong>: Alemania y Países Bajos arriba, Portugal y Francia abajo. Con el
dinero constante, manda el respaldo fiscal. Fuera del euro (panel B) el crecimiento del dinero también
correlaciona, pero no puede explicar la eurozona; y en el pool completo de países el ruido es grande,
como reconoce el propio Barro-Bianchi. La comparación honesta de todas las variantes está en
<code>src/estimacion/README_nivelB.md</code>.</p>""")
    # Sección 7 — reversión a la media de la velocidad
    b5 = _img(os.path.join(RAIZ, "src", "estimacion", "out", "velocidad.png"))
    if b5:
        html.append("""<h3>La otra defensa: ¿revierte la velocidad a su media?</h3>
<p>La escuela del dinero amplio concede que la velocidad del dinero varía, pero sostiene que
<em>revierte a una media</em> — de modo que la demanda de dinero seguiría siendo estable. Es una
afirmación contrastable: si fuese cierta, la velocidad sería estadísticamente estacionaria alrededor
de una media constante.</p>""")
        html.append(f'<img src="data:image/png;base64,{b5}" alt="velocidad.png">')
        html.append("""<p>No lo es. Los tests de raíz unitaria no rechazan que la velocidad de M2 sea
un paseo aleatorio (ADF p=0,78), ni siquiera permitiendo una ruptura (Zivot-Andrews p=0,53); la
semivida de reversión de un AR(1) es de <strong>83 años</strong>; y su media salta a niveles distintos
en cada régimen (1,77 → 2,12 → 1,96 → 1,63 → 1,35). El resultado se mantiene con la Divisia M4, el
agregado que esa escuela prefiere. "Reversión a la media" exige una media fija — y no la hay. Una media
que hay que reestimar tras cada ruptura no es un ancla, es un ajuste posterior.</p>""")
    # Caso-objeción — Argentina kirchnerista
    b6 = _img(os.path.join(RAIZ, "src", "estimacion", "out", "argentina.png"))
    if b6:
        html.append("""<h3>El caso más incómodo: superávit e inflación (Argentina, 2003-2015)</h3>
<p>La objeción más difícil a la teoría del respaldo es un país con superávit que aun así tiene
inflación. La Argentina kirchnerista lo tuvo, y con una explicación monetarista concreta: se emitía
para comprar dólares y sostener un peso barato, y ese exceso de pesos se iba al dólar y a los precios.
La mecánica es correcta; la cuestión es si explica lo observado.</p>""")
        html.append(f'<img src="data:image/png;base64,{b6}" alt="argentina.png">')
        html.append("""<p>Los datos dicen que no. La cantidad de dinero (M2) creció de forma bastante
estable (~30% anual) durante todo el periodo, mientras la inflación se aceleró de ~6% a ~38%: la misma
emisión, inflaciones muy distintas — lo que cambió fue la <em>demanda</em> de dinero. Y la fase de
<strong>máxima</strong> compra de dólares (2003-2011, reservas de 9.000 a 50.000 millones) fue la de
<strong>menor</strong> inflación; ésta se disparó cuando el superávit se volvió déficit y las reservas
se drenaron hacia el Tesoro. Comprar dólares emite pesos contra un activo de calidad (reservas): eso
estabiliza, hasta que ese activo se gasta. Es el mecanismo de la remonetización de los episodios
anteriores, al revés. (Matices de datos —la inflación oficial de esos años está falsificada— y de
método en <code>src/estimacion/README_argentina.md</code>.)</p>""")
    return "\n".join(html)


def main():
    partes = [CABECERA, INTRO]
    for ep in sorted(glob.glob(os.path.join(EPISODIOS, "e[0-9][0-9]_*"))):
        pngs = sorted(glob.glob(os.path.join(ep, "out", "*.png")))
        fnotas = os.path.join(ep, "notas.md")
        if not pngs or not os.path.exists(fnotas):
            continue
        with open(fnotas, encoding="utf-8") as f:
            notas = sanear(f.read())
        titulo = notas.splitlines()[0].lstrip("# ").strip()
        partes.append(f"<h2>{titulo}</h2>")
        for png in pngs:
            with open(png, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            partes.append(f'<img src="data:image/png;base64,{b64}" alt="{os.path.basename(png)}">')
        partes.append(f'<div class="notas">{md_a_html(notas)}</div>')
    partes.append(seccion_test1())
    partes.append(SINTESIS)
    partes.append("<footer>Proyecto <code>ftpl_empirics</code> — gráficos reproducibles con "
                  "<code>make.py</code> por episodio; datos: FRED, Center for Financial Stability, "
                  "Sargent (1982). Este archivo se regenera con <code>informe/build.py</code>.</footer>")
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(partes))
    print(f"OK -> {SALIDA} ({os.path.getsize(SALIDA)//1024} KB)")


if __name__ == "__main__":
    main()
