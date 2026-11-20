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
from .forms import PersonnelForm
from .models import Personnel


@acces_communal
def liste(request):
    agents = filtrer_fokontany(
        Personnel.objects.select_related("fokontany"),
        request.user,
    )

    recherche = request.GET.get("q", "").strip()
    statut = request.GET.get("statut", "").strip()

    if recherche:
        agents = agents.filter(
            Q(matricule__icontains=recherche)
            | Q(nom__icontains=recherche)
            | Q(prenoms__icontains=recherche)
            | Q(fonction__icontains=recherche)
            | Q(service__icontains=recherche)
        )

    if statut:
        agents = agents.filter(statut=statut)

    return render(request, "personnel/liste.html", {
        "agents": agents,
        "recherche": recherche,
        "statut_selectionne": statut,
        "statuts": Personnel.STATUT_CHOICES,
    })


@acces_communal
def ajouter(request):
    fokontany = fokontany_utilisateur(request.user)

    if est_chef(request.user) and not fokontany:
        raise PermissionDenied

    if request.method == "POST":
        formulaire = PersonnelForm(request.POST, fokontany=fokontany)

        if formulaire.is_valid():
            agent = formulaire.save(commit=False)
            if fokontany:
                agent.fokontany = fokontany
            agent.save()
            messages.success(request, "L'agent a été enregistré.")
            return redirect("personnel:liste")
    else:
        formulaire = PersonnelForm(fokontany=fokontany)

    return render(request, "personnel/formulaire.html", {
        "formulaire": formulaire,
        "titre": "Ajouter un agent",
    })


@acces_communal
def modifier(request, pk):
    agents = filtrer_fokontany(Personnel.objects.all(), request.user)
    agent = get_object_or_404(agents, pk=pk)
    fokontany = fokontany_utilisateur(request.user)

    if request.method == "POST":
        formulaire = PersonnelForm(
            request.POST,
            instance=agent,
            fokontany=fokontany,
        )

        if formulaire.is_valid():
            formulaire.save()
            messages.success(request, "L'agent a été modifié.")
            return redirect("personnel:liste")
    else:
        formulaire = PersonnelForm(instance=agent, fokontany=fokontany)

    return render(request, "personnel/formulaire.html", {
        "formulaire": formulaire,
        "titre": f"Modifier {agent.nom} {agent.prenoms}",
    })

