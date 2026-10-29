"""Utilitario de download com cache e registro de proveniencia."""
import urllib.request, ssl, os, json, hashlib, datetime, time

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "01_dados_brutos")
LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "07_log_pesquisa", "proveniencia_dados.json")
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'}

def _log(entry):
    rec = []
    if os.path.exists(LOG):
        try: rec = json.load(open(LOG, encoding='utf-8'))
        except Exception: rec = []
    rec = [r for r in rec if r.get('arquivo') != entry['arquivo']]
    rec.append(entry)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    json.dump(rec, open(LOG, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

def get(url, dest, descricao="", fonte="", force=False, tries=3):
    """Baixa url -> 01_dados_brutos/dest, registrando hash e data de acesso."""
    path = os.path.join(RAW, dest)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path) and not force:
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
