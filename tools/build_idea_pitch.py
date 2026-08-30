#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_idea_pitch.py — renders ideas/idea-pool.md content as a readable pitch PDF
for Carmen. Data is inline (kept in sync with ideas/idea-pool.md by hand).

Usage: python tools/build_idea_pitch.py [out.pdf]
Default output: ideas/idea-pool.pdf (gitignored).
"""
import sys
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, KeepTogether, HRFlowable)

FONTS = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Body", FONTS + r"\georgia.ttf"))
pdfmetrics.registerFont(TTFont("Body-B", FONTS + r"\georgiab.ttf"))
pdfmetrics.registerFont(TTFont("Body-I", FONTS + r"\georgiai.ttf"))
pdfmetrics.registerFont(TTFont("Head", FONTS + r"\calibrib.ttf"))
pdfmetrics.registerFont(TTFont("Head-R", FONTS + r"\calibri.ttf"))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-B", italic="Body-I")

INK = colors.HexColor("#1a1a1a")
MUTE = colors.HexColor("#6b6b6b")
RULE = colors.HexColor("#c8c2b6")
CARD = colors.HexColor("#f5f2ec")
ACCENT = colors.HexColor("#7a1f1f")

S = {
    "title": ParagraphStyle("title", fontName="Head", fontSize=30, leading=34, textColor=INK),
    "subtitle": ParagraphStyle("subtitle", fontName="Body-I", fontSize=13, leading=18, textColor=MUTE),
    "h1": ParagraphStyle("h1", fontName="Head", fontSize=19, leading=23, textColor=ACCENT,
                         spaceBefore=6, spaceAfter=4),
    "h2": ParagraphStyle("h2", fontName="Head", fontSize=13.5, leading=17, textColor=INK, spaceAfter=2),
    "meta": ParagraphStyle("meta", fontName="Head-R", fontSize=8.5, leading=12, textColor=MUTE,
                           spaceAfter=4),
    "body": ParagraphStyle("body", fontName="Body", fontSize=10, leading=14.5, textColor=INK,
                           alignment=TA_LEFT, spaceAfter=3),
    "lead": ParagraphStyle("lead", fontName="Body", fontSize=10.5, leading=15.5, textColor=INK,
                           spaceAfter=6),
    "label": ParagraphStyle("label", fontName="Head", fontSize=8, leading=11, textColor=ACCENT,
                            spaceBefore=3),
    "hook": ParagraphStyle("hook", fontName="Body-B", fontSize=10, leading=14, textColor=INK),
    "hook2": ParagraphStyle("hook2", fontName="Body-I", fontSize=9.5, leading=13, textColor=MUTE),
    "cell": ParagraphStyle("cell", fontName="Body", fontSize=8.5, leading=11, textColor=INK),
    "cellh": ParagraphStyle("cellh", fontName="Head", fontSize=8.5, leading=11, textColor=colors.white),
    "foot": ParagraphStyle("foot", fontName="Head-R", fontSize=8, textColor=MUTE, alignment=TA_CENTER),
}


def P(t, s="body"):
    return Paragraph(t, S[s])


# ---- data (sync with ideas/idea-pool.md) ----------------------------------

T01 = [
    ("T01-01", "Coca-Cola", "aprobada", "A", "alto", 20,
     "La inventó un farmacéutico adicto a la morfina que intentaba curarse.",
     ["La CocaCola nació para curar una ADICCIÓN",
      "El farmacéutico ADICTO que inventó la CocaCola",
      "¿Qué había REALMENTE en la primera CocaCola?"],
     "El remedio de un hombre desesperado se vuelve el producto más reconocible del planeta; "
     "qué se borró de esa historia — la cocaína, Pemberton muriendo pobre, Asa Candler quedándose la marca.",
     "Separar el mito de marketing de lo documentado. Tratamiento sobrio con la adicción."),
    ("T01-02", "Nintendo", "aprobada", "A", "medio", 18,
     "80 años de fracasos — naipes, taxis, love hotels, una aspiradora — antes de los videojuegos.",
     ["La empresa que FRACASÓ en todo durante 80 años",
      "Antes de Mario: los taxis, los love hotels y la aspiradora de Nintendo",
      "¿CÓMO sobrevive una empresa a 80 años de malas ideas?"],
     "Persistencia institucional, reinvención, la siguiente apuesta. Para llevar: sobrevivir no es "
     "acertar siempre, es seguir en la mesa.",
     None),
    ("T01-03", "Disney / Mickey", "aprobada", "A / B", "medio", 18,
     "Le robaron su primer personaje (Oswald); Mickey nació de esa traición.",
     ["A Walt Disney le ROBARON su primer personaje",
      "Mickey Mouse nació de una TRAICIÓN",
      "El día que Disney lo perdió TODO en un tren"],
     "Su distribuidor se queda a Oswald y a casi todo su equipo; Mickey es la respuesta. "
     "Para llevar: lo que te quitan puede forzar lo que te define.",
     "Cero imágenes modernas de Disney (IP). Solo animación temprana y prensa de los años 20."),
    ("T01-04", "Adidas vs Puma", "aprobada", "A / C", "medio", 18,
     "Dos hermanos, una fábrica de zapatillas, un odio que partió un pueblo alemán en dos.",
     ["Dos hermanos, una fábrica de zapatillas y un ODIO que partió un pueblo",
      "¿POR QUÉ Adidas y Puma están en la MISMA calle, enfrentadas?",
      "La GUERRA familiar detrás de tus zapatillas"],
     "Cómo un rencor personal se institucionaliza y dura generaciones: el pueblo dividido, "
     "dos equipos de fútbol, no se casaban entre bandos.",
     "Trasfondo nazi de ambos hermanos — tratar con cuidado y fuente, sin lavarlo."),
    ("T01-05", "Ferrari", "aprobada", "A / B", "medio", 18,
     "La muerte de su hijo Dino y la obsesión que construyó el mito.",
     ["Enzo Ferrari construyó un IMPERIO por una sola razón: no perder",
      "La MUERTE que hay detrás de cada Ferrari",
      "¿POR QUÉ Enzo Ferrari ODIABA vender coches?"],
     "Obsesión y duelo: Dino muere en 1956; la fábrica de coches de calle existe para financiar "
     "la escudería. Para llevar: cuando el motor es una herida, cuidado con lo que construyes encima.",
     None),
    ("T01-06", "El bolígrafo (László Bíró)", "aprobada", "A / B", "medio", 18,
     "Un periodista húngaro huyendo de los nazis inventa el bolígrafo en Argentina.",
     ["El hombre que huyó de los NAZIS e inventó el bolígrafo",
      "¿POR QUÉ en media Latinoamérica el bolígrafo se llama \u00abbirome\u00bb?",
      "La pluma que la RAF necesitaba — y un refugiado que la hizo"],
     "Refugiado, solución bajo presión, la idea al ver secarse la tinta de imprenta. Ata con "
     "\u00abExodo\u00bb sin forzar: alguien que empieza de cero en otro continente.",
     None),
    ("T01-07", "Colonel Sanders / KFC", "aprobada", "A", "medio", 17,
     "Empezó a los 65 con el cheque de la pensión, durmiendo en el coche.",
     ["Empezó a los 65 con un cheque de la PENSIÓN",
      "El hombre de KFC durmió en su COCHE vendiendo pollo",
      "¿Cuántas veces te pueden decir que NO?"],
     "Reinvención tardía. Para llevar: la edad como excusa. De camino, desmontar el mito de "
     "los \u00ab1009 rechazos\u00bb — la cifra no tiene fuente sólida.",
     None),
    ("T01-08", "Rolex", "aprobada", "A", "alto", 19,
     "El reloj sumergible, probado cruzando el Canal de la Mancha a nado (1927).",
     ["Cruzó el Canal de la Mancha a NADO para probar un reloj",
      "¿CÓMO convences al mundo de que un reloj es INDESTRUCTIBLE?",
      "El truco publicitario que hizo a Rolex"],
     "La \u00abprueba viva\u00bb como estrategia de marca; y la nadadora, Mercedes Gleitze, casi olvidada "
     "frente al reloj que promocionó.",
     None),
    ("T01-09", "Hokusai", "en producción (E001)", "A / B", "alto", 19,
     "Lo perdió todo tres veces — incendios, deudas — y pintó \u00abLa gran ola\u00bb a los 70.",
     ["Lo perdió TODO tres veces — y pintó \u00abLa gran ola\u00bb a los 70",
      "A los 70 dijo que aún NO sabía dibujar",
      "El artista que cambió de nombre 30 veces buscando ser mejor"],
     "Maestría como dirección, no como destino. Puso la meta tan lejos que sabía que no la "
     "alcanzaría — y eso lo mantuvo trabajando a los 88.",
     "Primer episodio en producción. Guion v1.2 hecho, en fact-check."),
    ("T01-10", "LEGO", "incubando", "A", "medio-bajo", 15,
     "Casi desaparece en 2004; el taller ardió tres veces.",
     ["LEGO estuvo a punto de DESAPARECER en 2004",
      "El taller que ardió TRES veces",
      "\u00abSolo lo mejor es suficiente\u00bb — cómo una familia arruinada construyó LEGO"],
     "Obsesión por la calidad en la Depresión + la casi quiebra de 2003–04 y el giro.",
     "Riesgo: archivo corporativo propietario (poco material libre) y hagiografía. Contrastar con fuentes independientes."),
    ("T01-11", "Stanislav Petrov", "incubando", "A / C", "medio-bajo", 17,
     "1983: evitó la guerra nuclear con una corazonada — y lo apartaron.",
     ["El hombre que evitó la GUERRA NUCLEAR — y al que castigaron",
      "1983: la computadora dijo que EE. UU. había ATACADO",
      "¿Qué harías con 15 minutos para decidir el FIN DEL MUNDO?"],
     "Juicio individual contra el protocolo y la máquina; el coste de tener razón (lo apartaron, "
     "sin premio). El individuo frente al sistema.",
     "Hook enorme; el freno es el material (URSS, 1983 — casi todo reconstrucción gráfica)."),
    ("T01-12", "Madam C.J. Walker", "aprobada", "A", "medio-alto", 19,
     "Hija de esclavos, huérfana a los 7 — primera millonaria hecha a sí misma de EE. UU.",
     ["Hija de esclavos, huérfana a los 7 — la primera MILLONARIA hecha a sí misma de EE. UU.",
      "De lavar ropa por centavos a una MANSIÓN junto a Rockefeller",
      "¿CÓMO se construye un imperio cuando TODO está en tu contra?"],
     "Raza, género, pobreza; construir con todo en contra, y qué hizo con el dinero "
     "(filantropía, activismo).",
     None),
    ("T01-13", "Garrett Morgan", "aprobada", "A / C", "medio", 18,
     "Inventor negro; tuvo que fingir ser blanco para vender su invento.",
     ["Inventó lo que te SALVA la vida — y tuvo que FINGIR ser blanco para venderlo",
      "El inventor negro que RESCATÓ a 30 hombres bajo un lago",
      "¿POR QUÉ nadie quería COMPRARLE su invento?"],
     "Talento + la barrera racial + el ingenio para sortearla (contrató a un actor blanco para "
     "las demostraciones). La máscara antigás y el semáforo.",
     None),
    ("T01-14", "Toyota / Taiichi Ohno", "incubando", "A", "medio-bajo", 16,
     "Demasiado pobres para copiar a EE. UU. — inventaron algo mejor y vencieron a Detroit.",
     ["Eran demasiado POBRES para copiar a EE. UU. — así que inventaron algo mejor",
      "¿CÓMO venció Japón a Detroit?",
      "El método que nació de NO tener dinero"],
     "La restricción como fuente de innovación; David contra Goliat. Para llevar: la falta de "
     "recursos obliga a pensar distinto.",
     "Riesgo de que sea árido — necesita anclarse en personas y escenas, no en el diagrama."),
    ("T01-15", "Wilma Rudolph", "aprobada", "A", "medio", 18,
     "Polio de niña, no caminaba sin aparato ortopédico — 3 oros olímpicos (1960).",
     ["Los médicos dijeron que NUNCA caminaría",
      "De un aparato ortopédico a la mujer más RÁPIDA del mundo",
      "¿CÓMO se corre cuando de niña no podías ni ANDAR?"],
     "Polio, segregación (se negó a un desfile segregado en su honor), la familia de 20 hermanos, "
     "el obstáculo visceral.",
     None),
]

T01_COLA = "Cola (material flojo): Tetris (la URSS lo inventa, guerra de derechos) · Marvel (quiebra de 1996, hipoteca de personajes para hacer Iron Man)."

T02 = [
    ("T02-01", "Radium Girls", "aprobada", "A", "alto", 19,
     "Les dijeron que el veneno luminoso era seguro; el juicio que creó la seguridad laboral.",
     ["Les dijeron que el VENENO brillante era seguro",
      "¿POR QUÉ la empresa las dejó MORIR?",
      "Las obreras que te dieron tu DERECHO a un trabajo seguro"],
     "Negación institucional, difusión de responsabilidad, el informe interno ignorado. "
     "El juicio que fundó el derecho laboral de seguridad en EE. UU.",
     "Sobrio — historia laboral, no morbo."),
    ("T02-02", "El colapso del Hyatt Regency", "aprobada", "A / C", "medio", 17,
     "Un cambio de plano que nadie recalculó — 114 muertos en un baile (Kansas City, 1981).",
     ["¿QUIÉN fue el CULPABLE?",
      "Un CAMBIO de plano que nadie revisó mató a 114 personas",
      "114 muertos en un baile — La VERDADERA HISTORIA del Hyatt Regency"],
     "Normalización de un atajo: un cambio de fabricación duplicó la carga en una unión, "
     "aprobado sin recalcular. Quién firma, quién revisa.",
     None),
    ("T02-03", "Tulipomanía", "aprobada", "C / A", "alto", 19,
     "La burbuja más famosa de la historia — y por qué casi todo lo que sabes es falso.",
     ["¿De verdad un país ENLOQUECIÓ por unas flores?",
      "La BURBUJA más famosa de la historia — y por qué casi todo lo que sabes es falso",
      "Cómo una MENTIRA sobre unas flores duró 400 años"],
     "La manía real (mercado de futuros de bulbos) y cómo el relato del siglo XIX infló el mito. "
     "Muy on-brand: cómo una historia se come a los hechos.",
     None),
    ("T02-04", "La plaga del baile de 1518", "incubando", "A / C", "medio-bajo", 16,
     "Decenas de personas bailaron durante días, algunas hasta morir — y nadie sabe por qué.",
     ["Bailaron hasta MORIR — y nadie sabe por qué",
      "¿QUÉ le pasó a Estrasburgo en el verano de 1518?",
      "Cuando el ESTRÉS de un pueblo se volvió una epidemia de baile"],
     "Enfermedad psicogénica masiva, sugestión, el cuerpo bajo presión colectiva (hambruna, "
     "enfermedad). El registro es escaso — puede ser un episodio de \u00abpor qué no lo sabemos\u00bb.",
     None),
    ("T02-05", "Talidomida", "aprobada", "A / B", "medio", 18,
     "La pastilla \u00absegura\u00bb que deformó a 10.000 bebés — y la funcionaria que dijo no.",
     ["La pastilla \u00absegura\u00bb que deformó a 10.000 bebés",
      "La FUNCIONARIA que dijo NO y salvó a un país",
      "¿CÓMO se aprobó? — La VERDADERA HISTORIA de la talidomida"],
     "El sistema que falló (marketing agresivo, pruebas insuficientes) y Frances Kelsey, "
     "que puso el freno en EE. UU.",
     "Sobrio; nota de recursos de ayuda si aplica."),
    ("T02-06", "El gran engaño lunar de 1835", "aprobada", "A / C", "alto", 19,
     "Un periódico de Nueva York dijo que había hombres-murciélago en la Luna — y le creyeron.",
     ["El día que un PERIÓDICO dijo que había HOMBRES-MURCIÉLAGO en la Luna — y le creyeron",
      "La MENTIRA que vendió más periódicos que ninguna verdad",
      "¿POR QUÉ queríamos creerlo?"],
     "Credibilidad prestada (se atribuyó a un astrónomo real) + el deseo de creer = aceptación "
     "masiva. Nunca se retractó del todo. Meta-relevante para un canal sobre \u00abversión real vs. oficial\u00bb.",
     None),
]

ESPERA = [
    ("Colonia Dignidad (Chile, 1961–2005)", "T02",
     "Riesgo legal alto — víctimas y responsables vivos, litigio. Pase legal serio antes de aprobar."),
    ("Katalin Karikó (mRNA, Nobel 2023)", "T01",
     "Persona viva; material casi todo con derechos. Reevaluar con un plan de gráficos propios."),
    ("La \u00abGuerra del Emu\u00bb (Australia, 1932)", "T02",
     "Descartada por ahora — el hook es cómico y la reflexión no sostiene un episodio (mejor un short)."),
]


# ---- rendering -----------------------------------------------------------

def card(idea):
    tid, title, status, close, mat, score, angle, hooks, close_txt, notes = idea
    inner = []
    inner.append(Paragraph(f"{tid} &nbsp;·&nbsp; {title}", S["h2"]))
    inner.append(Paragraph(
        f"Estado: {status} &nbsp;|&nbsp; Cierre: forma {close} &nbsp;|&nbsp; "
        f"Material dominio público: {mat} &nbsp;|&nbsp; Puntuación estimada: {score}/21", S["meta"]))
    inner.append(Paragraph("EL GANCHO", S["label"]))
    inner.append(Paragraph(hooks[0] + " &nbsp;| Documental", S["hook"]))
    for h in hooks[1:]:
        inner.append(Paragraph(h + " &nbsp;| Documental", S["hook2"]))
    inner.append(Paragraph("EL \u00c1NGULO", S["label"]))
    inner.append(Paragraph(angle, S["body"]))
    inner.append(Paragraph("EL CIERRE", S["label"]))
    inner.append(Paragraph(close_txt, S["body"]))
    if notes:
        inner.append(Paragraph("NOTA", S["label"]))
        inner.append(Paragraph(notes, S["body"]))
    t = Table([[inner]], colWidths=[165 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CARD),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return KeepTogether([t, Spacer(1, 7)])


def summary_table(rows):
    data = [[Paragraph(x, S["cellh"]) for x in ["#", "Idea", "Cierre", "Material", "/21", "Estado"]]]
    for r in rows:
        data.append([Paragraph(str(c), S["cell"]) for c in
                     (r[0], r[1], r[3], r[4], r[5], r[2])])
    t = Table(data, colWidths=[16 * mm, 52 * mm, 15 * mm, 22 * mm, 12 * mm, 48 * mm], repeatRows=1)
    st = [("BACKGROUND", (0, 0), (-1, 0), ACCENT),
          ("GRID", (0, 0), (-1, -1), 0.4, RULE),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
    for i in range(1, len(data)):
        if i % 2 == 0:
            st.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#faf8f4")))
    t.setStyle(TableStyle(st))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Head-R", 8)
    canvas.setFillColor(MUTE)
    canvas.drawCentredString(A4[0] / 2, 12 * mm,
                             f"Exodo · Pool de ideas · pág. {doc.page}")
    canvas.restoreState()


def build(out):
    doc = SimpleDocTemplate(out, pagesize=A4,
                            leftMargin=22 * mm, rightMargin=22 * mm,
                            topMargin=20 * mm, bottomMargin=20 * mm,
                            title="Exodo — Pool de ideas", author="Exodo")
    st = []
    # cover
    st.append(Spacer(1, 40 * mm))
    st.append(Paragraph("Exodo", S["title"]))
    st.append(Spacer(1, 4))
    st.append(Paragraph("Pool de ideas — Ronda 1", S["h1"]))
    st.append(Spacer(1, 10))
    st.append(Paragraph("Documento de pitch para Carmen. 21 ideas para episodios, en dos tracks. "
                        "Cada una con su gancho (título estilo Farid Dieck), el ángulo oculto que la "
                        "hace clicable, y hacia dónde apunta la reflexión del cierre.", S["subtitle"]))
    st.append(Spacer(1, 16))
    st.append(HRFlowable(width="100%", thickness=0.6, color=RULE))
    st.append(Spacer(1, 10))
    st.append(Paragraph("Cómo leer esto", S["h2"]))
    for line in [
        "<b>Tracks.</b> T01 Historias Inspiradoras (owner: Carmen) — biografías y trayectorias "
        "de sujetos reconocibles con un ángulo oculto. T02 Exploración (owner: Josh) — errores, "
        "fraudes, manías, casos que revelan cómo deciden las personas y las instituciones.",
        "<b>Cierre.</b> Forma A = reflexión + para llevar. Forma B = lección distribuida por la "
        "narrativa, final elegíaco. Forma C = pregunta abierta al espectador.",
        "<b>Puntuación /21.</b> Estimación de ideación (fuerza del hook, narrativa, fuentes, "
        "ángulo humano, cierre, relevancia, material). Se cierra en el brief. \u226514 = aprobada.",
        "<b>Estado.</b> aprobada · incubando (falta material o ángulo) · en producción.",
        "<b>Nota de rigor.</b> Todo caso es registro público, con fuentes verificables, y ninguno "
        "toca a nadie que conozcamos. Los mitos pegados "
        "(\u00ab1009 rechazos\u00bb, etc.) el canal los desmonta de camino.",
    ]:
        st.append(Paragraph(line, S["body"]))
    st.append(PageBreak())

    # T01
    st.append(Paragraph("T01 · Historias Inspiradoras", S["h1"]))
    st.append(Paragraph("Owner de ideación: Carmen. Sujetos reconocibles, ángulo oculto.", S["lead"]))
    st.append(summary_table(T01))
    st.append(Spacer(1, 4))
    st.append(Paragraph(T01_COLA, S["meta"]))
    st.append(Spacer(1, 10))
    for idea in T01:
        st.append(card(idea))
    st.append(PageBreak())

    # T02
    st.append(Paragraph("T02 · Exploración", S["h1"]))
    st.append(Paragraph("Owner de ideación: Josh. Errores, fraudes, manías; cómo deciden "
                        "personas e instituciones.", S["lead"]))
    st.append(summary_table(T02))
    st.append(Spacer(1, 10))
    for idea in T02:
        st.append(card(idea))

    # espera
    st.append(Spacer(1, 6))
    st.append(Paragraph("En espera", S["h1"]))
    for name, tr, why in ESPERA:
        st.append(Paragraph(f"<b>{name}</b> &nbsp;({tr})", S["body"]))
        st.append(Paragraph(why, S["meta"]))
    st.append(Spacer(1, 10))
    st.append(HRFlowable(width="100%", thickness=0.6, color=RULE))
    st.append(Spacer(1, 8))
    st.append(Paragraph("Próximo paso", S["h2"]))
    st.append(Paragraph("Carmen y Josh eligen cuál va primero a brief. El brief confirma track, "
                        "hook-title definitivo, cross-check de material real y forma de cierre; "
                        "corre los eliminatorios y la puntuación completa; y si pasa, arranca "
                        "producción. Hokusai (T01-09) ya está en marcha.", S["body"]))

    doc.build(st, onFirstPage=footer, onLaterPages=footer)
    print("wrote", out)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent / "ideas" / "idea-pool.pdf")
    build(out)
