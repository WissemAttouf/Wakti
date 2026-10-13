# Wakti — Quran, Prayer Times & Hijri Calendar

<p align="center">
  <strong>A thoughtful, installable web experience for Quran reading, recitation, prayer times, and the Islamic calendar.</strong>
  <br />
  Built with a focus on accessibility, responsive design, and a calm, distraction-conscious interface.
</p>

<p align="center">
  <a href="https://wakti-ashen.vercel.app/"><img src="https://img.shields.io/badge/Live%20Demo-Open%20Wakti-0E6A58?style=for-the-badge" alt="Live demo" /></a>
  <a href="https://github.com/WissemAttouf/Wakti"><img src="https://img.shields.io/badge/Source-GitHub-181717?style=for-the-badge&logo=github" alt="GitHub repository" /></a>
  <img src="https://img.shields.io/badge/Platform-PWA-5A45FF?style=for-the-badge" alt="Progressive Web App" />
  <img src="https://img.shields.io/badge/Runtime-Node.js%2020%2B-339933?style=for-the-badge&logo=nodedotjs&logoColor=white" alt="Node.js 20 or newer" />
</p>

---

## Overview

**Wakti** (وقتي) is a Progressive Web App that brings several everyday Islamic practices together in one responsive interface. Users can read and listen to the Quran, check prayer times for a selected location, and explore the Hijri and Gregorian calendars.

The project combines a carefully themed interface with browser capabilities such as local persistence, installability, and service-worker caching. It is designed to work on desktop and mobile screens, with dark and light appearance options.

**Try it:** [wakti-ashen.vercel.app](https://wakti-ashen.vercel.app/)  
**Explore the code:** [github.com/WissemAttouf/Wakti](https://github.com/WissemAttouf/Wakti)

## Key Features

### Quran reading and recitation
- Browse the 114 surahs and find content using the Quran browsing interface.
- Listen to Quran recitations with playback controls, verse navigation, and reciter selection.
- Resume reading/listening and manage bookmarks and favourite reciters.
- Use repeat and memorisation-support controls while learning verses.
- Explore Quran text in a Mushaf-style reading view.

### Prayer times and daily routine
- View prayer times based on a selected location.
- Configure calculation method and school settings where supported by the app.
- Track completed prayers and view daily progress.
- Enable in-app prayer reminders and notification preferences.

### Hijri and Gregorian calendar
- Browse dates in the Gregorian calendar alongside Hijri date information.
- Navigate calendar months and inspect individual dates.
- Adjust the Hijri date setting in the app.

### Product experience
- Responsive layout designed for mobile and desktop.
- Dark and light themes, with additional appearance presets.
- Installable PWA experience with app manifest, icons, and standalone display mode.
- Service-worker caching for the application shell, local images, and selected API responses.
- Local browser storage for preferences and personal progress.
- French interface copy and Arabic-focused typography for Quran content.

## Technology Stack

| Area | Technologies |
| --- | --- |
| Front end | HTML5, CSS3, modern JavaScript (ES modules) |
| App architecture | Client-side single-page navigation and modular UI behaviours |
| PWA | Web App Manifest, Service Worker, Cache API |
| Deployment | Vercel |
| Runtime / package tooling | Node.js 20+, npm |
| Quran and prayer data | AlQuran Cloud, Aladhan, Islamic Network CDN |
| Audio | Quran recitation audio providers, with an application audio-proxy endpoint |
| Optional server-side packages | `web-push`, `@upstash/redis`, `@vercel/kv` |

The project is primarily a lightweight web application rather than a framework-heavy front end. External services provide Quran/prayer data and recitation audio; availability and response behaviour can depend on those providers.

## Architecture at a Glance

- `index.html` — application shell, metadata, and main interface.
- `css/style.css` — design tokens, themes, layout, and responsive styling.
- `js/app.js` — client-side application logic, navigation, Quran experience, prayer times, calendar, and user preferences.
- `sw.js` — service worker and cache strategies.
- `manifest.webmanifest` — installability metadata, icons, and app shortcuts.
- `vercel.json` — deployment and response-header configuration.
- `package.json` — package metadata and developer/deployment scripts.
- `api/` — serverless API endpoints used by the application, including audio-related functionality.

## Run Locally

### Prerequisites
- Node.js **20 or newer**
- npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/WissemAttouf/Wakti.git
cd Wakti
```

### 2. Install dependencies

```bash
npm install
```

### 3. Start a local static server

The package provides a simple static-server script:

```bash
npm run serve
```

Open [http://localhost:3000](http://localhost:3000).

> **Note:** Some features rely on external APIs or Vercel serverless endpoints. For the closest match to the deployed application, use the Vercel CLI and run the project in the Vercel development environment. If a feature depends on a deployment-only endpoint, a plain static server may not reproduce it.

## Deploy to Vercel

1. Import the repository into [Vercel](https://vercel.com/), or link it with the Vercel CLI.
2. Keep the project root set to the repository root.
3. Review any environment variables required by enabled server-side integrations.
4. Deploy and test the production URL on both mobile and desktop.

The repository includes a `deploy` script for production and a `deploy:preview` script for preview deployments:

```bash
npm run deploy:preview
npm run deploy
```

Do not commit private API keys, tokens, or production credentials to Git.

## Quality and Engineering Notes

The project includes several practical web-platform considerations:

- **PWA fundamentals:** manifest, app icons, standalone display mode, and a service worker.
- **Caching:** separate cache handling for the application shell, local images, and selected external API responses.
- **Resilient requests:** shared JSON-fetching utilities include retry and timeout handling.
- **User preferences:** local storage is used for settings and progress that should persist between visits on the same browser.
- **Browser integration:** audio playback and media controls are designed around browser capabilities.
- **Security headers:** Vercel configuration defines a Content Security Policy and other response headers. Review the policy whenever adding new external providers or scripts.

External APIs and media hosts may change their availability, URL structure, or usage policies. Review their current documentation before extending the integration.

## Roadmap Ideas

Potential future improvements—not claims about current functionality—include:
- Add automated unit and end-to-end tests to the repository.
- Document accessibility checks and performance budgets.
- Add a concise contributor guide and issue templates.
- Provide a privacy page explaining what stays in browser storage and what is sent to external providers.
- Add documented screenshots and a feature walkthrough.

## Contributing

Suggestions, bug reports, and improvements are welcome. Before opening a pull request:

1. Keep changes focused and explain the user-facing impact.
2. Test the affected flows in a modern browser.
3. Check mobile layouts and both themes.
4. Verify that any new external resource is compatible with the Content Security Policy.
5. Never include credentials or personal data in commits.

## Author

**Wissem Attouf** — Software Engineer / Full-Stack Developer

- GitHub: [@WissemAttouf](https://github.com/WissemAttouf)
- Live project: [Wakti](https://wakti-ashen.vercel.app/)

---

<p align="center">
  <sub>Wakti — make space for what matters, one day at a time.</sub>
</p>
