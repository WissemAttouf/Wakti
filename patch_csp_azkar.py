#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

print("=== AJOUT DE L'API AZKAR A LA CSP ===\n")

with open('vercel.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Trouver et modifier la CSP
for rule in config.get('headers', []):
    if rule.get('source') == '/(.*)':
        for h in rule.get('headers', []):
            if h.get('key') == 'Content-Security-Policy':
                csp = h['value']
                
                # Domaines à ajouter
                NEW_DOMAINS = [
                    'https://raw.githubusercontent.com',
                    'https://api.bonyanoss.org',
                    'https://dua-dhikr.vercel.app'
                ]
                
                changes = []
                for domain in NEW_DOMAINS:
                    if domain not in csp:
                        # Ajouter dans connect-src
                        csp = csp.replace(
                            "connect-src 'self'",
                            "connect-src 'self' " + domain,
                            1  # une seule fois
                        )
                        changes.append(domain)
                
                if changes:
                    h['value'] = csp
                    print("Domaines ajoutes a connect-src :")
                    for c in changes:
                        print(f"  ✅ {c}")
                else:
                    print("Tous les domaines sont deja dans la CSP")
                
                break

with open('vercel.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

# Vérification
with open('vercel.json', 'r', encoding='utf-8') as f:
    content = f.read()

print("\n=== VERIFICATION ===")
for domain in ['raw.githubusercontent.com', 'api.bonyanoss.org']:
    if domain in content:
        print(f"  ✅ {domain} present")
    else:
        print(f"  ❌ {domain} manquant")

print("\n=== TERMINE ===")
print("Prochaine etape : npx vercel --prod --force")
