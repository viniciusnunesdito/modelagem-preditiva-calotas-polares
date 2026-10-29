# -*- coding: utf-8 -*-
"""Etapa 3: projecoes oficiais do IPCC AR6 por localidade (decompostas por processo)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
u = import_module('00_util_download')

EST = {542:'IMBITUBA', 556:'RECIFE', 578:'SALVADOR', 580:'BELEM', 726:'CANANEIA', 1032:'ILHA_FISCAL'}
API = "https://sealevel.nasa.gov/projection-passthru/?psmsl_id={}"
FONTE = ("Garner et al. (2021), IPCC AR6 Sea Level Projections, DOI 10.5281/zenodo.6382554; "
         "servido pelo NASA Sea Level Projection Tool")

u.try_get("https://sealevel.nasa.gov/projection-passthru/?markers=true",
          "ipcc_ar6/marcadores_estacoes.geojson",
          "Metadados de todas as localidades disponiveis na ferramenta IPCC AR6", FONTE)

for pid, nome in EST.items():
    p = u.try_get(API.format(pid), f"ipcc_ar6/ar6_psmsl_{pid}.json",
                  f"Projecoes IPCC AR6 de nivel relativo do mar, decompostas por processo, "
                  f"cenario e percentil, para a estacao {pid} ({nome})", FONTE)
    if p:
        d = json.load(open(p, encoding='utf-8'))
        proc = sorted({r['process'] for r in d}); scen = sorted({r['scenario'] for r in d})
        conf = sorted({r['confidence'] for r in d}); tip = sorted({r['type'] for r in d})
        print(f"      {nome}: {len(d)} registros | tipos={tip}")
        print(f"      processos={proc}")
        print(f"      cenarios={scen} | confianca={conf}")
