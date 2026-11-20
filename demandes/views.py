from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from comptes.models import ProfilUtilisateur
from comptes.permissions import (
    acces_communal,
    acces_global,
    est_chef,
    est_maire,
    est_secretaire,
    fokontany_utilisateur,
    role_required,
    secretariat_required,
)
from fokontany.models import Fokontany
from .forms import DemandeForm, TraitementDemandeForm
from .models import Demande
from .pdf import generer_pdf_demande


def _demandes_accessibles(user):
    demandes = Demande.objects.select_related(
        "fokontany",
        "demandeur",
        "citoyen",
        "traite_par",
    )

    if acces_global(user):
        return demandes

    fokontany = fokontany_utilisateur(user)
    if not fokontany:
        return demandes.none()

    return demandes.filter(fokontany=fokontany)


@acces_communal
def liste(request):
    demandes = _demandes_accessibles(request.user)

    statut = request.GET.get("statut", "").strip()
    type_demande = request.GET.get("type", "").strip()
    fokontany_id = request.GET.get("fokontany", "").strip()
    recherche = request.GET.get("q", "").strip()

    if statut:
        demandes = demandes.filter(statut=statut)

    if type_demande:
        demandes = demandes.filter(type_demande=type_demande)

    if fokontany_id and acces_global(request.user):
        demandes = demandes.filter(fokontany_id=fokontany_id)

    if recherche:
        demandes = demandes.filter(
            Q(objet__icontains=recherche)
            | Q(description__icontains=recherche)
        )

    return render(request, "demandes/liste.html", {
        "demandes": demandes,
        "statut_selectionne": statut,
        "type_selectionne": type_demande,
        "fokontany_selectionne": fokontany_id,
        "recherche": recherche,
        "statuts": Demande.CHOIX_STATUTS,
        "types": Demande.CHOIX_TYPES,
        "fokontanys": Fokontany.objects.all() if acces_global(request.user) else [],
    })


@role_required(ProfilUtilisateur.ROLE_CHEF, ProfilUtilisateur.ROLE_SECRETAIRE)
def creer(request):
    chef = est_chef(request.user)
    fokontany = fokontany_utilisateur(request.user)

    if chef and not fokontany:
        raise PermissionDenied

    if request.method == "POST":
        formulaire = DemandeForm(request.POST, fokontany=fokontany)

        if formulaire.is_valid():
            demande = formulaire.save(commit=False)
            demande.fokontany = fokontany or formulaire.cleaned_data["fokontany"]
            demande.demandeur = request.user
            demande.full_clean()
            demande.save()
            messages.success(
                request,
                "Votre demande a été envoyée au maire de la commune.",
            )
            return redirect("demandes:detail", pk=demande.pk)
    else:
        formulaire = DemandeForm(fokontany=fokontany)

    return render(request, "demandes/formulaire.html", {
        "formulaire": formulaire,
        "fokontany": fokontany,
    })


@acces_communal
def detail(request, pk):
    demande = get_object_or_404(_demandes_accessibles(request.user), pk=pk)

    formulaire_traitement = None
    if (est_maire(request.user) or est_secretaire(request.user)) and demande.statut in (
        Demande.STATUT_EN_ATTENTE,
        Demande.STATUT_MISE_EN_ATTENTE,
    ):
        formulaire_traitement = TraitementDemandeForm()

    return render(request, "demandes/detail.html", {
        "demande": demande,
        "formulaire_traitement": formulaire_traitement,
    })


@secretariat_required
def traiter(request, pk):
    demande = get_object_or_404(Demande, pk=pk)

    if request.method != "POST":
        return redirect("demandes:detail", pk=demande.pk)

    if demande.statut not in (
        Demande.STATUT_EN_ATTENTE,
        Demande.STATUT_MISE_EN_ATTENTE,
    ):
        messages.error(request, "Cette demande a déjà été traitée.")
        return redirect("demandes:detail", pk=demande.pk)

    formulaire = TraitementDemandeForm(request.POST)

    if formulaire.is_valid():
        demande.statut = formulaire.cleaned_data["decision"]
        demande.reponse = formulaire.cleaned_data["reponse"].strip()
        demande.traite_par = request.user
        demande.date_traitement = timezone.now()
        demande.save(update_fields=[
            "statut",
            "reponse",
            "traite_par",
            "date_traitement",
        ])

        if demande.statut == Demande.STATUT_ACCEPTEE:
            messages.success(request, "La demande a été acceptée.")
        elif demande.statut == Demande.STATUT_MISE_EN_ATTENTE:
            messages.warning(request, "La demande a été mise en attente.")
        else:
            messages.warning(request, "La demande a été refusée.")

        return redirect("demandes:detail", pk=demande.pk)

    for champ, erreurs in formulaire.errors.items():
        for erreur in erreurs:
            messages.error(request, erreur)

    return redirect("demandes:detail", pk=demande.pk)


@role_required(ProfilUtilisateur.ROLE_CHEF)
def annuler(request, pk):
    demande = get_object_or_404(
        Demande.objects.filter(fokontany=fokontany_utilisateur(request.user)),
        pk=pk,
    )

    if request.method != "POST":
        return redirect("demandes:detail", pk=demande.pk)

    if not demande.en_attente:
        messages.error(request, "Seule une demande en attente peut être annulée.")
        return redirect("demandes:detail", pk=demande.pk)

    demande.statut = Demande.STATUT_ANNULEE
    demande.date_traitement = timezone.now()
    demande.save(update_fields=["statut", "date_traitement"])
    messages.info(request, "La demande a été annulée.")

    return redirect("demandes:detail", pk=demande.pk)


@acces_communal
def pdf(request, pk):
    demande = get_object_or_404(_demandes_accessibles(request.user), pk=pk)

    if not demande.est_finie:
        messages.error(
            request,
            "Le document PDF est disponible uniquement lorsque la demande "
            "est acceptée ou refusée.",
        )
        return redirect("demandes:detail", pk=demande.pk)

    contenu = generer_pdf_demande(demande)
    response = HttpResponse(contenu, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="demande-{demande.reference}.pdf"'
    )
    return response


@role_required(ProfilUtilisateur.ROLE_MAIRE)
def appliquer_cachet(request, pk):
    demande = get_object_or_404(Demande, pk=pk)

    if request.method != "POST":
        return redirect("demandes:detail", pk=demande.pk)

    if not demande.est_finie:
        messages.error(
            request,
            "Le cachet ne peut être appliqué qu'à une demande traitée.",
        )
        return redirect("demandes:detail", pk=demande.pk)

    demande.cachet_applique = True
    demande.date_cachet = timezone.now()
    demande.save(update_fields=["cachet_applique", "date_cachet"])
    messages.success(request, "Le cachet officiel a été appliqué au document.")
    return redirect("demandes:detail", pk=demande.pk)
