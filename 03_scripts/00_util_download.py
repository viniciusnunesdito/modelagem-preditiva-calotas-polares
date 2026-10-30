"""Utilitario de download com cache e registro de proveniencia."""
import urllib.request, ssl, os, json, hashlib, datetime, time

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "01_dados_brutos")
LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "07_log_pesquisa", "proveniencia_dados.json")
# Contexto TLS com verificacao de certificado ATIVA. A integridade declarada no log de
# proveniencia depende de os bytes terem vindo do host indicado na URL: sem verificacao,
# a soma SHA-256 atesta apenas o que chegou, nao a origem. Os hosts usados neste trabalho
# (PSMSL, UHSLC, Zenodo, Met Office, NASA, NOAA/NESDIS, NCEI, NGL, IPCC) foram testados
# com verificacao ativa e nenhum apresenta erro de validacao de certificado.
CTX = ssl.create_default_context()
# User-Agent descritivo, e nao de navegador falsificado. Alem de ser a pratica correta para
# coleta automatizada em repositorios cientificos, e necessario: o Zenodo responde HTTP 403
# a cadeias de UA de navegador, o que fazia falhar silenciosamente o download do conjunto de
# Frederikse et al. (2020) -- justamente a fonte das impressoes digitais. Com o UA abaixo,
# todos os hosts do trabalho respondem HTTP 200.
UA = {'User-Agent': 'modelagem-preditiva-calotas-polares/1.0 (pesquisa academica; Python urllib)'}

def _log(entry):
    rec = []
    if os.path.exists(LOG):
        try: rec = json.load(open(LOG, encoding='utf-8'))
        except Exception: rec = []
    rec = [r for r in rec if r.get('arquivo') != entry['arquivo']]
    rec.append(entry)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    json.dump(rec, open(LOG, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

def _registrado(dest):
    """Ja existe entrada de proveniencia para este destino?"""
    if not os.path.exists(LOG):
        return False
    try:
        return any(r.get('arquivo') == dest for r in json.load(open(LOG, encoding='utf-8')))
    except Exception:
        return False


def get(url, dest, descricao="", fonte="", force=False, tries=3):
    """Baixa url -> 01_dados_brutos/dest, registrando hash e data de acesso."""
    path = os.path.join(RAW, dest)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path) and not force:
        # O arquivo ja esta em cache e nao sera rebaixado. Ainda assim garante-se que ele
        # tenha entrada no log: a versao anterior retornava aqui sem registrar nada, e por
        # isso arquivos baixados em sessao anterior ficavam fora da proveniencia.
        if not _registrado(dest):
            data = open(path, 'rb').read()
            _log({'arquivo': dest, 'url': url, 'descricao': descricao, 'fonte': fonte,
                  'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                  'acessado_em': datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat(),
                  'observacao': 'arquivo ja presente em cache; soma calculada a partir do '
                                'arquivo local e data de acesso tomada da data de modificacao'})
        return path
    last = None
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120, context=CTX)
            data = r.read()
            open(path, 'wb').write(data)
            _log({'arquivo': dest, 'url': url, 'descricao': descricao, 'fonte': fonte,
                  'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                  'acessado_em': datetime.datetime.now().isoformat(timespec='seconds')})
            return path
        except Exception as e:
            last = e; time.sleep(2 + 3*i)
    raise RuntimeError(f"falhou {url}: {type(last).__name__}: {last}")

def try_get(url, dest, descricao="", fonte=""):
    try:
        p = get(url, dest, descricao, fonte)
        print(f"  OK   {dest}  ({os.path.getsize(p)} bytes)")
        return p
    except Exception as e:
        print(f"  FALHA {dest}: {str(e)[:160]}")
        return None
