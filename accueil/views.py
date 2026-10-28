from django.shortcuts import render


def dashboard(request):
    context = {
        'titre': 'Tableau de bord',
        'commune': 'Commune d’Anosizato Ouest',
    }
    return render(request, 'accueil/dashboard.html', context)