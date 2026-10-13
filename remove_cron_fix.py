#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('vercel.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

if 'crons' in config:
    del config['crons']
    with open('vercel.json', 'w', encoding='utf-8', newline='\n') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print('OK crons supprimes')
else:
    print('Pas de crons')
