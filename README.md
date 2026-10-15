# Wakti — Coran, horaires de prière et calendrier hégirien

**Wakti (وقتي)** est une application web progressive (PWA) qui réunit la lecture et l’écoute du Coran, les horaires de prière et la consultation du calendrier hégirien dans une interface adaptée aux mobiles et aux ordinateurs.

<p align="center">
  <a href="https://wakti-ashen.vercel.app/"><strong>Ouvrir Wakti</strong></a>
  ·
  <a href="https://github.com/WissemAttouf/Wakti"><strong>Code source</strong></a>
</p>

## Présentation

Le projet associe une interface responsive à des fonctionnalités du navigateur comme l’installation en PWA, la mise en cache via un service worker et la sauvegarde locale de préférences. Les données du Coran, des horaires de prière et des récitations dépendent de fournisseurs externes.

## Fonctionnalités

### Lecture et écoute du Coran
- Parcourir les 114 sourates.
- Écouter des récitations avec contrôles de lecture, navigation dans les versets et sélection du récitant.
- Reprendre la lecture et gérer des favoris et des marque-pages.
- Utiliser des options de répétition pour accompagner la mémorisation.
- Consulter le texte dans une vue de lecture inspirée du Mushaf.

### Horaires de prière et habitudes quotidiennes
- Afficher les horaires en fonction d’un lieu sélectionné.
- Choisir les paramètres de calcul disponibles dans l’application.
- Suivre la progression quotidienne des prières.
- Configurer les rappels et préférences de notification pris en charge.

### Calendrier
- Consulter les dates grégoriennes et hégiriennes.
- Naviguer entre les mois et sélectionner une date.
- Ajuster le paramètre de date hégirienne disponible.

### Expérience utilisateur
- Mise en page responsive.
- Thèmes clair et sombre et options d’apparence.
- Application installable grâce au manifeste PWA.
- Mise en cache de ressources avec un service worker.
- Sauvegarde locale des préférences et de la progression.
- Interface en français et typographie adaptée au contenu arabe.

## Technologies

| Domaine | Technologies |
|---|---|
| Interface | HTML5, CSS3, JavaScript moderne |
| Application progressive | Web App Manifest, Service Worker, Cache API |
| Déploiement | Vercel |
| Outils | Node.js 20+, npm |
| Données du Coran et des prières | AlQuran Cloud, Aladhan, Islamic Network CDN |
| Audio | Fournisseurs de récitations et endpoint proxy audio |
| Packages serveur optionnels | web-push, @upstash/redis, @vercel/kv |

L’application repose principalement sur des technologies web natives et des modules JavaScript. La disponibilité des données et de l’audio dépend des services externes intégrés.

## Architecture

- `index.html` — structure principale et métadonnées.
- `css/style.css` — styles, thèmes et adaptation responsive.
- `js/app.js` — navigation, expérience Coran, horaires, calendrier et préférences.
- `sw.js` — stratégies de mise en cache.
- `manifest.webmanifest` — métadonnées d’installation et icônes.
- `vercel.json` — paramètres de déploiement et en-têtes.
- `package.json` — métadonnées et scripts.
- `api/` — endpoints serveur utilisés par l’application.

## Lancer le projet localement

### Prérequis
- Node.js 20 ou plus récent
- npm
- Git

### Installation

```bash
git clone https://github.com/WissemAttouf/Wakti.git
cd Wakti
npm install
```

Consultez `package.json` pour les scripts disponibles et les variables d’environnement requises. Les fonctionnalités reposant sur des services externes peuvent nécessiter une configuration complémentaire.

## Démonstration

- **Application :** [wakti-ashen.vercel.app](https://wakti-ashen.vercel.app/)
- **Code source :** [WissemAttouf/Wakti](https://github.com/WissemAttouf/Wakti)

## Auteur

**Wissem Attouf** — Ingénieur logiciel | Développeur Full Stack  
[GitHub](https://github.com/WissemAttouf) · [LinkedIn](https://www.linkedin.com/in/wissem-attouf-452509226/) · [Portfolio](https://wissem-portfolio.vercel.app/) · [E-mail](mailto:wattouf35@gmail.com)
