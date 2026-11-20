from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from comptes.permissions import (
    acces_communal,
    est_chef,
    fokontany_utilisateur,
    filtrer_fokontany,
)
from .forms import (
    ActeEtatCivilForm,
    ActeNaissanceForm,
    DocumentAdministratifForm,
)
from .models import ActeEtatCivil, ActeNaissance, DocumentAdministratif


@acces_communal
def liste(request):
    actes = filtrer_fokontany(
        ActeEtatCivil.objects.select_related("fokontany"),
        request.user,
    )

    recherche = request.GET.get("q", "").strip()
    type_acte = request.GET.get("type", "").strip()

    if recherche:
        actes = actes.filter(
            Q(numero_acte__icontains=recherche)
            | Q(lieu_acte__icontains=recherche)
        )

    if type_acte:
        actes = actes.filter(type_acte=type_acte)

    return render(request, "etat_civil/liste.html", {
        "actes": actes,
        "recherche": recherche,
        "type_selectionne": type_acte,
        "types": ActeEtatCivil.TYPE_ACTE_CHOICES,
    })


@acces_communal
def ajouter(request):
    fokontany = fokontany_utilisateur(request.user)

    if est_chef(request.user) and not fokontany:
        raise PermissionDenied

    if request.method == "POST":
        formulaire = ActeEtatCivilForm(request.POST, fokontany=fokontany)

        if formulaire.is_valid():
            acte = formulaire.save(commit=False)
            if fokontany:
                acte.fokontany = fokontany
            acte.save()
            messages.success(request, "L'acte a été enregistré.")
            return redirect("etat_civil:liste")
    else:
        formulaire = ActeEtatCivilForm(fokontany=fokontany)

    return render(request, "etat_civil/formulaire.html", {
        "formulaire": formulaire,
        "titre": "Enregistrer un acte",
    })


@acces_communal
def modifier(request, pk):
    actes = filtrer_fokontany(ActeEtatCivil.objects.all(), request.user)
    acte = get_object_or_404(actes, pk=pk)
    fokontany = fokontany_utilisateur(request.user)

    if request.method == "POST":
        formulaire = ActeEtatCivilForm(
            request.POST,
            instance=acte,
            fokontany=fokontany,
        )

        if formulaire.is_valid():
            formulaire.save()
            messages.success(request, "L'acte a été modifié.")
            return redirect("etat_civil:liste")
    else:
        formulaire = ActeEtatCivilForm(instance=acte, fokontany=fokontany)

    return render(request, "etat_civil/formulaire.html", {
        "formulaire": formulaire,
        "titre": f"Modifier l'acte {acte.numero_acte}",
    })



@acces_communal
def naissances_liste(request):
    actes = filtrer_fokontany(
        ActeNaissance.objects.select_related("fokontany", "enregistre_par"),
        request.user,
    )
    recherche = request.GET.get("q", "").strip()
    if recherche:
        actes = actes.filter(
            Q(numero_acte__icontains=recherche)
            | Q(nom_enfant__icontains=recherche)
            | Q(prenoms_enfant__icontains=recherche)
            | Q(nom_pere__icontains=recherche)
            | Q(nom_mere__icontains=recherche)
        )

    return render(request, "etat_civil/naissances_liste.html", {
        "actes": actes,
        "recherche": recherche,
    })


@acces_communal
def naissance_ajouter(request):
    fokontany = fokontany_utilisateur(request.user)

    if est_chef(request.user) and not fokontany:
        raise PermissionDenied

    if request.method == "POST":
        formulaire = ActeNaissanceForm(request.POST, fokontany=fokontany)
        if formulaire.is_valid():
            acte = formulaire.save(commit=False)
            if fokontany:
                acte.fokontany = fokontany
            acte.enregistre_par = request.user
            acte.save()
            messages.success(request, "L'acte de naissance a été enregistré.")
            return redirect("etat_civil:naissances_liste")
    else:
        formulaire = ActeNaissanceForm(fokontany=fokontany)

    return render(request, "etat_civil/naissance_formulaire.html", {
        "formulaire": formulaire,
        "titre": "Nouvel acte de naissance",
    })


@acces_communal
def documents_liste(request):
    documents = filtrer_fokontany(
        DocumentAdministratif.objects.select_related(
            "fokontany", "citoyen", "delivre_par"
        ),
        request.user,
    )
    recherche = request.GET.get("q", "").strip()
    type_document = request.GET.get("type", "").strip()

    if recherche:
        documents = documents.filter(
            Q(numero__icontains=recherche)
            | Q(nom_beneficiaire__icontains=recherche)
        )
    if type_document:
        documents = documents.filter(type_document=type_document)

    return render(request, "etat_civil/documents_liste.html", {
        "documents": documents,
        "recherche": recherche,
        "type_selectionne": type_document,
        "types": DocumentAdministratif.CHOIX_TYPES,
    })


@acces_communal
def document_ajouter(request, type_document=None):
    fokontany = fokontany_utilisateur(request.user)
    type_document = (
        type_document
        or request.GET.get("type", "").strip()
        or None
    )

    if est_chef(request.user) and not fokontany:
        raise PermissionDenied

    if request.method == "POST":
        formulaire = DocumentAdministratifForm(
            request.POST,
            fokontany=fokontany,
            type_document=type_document,
        )
        if formulaire.is_valid():
            document = formulaire.save(commit=False)
            if fokontany:
                document.fokontany = fokontany
            document.delivre_par = request.user
            document.save()
            messages.success(request, "Le document a été délivré.")
            return redirect("etat_civil:documents_liste")
    else:
        formulaire = DocumentAdministratifForm(
            fokontany=fokontany,
            type_document=type_document,
        )

    titres = {
        DocumentAdministratif.TYPE_CERTIFICAT_RESIDENCE: "Certificat de résidence",
        DocumentAdministratif.TYPE_CIN: "Carte d'identité nationale",
        DocumentAdministratif.TYPE_BULLETIN_NAISSANCE: "Bulletin de naissance",
    }

    return render(request, "etat_civil/document_formulaire.html", {
        "formulaire": formulaire,
        "titre": titres.get(type_document, "Délivrer un document administratif"),
    })
