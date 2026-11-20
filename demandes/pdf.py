import io
from pathlib import Path

import qrcode
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

VERT = colors.HexColor("#176b50")
VERT_FONCE = colors.HexColor("#104b39")
OR = colors.HexColor("#c9a227")
GRIS = colors.HexColor("#64748b")
CLAIR = colors.HexColor("#eef5f1")


def _logo_path():
    chemin = Path(settings.BASE_DIR) / "static" / "img" / "logo.png"
    return chemin if chemin.exists() else None


def _qr_image(contenu, taille=30 * mm):
    image_qr = qrcode.make(contenu)
    tampon = io.BytesIO()
    image_qr.save(tampon, format="PNG")
    tampon.seek(0)
    return Image(tampon, width=taille, height=taille)


def generer_pdf_demande(demande):
    tampon = io.BytesIO()
    document = SimpleDocTemplate(
        tampon,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title=f"Demande {demande.reference}",
        author="Commune d'Anosizato Ouest",
    )

    styles = getSampleStyleSheet()
    style_titre = ParagraphStyle(
        "TitreCommune",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        textColor=VERT_FONCE,
        alignment=TA_CENTER,
    )
    style_sous_titre = ParagraphStyle(
        "SousTitre",
        parent=styles["Normal"],
        fontSize=10,
        leading=13,
        textColor=GRIS,
        alignment=TA_CENTER,
    )
    style_section = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=VERT_FONCE,
        spaceBefore=10,
        spaceAfter=6,
    )
    style_normal = ParagraphStyle(
        "NormalGIC",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
    )
    style_cellule = ParagraphStyle(
        "Cellule",
        parent=style_normal,
        fontSize=9,
        leading=12,
    )

    logo = _logo_path()
    if logo:
        logo_flow = Image(str(logo), width=24 * mm, height=24 * mm)
    else:
        logo_flow = Paragraph("<b>GIC</b>", style_titre)

    entete_gauche = logo_flow
    entete_centre = [
        Paragraph("RÉPUBLIQUE DE MADAGASCAR", style_sous_titre),
        Paragraph("COMMUNE D'ANOSIZATO OUEST", style_titre),
        Paragraph(
            f"Fokontany : {demande.fokontany.nom}",
            style_sous_titre,
        ),
    ]
    entete_droite = _qr_image(demande.contenu_qr)

    entete = Table(
        [[entete_gauche, entete_centre, entete_droite]],
        colWidths=[30 * mm, 105 * mm, 35 * mm],
    )
    entete.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (2, 0), (2, 0), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    ligne = Table(
        [[""]],
        colWidths=[170 * mm],
        rowHeights=[2.5 * mm],
    )
    ligne.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), VERT),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    elements = [
        entete,
        ligne,
        Spacer(1, 10),
        Paragraph("DÉCISION DE LA COMMUNE", style_section),
        Paragraph(
            f"Référence : <b>{demande.reference}</b>",
            style_normal,
        ),
        Paragraph(
            f"Objet : <b>{demande.objet}</b>",
            style_normal,
        ),
        Spacer(1, 6),
    ]

    lignes = [
        ("Type de demande", demande.get_type_demande_display()),
        ("Fokontany", demande.fokontany.nom),
        ("Demandeur", demande.demandeur.get_full_name() or demande.demandeur.username),
        ("Priorité", demande.get_priorite_display()),
        ("Statut", demande.get_statut_display()),
        ("Date de la demande", demande.date_creation.strftime("%d/%m/%Y %H:%M")),
        ("Lieu", demande.fokontany.adresse or demande.fokontany.nom),
    ]

    if demande.citoyen:
        lignes.append((
            "Citoyen concerné",
            f"{demande.citoyen.nom} {demande.citoyen.prenoms} "
            f"({demande.citoyen.numero_citoyen})",
        ))
    if demande.document_souhaite:
        lignes.append(("Document souhaité", demande.document_souhaite))
    if demande.date_traitement:
        lignes.append((
            "Date de traitement",
            demande.date_traitement.strftime("%d/%m/%Y %H:%M"),
        ))
    if demande.traite_par:
        lignes.append((
            "Traitée par",
            demande.traite_par.get_full_name() or demande.traite_par.username,
        ))

    tableau = Table(
        [
            [
                Paragraph(f"<b>{label}</b>", style_cellule),
                Paragraph(str(valeur), style_cellule),
            ]
            for label, valeur in lignes
        ],
        colWidths=[50 * mm, 120 * mm],
    )
    tableau.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), CLAIR),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d7e4dd")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(tableau)

    elements.append(Paragraph("Description de la demande", style_section))
    elements.append(
        Paragraph(
            (demande.description or "—").replace("\n", "<br/>"),
            style_normal,
        )
    )

    if demande.reponse:
        elements.append(Paragraph("Réponse de la commune", style_section))
        elements.append(
            Paragraph(
                demande.reponse.replace("\n", "<br/>"),
                style_normal,
            )
        )

    elements.append(Spacer(1, 16))
    elements.append(
        Paragraph(
            "Ce document est généré automatiquement par la plateforme de "
            "gestion intégrée de la Commune d'Anosizato Ouest. "
            "Le QR code ci-dessus permet de vérifier la référence de la demande.",
            ParagraphStyle(
                "Note",
                parent=style_normal,
                fontSize=8,
                textColor=GRIS,
            ),
        )
    )
    elements.append(Spacer(1, 18))

    signature = Table(
        [
            [
                Paragraph("Le Chef Fokontany", style_sous_titre),
                Paragraph("Le Maire de la Commune", style_sous_titre),
            ],
            [
                Paragraph("<br/><br/><br/>______________________", style_cellule),
                Paragraph("<br/><br/><br/>______________________", style_cellule),
            ],
        ],
        colWidths=[85 * mm, 85 * mm],
    )
    signature.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(signature)

    elements.append(Spacer(1, 16))
    if demande.cachet_applique:
        cachet_texte = "CACHET OFFICIEL DE LA COMMUNE"
        cachet_couleur = colors.HexColor("#b91c1c")
    else:
        cachet_texte = "CACHET MASQUÉ — en attente du responsable"
        cachet_couleur = colors.HexColor("#dc2626")

    cachet = Table(
        [[Paragraph(
            f"<b>{cachet_texte}</b>",
            ParagraphStyle(
                "Cachet",
                parent=style_cellule,
                textColor=cachet_couleur,
                alignment=TA_CENTER,
                fontSize=10,
            ),
        )]],
        colWidths=[170 * mm],
    )
    cachet.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.4, cachet_couleur),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fef2f2")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(cachet)

    document.build(elements)
    contenu = tampon.getvalue()
    tampon.close()
    return contenu
