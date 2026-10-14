"""Ricerca POCUS in tutta PubMed tramite ESearch/EFetch (solo libreria standard).

Le date EDAT identificano nuovi record indicizzati: la data mostrata nel digest
resta quella di pubblicazione, quando disponibile. Ogni articolo candidato deve
poi superare il filtro clinico AI del programma principale.
"""
import json
import logging
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import config as cfg

log = logging.getLogger("newsletter_rss")

POCUS_QUERY = """(
    "point-of-care ultrasound"[tiab] OR "point of care ultrasound"[tiab]
    OR "point-of-care ultrasonography"[tiab] OR POCUS[tiab]
    OR "bedside ultrasound"[tiab] OR "emergency ultrasound"[tiab]
    OR "focused cardiac ultrasound"[tiab] OR "focused echocardiography"[tiab]
    OR "lung ultrasound"[tiab] OR "pleural ultrasound"[tiab]
    OR (("ultrasound-guided"[tiab] OR "ultrasound guided"[tiab]
         OR "ultrasonography-guided"[tiab])
        AND ("emergency"[tiab] OR "critical care"[tiab]
             OR "intensive care"[tiab] OR "resuscitation"[tiab]
             OR "vascular access"[tiab] OR "central venous"[tiab]
             OR "thoracentesis"[tiab] OR "nerve block"[tiab]))
    OR eFAST[tiab] OR "extended focused assessment with sonography"[tiab]
    OR "focused assessment with sonography"[tiab]
    OR "RUSH protocol"[tiab] OR "BLUE protocol"[tiab]
    OR ("ultrasonography"[MeSH Terms] AND
        ("Emergency Service, Hospital"[MeSH Terms]
         OR "Critical Care"[MeSH Terms]
         OR "Emergency Medicine"[MeSH Terms]))
)"""

_RE_ULTRASUONO = re.compile(
    r"\b(?:pocus|ultraso(?:und|nography|nographic)|sonograph\w*|"
    r"echograph\w*|echocardiograph\w*|e-?fast)\b", re.I)
_RE_DIRETTO = re.compile(
    r"\bpocus\b|point[- ]of[- ]care.{0,28}ultraso|bedside.{0,18}ultraso|"
    r"emergency.{0,18}ultraso|focused cardiac ultraso|focused echocardio|"
    r"lung ultraso|pleural ultraso|focused assessment with sonography|"
    r"\be-?fast\b|\brush protocol\b|\bblue protocol\b", re.I)
_RE_CONTESTO = re.compile(
    r"emergency|critical(?:ly ill| care)|intensive care|resuscitat|"
    r"prehospital|pre-hospital|emergent|bedside|shock|cardiac arrest|"
    r"trauma|acute care|vascular access|central venous|thoracentesis|"
    r"paracentesis|pericardiocentesis|nerve block|regional anesth|"
    r"emergency physician|emergency department", re.I)


def potenzialmente_pocus(titolo, abstract):
    """Primo filtro sensibile: una vera conferma POCUS richiede SEMPRE il filtro AI."""
    testo = f"{titolo or ''} {abstract or ''}"
    return bool(_RE_DIRETTO.search(testo) or
                (_RE_ULTRASUONO.search(testo) and _RE_CONTESTO.search(testo)))


def _richiesta(url, dati=None):
    intestazione = {"User-Agent": f"{cfg.NCBI_TOOL} (POCUS digest)"}
    for tentativo in range(3):
        try:
            req = urllib.request.Request(url, data=dati, headers=intestazione)
            with urllib.request.urlopen(req, timeout=cfg.EFETCH_TIMEOUT) as response:
                return response.read()
        except Exception as exc:
            if tentativo == 2:
                raise RuntimeError(f"E-utilities NCBI irraggiungibile: {exc}") from exc
            log.warning("NCBI tentativo %s/3: %s", tentativo + 1, exc)
            time.sleep(2 ** tentativo)


def cerca_pmid(giorni):
    if not isinstance(giorni, int) or giorni < 1:
        raise ValueError("giorni deve essere un intero positivo")
    params = {
        "db": "pubmed", "term": " ".join(POCUS_QUERY.split()),
        "datetype": "edat", "reldate": giorni, "retmode": "json",
        "retmax": cfg.ESEARCH_RETMAX, "sort": "pub_date", "tool": cfg.NCBI_TOOL,
    }
    if cfg.NCBI_EMAIL:
        params["email"] = cfg.NCBI_EMAIL
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
           + urllib.parse.urlencode(params))
    data = json.loads(_richiesta(url).decode("utf-8"))
    result = data["esearchresult"]
    ids = result.get("idlist", [])
    count = int(result.get("count", 0))
    log.info("PubMed ESearch: %s hit in %s giorni, PMID recuperati %s",
             count, giorni, len(ids))
    if count > len(ids):
        log.warning("ESearch troncato: %s/%s PMID; aumentare ESEARCH_RETMAX",
                    len(ids), count)
    return ids


