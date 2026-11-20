<<<<<<< HEAD
# GIC-Anosizato-Ouest

Plateforme de gestion intégrée de la Commune d'Anosizato Ouest
(District Antananarivo Atsimondrano, Madagascar).

Stack : Django 6, Python 3.14, MySQL (ou SQLite en développement), reportlab,
qrcode, Leaflet et Chart.js.

## Fonctionnalités

- Page d'accueil publique interactive : slogan, slider, carte des 7 fokontany,
  actualités et présentation de la commune.
- Page « La commune » avec carte Leaflet, spécificités de chaque fokontany et
  statistiques.
- Authentification avec sélection du rôle.
- Tableau de bord global pour les rôles communaux et tableau de bord du chef
  fokontany (statistiques, graphiques, demandes, adidy, actualités).
- Recensement des citoyens par fokontany.
- Population de référence par fokontany (hommes/femmes/total, avec année et source),
  affichée sur l'accueil, la commune, les tableaux de bord, les fiches et la carte.
- État civil : actes de naissance, certificats et documents administratifs
  (certificat de résidence avec père, mère, date/lieu de naissance et usage).
- Demandes d'amélioration : route, école, commune, CSBII, WC public, pompe,
  certificat de résidence, recensement et adidy.
- Workflow de demande : en attente, acceptée, refusée, mise en attente.
- Paiement adidy lié au carnet de fokontany.
- Fonds de l'association : entrées, sorties et solde.
- Actualités publiées par l'administration et visibles par les chefs.
- Export PDF avec logo, QR code de vérification et cachet officiel.

## Rôles et responsabilités

- **Administrateur** : gestion des comptes, des rôles et des paramètres de la
  plateforme (création/modification/suppression de comptes, fokontany, admin Django).
- **Maire** : consultation et supervision des informations communales (vue globale).
- **Chef Fokontany** : gestion des informations relatives à son fokontany
  (citoyens, état civil, personnel, adidy, demandes).
- **Trésorier** : gestion et suivi des opérations de trésorerie (adidy et fonds
  de l'association).
- **Secrétaire** : gestion des informations et opérations administratives
  (recensement, état civil, personnel, création et traitement des demandes).
- **Première Adjointe / Premier Adjoint** et **Deuxième Adjointe / Deuxième
  Adjoint** : supervision communale et traitement des demandes.

Chaque fokontany ne peut avoir qu'un seul chef affecté. Les rôles
Administrateur, Maire, Trésorier et Secrétaire sont uniques.

## Workflow des demandes

1. Le chef de fokontany crée une demande (amélioration, certificat de résidence,
   recensement, adidy...).
2. L'administration consulte la demande et l'accepte, la refuse ou la met en
   attente avec un motif.
3. Une fois la demande acceptée ou refusée, le PDF devient téléchargeable.
4. Le maire peut appliquer le cachet officiel sur le document.

## Installation

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

```powershell
Copy-Item .env.example .env
```

Variables disponibles :

- `DJANGO_SECRET_KEY` : clé secrète obligatoire.
- `DJANGO_DEBUG` : `True` en développement, `False` en production.
- `DJANGO_ALLOWED_HOSTS` : hôtes autorisés séparés par des virgules.
- `DB_ENGINE` : `mysql` (défaut) ou `sqlite` pour un repli sans serveur.
- `MYSQL_DATABASE` : `gic_anosizato` (base utilisée par la plateforme).
- `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT` : paramètres MySQL.

Le backend `config.db_backends.mysql` autorise MariaDB 10.4 avec Django 6,
qui exige normalement MariaDB 10.11+.

### MySQL

Prérequis : MySQL 8.0+ ou MariaDB 10.11+ (Django 6 refuse les versions plus
anciennes). Créer la base puis renseigner `.env` :

```sql
CREATE DATABASE gic_anosizato
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

```dotenv
DB_ENGINE=mysql
MYSQL_DATABASE=gic_anosizato
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
```

## Base de données

```powershell
python manage.py migrate
python manage.py charger_fokontany
python manage.py charger_population
python manage.py createsuperuser
```

`charger_fokontany` renseigne aussi les responsables des 7 fokontany selon la
monographie de la commune, ainsi que leurs positions GPS d'après les divisions
ADM4 GeoNames `11117012001` à `11117012007`. Il met à jour le responsable et les
coordonnées si ceux-ci diffèrent, sans modifier le code existant d'un fokontany
déjà enregistré.

Après `createsuperuser`, le superutilisateur se connecte en choisissant le rôle
« Administrateur ». Les comptes des chefs et des autres acteurs se créent depuis
le menu « Comptes et rôles ».

## Lancement

```powershell
python manage.py runserver
```

- Accueil : http://127.0.0.1:8000/
- La commune : http://127.0.0.1:8000/commune/
- Connexion : http://127.0.0.1:8000/connexion/
- Tableau de bord : http://127.0.0.1:8000/tableau-de-bord/
- Demandes : http://127.0.0.1:8000/demandes/
- Citoyens : http://127.0.0.1:8000/citoyens/
- État civil : http://127.0.0.1:8000/etat-civil/
- Personnel : http://127.0.0.1:8000/personnel/
- Fokontany : http://127.0.0.1:8000/fokontany/
- Carte GPS : http://127.0.0.1:8000/fokontany/carte/
- Population (administrateur) : http://127.0.0.1:8000/fokontany/population/
- Adidy : http://127.0.0.1:8000/finances/adidy/
- Fonds association : http://127.0.0.1:8000/finances/association/
- Comptes et rôles : http://127.0.0.1:8000/comptes/chefs/
- Paramètres : http://127.0.0.1:8000/comptes/parametres/
- Administration : http://127.0.0.1:8000/admin/

## Tests

```powershell
python manage.py check
python manage.py test
```
=======
# GIC_Anosizato_Ouest
>>>>>>> 8dd7f724b73e2d68d21e7cd69217822d6682d5ff
