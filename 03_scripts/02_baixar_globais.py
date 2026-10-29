# -*- coding: utf-8 -*-
"""Etapa 2: aquisicao dos conjuntos de dados globais."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
u = import_module('00_util_download')
Z = "https://zenodo.org/api/records/3862995/files/{}/content"

D = [
# --- Orcamento do nivel do mar e impressoes digitais (Frederikse et al., 2020, Nature) ---
(Z.format("global_basin_timeseries.xlsx"), "frederikse2020/global_basin_timeseries.xlsx",
 "Series globais e por bacia do nivel do mar e de cada processo contribuinte, 1900-2018",
 "Frederikse et al. (2020), Nature 584:393-397, DOI 10.5281/zenodo.3862995"),
(Z.format("region_info.xlsx"), "frederikse2020/region_info.xlsx",
 "Lista de maregrafos usados e estimativas de movimento vertical do terreno (VLM) por regiao",
 "Frederikse et al. (2020), DOI 10.5281/zenodo.3862995"),
(Z.format("GrIS.nc"), "frederikse2020/GrIS.nc",
 "Padrao espacial do nivel relativo do mar devido a perda de massa da Groenlandia (impressao digital)",
 "Frederikse et al. (2020), DOI 10.5281/zenodo.3862995"),
(Z.format("AIS.nc"), "frederikse2020/AIS.nc",
 "Padrao espacial do nivel relativo do mar devido a perda de massa da Antartica (impressao digital)",
 "Frederikse et al. (2020), DOI 10.5281/zenodo.3862995"),
(Z.format("glac.nc"), "frederikse2020/glac.nc",
 "Padrao espacial do nivel relativo do mar devido as geleiras de montanha",
 "Frederikse et al. (2020), DOI 10.5281/zenodo.3862995"),
(Z.format("tws.nc"), "frederikse2020/tws.nc",
 "Padrao espacial do nivel relativo do mar devido ao armazenamento de agua continental",
 "Frederikse et al. (2020), DOI 10.5281/zenodo.3862995"),
(Z.format("total.nc"), "frederikse2020/total.nc",
 "Padrao espacial combinado de todos os processos baristaticos",
 "Frederikse et al. (2020), DOI 10.5281/zenodo.3862995"),
(Z.format("steric.nc"), "frederikse2020/steric.nc",
 "Media e desvio padrao das anomalias estericas (termo e halosterica), 1957-2018",
 "Frederikse et al. (2020), DOI 10.5281/zenodo.3862995"),
(Z.format("README"), "frederikse2020/README", "Documentacao do conjunto de dados",
 "Frederikse et al. (2020), DOI 10.5281/zenodo.3862995"),

# --- Altimetria por satelite ---
("https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/slr/slr_sla_gbl_free_all_66.csv",
 "altimetria/noaa_gmsl_66S66N_sazonal_removida.csv",
 "Anomalia do nivel medio global do mar por altimetria de satelite (66S-66N), sinal sazonal removido",
 "NOAA/NESDIS Laboratory for Satellite Altimetry"),
("https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/slr/slr_sla_gbl_keep_all_66.csv",
 "altimetria/noaa_gmsl_66S66N_sazonal_mantida.csv",
 "Idem, com sinal sazonal mantido", "NOAA/NESDIS Laboratory for Satellite Altimetry"),

# --- Temperatura global ---
("https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv", "temperatura/gistemp_v4_global.csv",
 "Anomalia de temperatura media global da superficie terra-oceano (GISTEMP v4), base 1951-1980",
 "NASA Goddard Institute for Space Studies (GISTEMP Team, 2026)"),
("https://www.metoffice.gov.uk/hadobs/hadcrut5/data/HadCRUT.5.0.2.0/analysis/diagnostics/HadCRUT.5.0.2.0.analysis.summary_series.global.annual.csv",
 "temperatura/hadcrut5_global_anual.csv",
 "Anomalia de temperatura media global anual (HadCRUT5), base 1961-1990, com IC 95%",
 "Morice et al. (2021), Met Office Hadley Centre / Climatic Research Unit"),

# --- Conteudo de calor oceanico ---
("https://www.ncei.noaa.gov/data/oceans/woa/DATA_ANALYSIS/3M_HEAT_CONTENT/DATA/basin/yearly/h22-w0-700m.dat",
 "oceano/ncei_ohc_0-700m_anual.dat", "Conteudo de calor oceanico 0-700 m, anual, global e por hemisferio",
 "NOAA NCEI (Levitus et al., 2012)"),
("https://www.ncei.noaa.gov/data/oceans/woa/DATA_ANALYSIS/3M_HEAT_CONTENT/DATA/basin/yearly/h22-w0-2000m.dat",
 "oceano/ncei_ohc_0-2000m_anual.dat", "Conteudo de calor oceanico 0-2000 m, anual",
 "NOAA NCEI (Levitus et al., 2012)"),

# --- Nivel do mar historico pre-altimetria ---
("https://www.cmar.csiro.au/sealevel/downloads/church_white_gmsl_2011_up.zip",
 "altimetria/church_white_gmsl_2011.zip",
 "Reconstrucao do nivel medio global do mar 1880-2013 a partir de maregrafos",
 "Church e White (2011), Surveys in Geophysics 32:585-602 / CSIRO"),

# --- Movimento vertical do terreno por GNSS ---
("https://geodesy.unr.edu/velocities/midas.IGS14.txt", "gnss/ngl_midas_IGS14.txt",
 "Velocidades MIDAS de todas as estacoes GNSS globais no referencial IGS14 (inclui componente vertical)",
 "Blewitt et al. (2016), Nevada Geodetic Laboratory"),
]

print(f"Baixando {len(D)} conjuntos de dados\n")
ok = 0
for url, dest, desc, fonte in D:
    if u.try_get(url, dest, desc, fonte): ok += 1
print(f"\n{ok}/{len(D)} conjuntos obtidos")