def _testo(elemento):
    return " ".join("".join(elemento.itertext()).split()) if elemento is not None else ""


def _data_articolo(articolo):
    """Data di pubblicazione, distinta da EDAT e da PubMedPubDate."""
    date_possibili = (articolo.findall("./ArticleDate")
                      + articolo.findall("./Journal/JournalIssue/PubDate"))
    for el in date_possibili:
        anno = (el.findtext("Year") or "").strip()
        mese = (el.findtext("Month") or "1").strip()
        giorno = (el.findtext("Day") or "1").strip()
        if not anno:
            medline = el.findtext("MedlineDate") or ""
            trovato = re.search(r"\b(?:19|20)\d{2}\b", medline)
            anno = trovato.group(0) if trovato else ""
        if not anno:
            continue
        try:
            m = int(mese) if mese.isdigit() else datetime.strptime(mese[:3].title(), "%b").month
            return datetime(int(anno), m, int(giorno), tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
    return None


def _estrai_articolo(el, gruppi):
    mc = el.find("./MedlineCitation")
    art = mc.find("./Article") if mc is not None else None
    if mc is None or art is None:
        return None
    pmid = (mc.findtext("./PMID") or "").strip()
    titolo = _testo(art.find("./ArticleTitle")).rstrip(".")
    if not pmid or not titolo:
        return None
    sezioni = []
    for parte in art.findall("./Abstract/AbstractText"):
        testo = _testo(parte)
        if testo:
            label = (parte.get("Label") or "").strip()
            sezioni.append((label + ": " if label else "") + testo)
    nome_rivista = (art.findtext("./Journal/Title") or
                    art.findtext("./Journal/ISOAbbreviation") or
                    "Rivista non disponibile")
    abbreviazione = (mc.findtext("./MedlineJournalInfo/MedlineTA") or
                     art.findtext("./Journal/ISOAbbreviation") or "").lower()
    nomi = []
    for autore in art.findall("./AuthorList/Author"):
        nome = " ".join(s for s in (autore.findtext("ForeName"), autore.findtext("LastName")) if s)
        if nome:
            nomi.append(nome)
    autori = ", ".join(nomi[:3]) + (" et al." if len(nomi) > 3 else "")
    doi = ""
    for id_el in el.findall("./PubmedData/ArticleIdList/ArticleId"):
        if id_el.get("IdType") == "doi":
            doi = (id_el.text or "").strip()
            break
    if not doi:
        for eid in art.findall("./ELocationID"):
            if eid.get("EIdType") == "doi":
                doi = (eid.text or "").strip()
                break
    data = _data_articolo(art)
    tipi = [_testo(t) for t in art.findall("./PublicationTypeList/PublicationType")]
    return {
        "pmid": pmid, "titolo": titolo, "autori": autori,
        "rivista": nome_rivista, "gruppo": gruppi.get(abbreviazione, "spec"),
        "data": data.strftime("%Y %b %d") if data else "",
        "pubdate_dt": data, "doi": doi, "abstract": " ".join(sezioni),
        "pubtypes": [t for t in tipi if t],
        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
    }


def cerca_articoli_pubmed(giorni=7):
    ids = cerca_pmid(giorni)
    if not ids:
        return []
    gruppi = {r["nlmta"].lower(): r["gruppo"] for r in cfg.RIVISTE}
    result = {}
    for i in range(0, len(ids), cfg.EFETCH_BATCH):
        lotto = ids[i:i + cfg.EFETCH_BATCH]
        params = {"db": "pubmed", "id": ",".join(lotto),
                  "retmode": "xml", "tool": cfg.NCBI_TOOL}
        if cfg.NCBI_EMAIL:
            params["email"] = cfg.NCBI_EMAIL
        dati = urllib.parse.urlencode(params).encode("utf-8")
        xml = _richiesta(cfg.EFETCH_URL, dati)
        root = ET.fromstring(xml)
        for el in root.findall("./PubmedArticle"):
            a = _estrai_articolo(el, gruppi)
            if a and a["pmid"] in lotto:
                result[a["pmid"]] = a
        time.sleep(0.4)  # senza chiave NCBI: max 3 richieste/s
    log.info("PubMed EFetch: %s/%s PMID con metadati", len(result), len(ids))
    return [result[pmid] for pmid in ids if pmid in result]
