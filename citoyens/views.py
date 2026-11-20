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
from .forms import CitoyenForm
from .models import Citoyen


@acces_communal
def liste(request):
    citoyens = filtrer_fokontany(
        Citoyen.objects.select_related("fokontany"),
        request.user,
    )

    recherche = request.GET.get("q", "").strip()
    if recherche:
        citoyens = citoyens.filter(
            Q(numero_citoyen__icontains=recherche)
            | Q(nom__icontains=recherche)
            | Q(prenoms__icontains=recherche)
            | Q(telephone__icontains=recherche)
        )

    return render(request, "citoyens/liste.html", {
        "citoyens": citoyens,
        "recherche": recherche,
    })


@acces_communal
def ajouter(request):
    fokontany = fokontany_utilisateur(request.user)

    if est_chef(request.user) and not fokontany:
        raise PermissionDenied

    if request.method == "POST":
        formulaire = CitoyenForm(request.POST, fokontany=fokontany)

        if formulaire.is_valid():
            citoyen = formulaire.save(commit=False)
            if fokontany:
                citoyen.fokontany = fokontany
            citoyen.save()
            messages.success(request, "Le citoyen a été ajouté.")
            return redirect("citoyens:liste")
    else:
        formulaire = CitoyenForm(fokontany=fokontany)

    return render(request, "citoyens/formulaire.html", {
        "formulaire": formulaire,
        "titre": "Ajouter un citoyen",
    })


@acces_communal
def modifier(request, pk):
    citoyens = filtrer_fokontany(Citoyen.objects.all(), request.user)
    citoyen = get_object_or_404(citoyens, pk=pk)
    fokontany = fokontany_utilisateur(request.user)

    if request.method == "POST":
        formulaire = CitoyenForm(
            request.POST,
            instance=citoyen,
            fokontany=fokontany,
        )

        if formulaire.is_valid():
            formulaire.save()
            messages.success(request, "Le citoyen a été modifié.")
            return redirect("citoyens:liste")
    else:
        formulaire = CitoyenForm(instance=citoyen, fokontany=fokontany)

    return render(request, "citoyens/formulaire.html", {
        "formulaire": formulaire,
        "titre": f"Modifier {citoyen.nom} {citoyen.prenoms}",
    })

