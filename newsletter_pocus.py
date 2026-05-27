"""
POCUS Weekly Digest — Newsletter ecografia d'urgenza
Emergency Ultrasound School in Turin, San Giovanni Bosco, Torino
Comando: python newsletter_pocus.py
"""

import os
import re
import json
import time
import logging
import base64
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone

import config as cfg

DESTINATARI_FISSI = [
    "francesco.panero@aslcittaditorino.it",
    "pietro.tizzani@aslcittaditorino.it",
    "jacopo.pieroni@aslcittaditorino.it",
    "marcella.converso@aslcittaditorino.it",
    "valeria.milazzo@aslcittaditorino.it",
    "manuela.valle@aslcittaditorino.it",
    "giulia.cavalot@aslcittaditorino.it",
    "marta.cravino@aslcittaditorino.it",
    "sara.delcolle@aslcittaditorino.it",
    "paolo.petitti@aslcittaditorino.it",
    "immacolata.andria@aslcittaditorino.it",
    "massimo.perotto@gmail.com",
    "elvira.fanelli@aslcittaditorino.it",
    "daniela.viscovo@aslcittaditorino.it",
]


def carica_destinatari():
    try:
        sub_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "subscribers.json")
        with open(sub_path, encoding="utf-8") as f:
            subs = json.load(f)
        emails_sub = [
            s["email"].strip().lower()
            for s in subs
            if "@" in s.get("email", "") and " " not in s.get("email", "")
        ]
        tutti = list(DESTINATARI_FISSI)
        fissi_lower = {e.lower() for e in DESTINATARI_FISSI}
        for e in emails_sub:
            if e not in fissi_lower:
                tutti.append(e)
        print(f"Destinatari totali: {len(tutti)} ({len(DESTINATARI_FISSI)} fissi + {len(tutti) - len(DESTINATARI_FISSI)} subscribers)")
        return tutti
    except Exception as e:
        print(f"Errore carica subscribers: {e} — uso solo destinatari fissi")
        return list(DESTINATARI_FISSI)


DESTINATARI = carica_destinatari()

RIVISTE_POCUS = [
    {"nome": "Journal of Ultrasound in Medicine",               "nlmta": "J Ultrasound Med",         "issn": "0278-4297"},
    {"nome": "Ultrasound in Medicine and Biology",              "nlmta": "Ultrasound Med Biol",      "issn": "0301-5629"},
    {"nome": "Journal of the American Society of Echocardiography", "nlmta": "J Am Soc Echocardiogr", "issn": "0894-7317"},
    {"nome": "Critical Ultrasound Journal",                     "nlmta": "Crit Ultrasound J",        "issn": "2036-3176"},
    {"nome": "Ultrasound Journal",                              "nlmta": "Ultrasound J",             "issn": "2524-8987"},
]

TUTTE_RIVISTE = RIVISTE_POCUS + cfg.RIVISTE
ARTICOLI_FINALI = 5
COLOR_ACCENT = "#0a6e8a"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(cfg.LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("newsletter_pocus")


def numero_settimana():
    now = datetime.now()
    mesi = ["Gennaio","Febbraio","Marzo","Aprile","Maggio","Giugno",
            "Luglio","Agosto","Settembre","Ottobre","Novembre","Dicembre"]
    return {
        "settimana": now.isocalendar()[1],
        "anno":      now.year,
        "giorno":    now.day,
        "mese":      mesi[now.month - 1],
    }


def fetch_url(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": cfg.NCBI_TOOL})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            log.warning(f"Tentativo {attempt+1}/3 fallito: {e}")
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Fetch fallito: {url}")


NS = {"dc": "http://purl.org/dc/elements/1.1/"}


def url_rss_pubmed(issn):
    return f"https://pubmed.ncbi.nlm.nih.gov/rss/journals/{issn}/?limit=20&utm_campaign=journals"


def parse_pubdate(s):
    if not s:
        return None
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(s)
    except Exception:
        return None


def estrai_abstract_da_description(desc):
    if not desc:
        return ""
    testo = re.sub(r"<[^>]+>", " ", desc)
    testo = testo.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    testo = re.sub(r"PMID:\s*\d+.*$", "", testo, flags=re.IGNORECASE)
    testo = re.sub(r"DOI:\s*[\w./-]+", "", testo, flags=re.IGNORECASE)
    testo = re.sub(r"\s+", " ", testo).strip()
    return testo[:2500]


def estrai_pmid(item):
    link_el = item.find("link")
    if link_el is not None and link_el.text:
        m = re.search(r"/(\d{7,9})/?", link_el.text)
        if m:
            return m.group(1)
    for ident in item.findall("dc:identifier", NS):
        if ident.text and ident.text.startswith("pmid:"):
            return ident.text.replace("pmid:", "").strip()
    return ""


def estrai_doi(item):
    for ident in item.findall("dc:identifier", NS):
        if ident.text and ident.text.startswith("doi:"):
            return ident.text.replace("doi:", "").strip()
    return ""


def estrai_autori(item):
    creators = item.findall("dc:creator", NS)
    nomi = [c.text for c in creators if c.text]
    if not nomi:
        return ""
    if len(nomi) > 3:
        return ", ".join(nomi[:3]) + " et al."
    return ", ".join(nomi)


def fetch_feed(rivista):
    url = url_rss_pubmed(rivista["issn"])
    try:
        raw = fetch_url(url)
        root = ET.fromstring(raw)
    except Exception as e:
        log.error(f"  {rivista['nlmta']}: errore RSS {e}")
        return []
    articoli = []
    for item in root.findall(".//item"):
        titolo   = (item.findtext("title") or "").strip()
        link     = (item.findtext("link") or "").strip()
        desc     = item.findtext("description") or ""
        pubdate  = parse_pubdate(item.findtext("pubDate"))
        pmid     = estrai_pmid(item)
        doi      = estrai_doi(item)
        autori   = estrai_autori(item)
        abstract = estrai_abstract_da_description(desc)
        if not pmid or not titolo:
            continue
        articoli.append({
            "pmid":       pmid,
            "titolo":     titolo.rstrip("."),
            "autori":     autori,
            "rivista":    rivista["nome"],
            "data":       pubdate.strftime("%Y %b %d") if pubdate else "",
            "pubdate_dt": pubdate,
            "doi":        doi,
            "abstract":   abstract,
            "url":        link or f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        })
    log.info(f"  {rivista['nlmta']}: {len(articoli)} articoli dal feed")
    return articoli


def raccogli_candidati(giorni=7):
    log.info(f"Lettura RSS PubMed: ultimi {giorni} giorni su {len(TUTTE_RIVISTE)} riviste")
    cutoff = datetime.now(timezone.utc) - timedelta(days=giorni)
    tutti = []
    for rivista in TUTTE_RIVISTE:
        feed = fetch_feed(rivista)
        recenti = [
            a for a in feed
            if a["pubdate_dt"] and a["pubdate_dt"].astimezone(timezone.utc) >= cutoff
        ]
        log.info(f"    -> {len(recenti)} pubblicati negli ultimi {giorni}g")
        tutti.extend(recenti)
        time.sleep(0.3)
    seen = set()
    unici = []
    for a in tutti:
        if a["pmid"] not in seen:
            seen.add(a["pmid"])
            unici.append(a)
    con_abstract = [a for a in unici if a["abstract"] and len(a["abstract"]) > 100]
    log.info(f"Totale unici: {len(unici)}, con abstract: {len(con_abstract)}")
    return con_abstract


def chiama_opus(prompt, max_tokens=1500):
    payload = json.dumps({
        "model":      cfg.ANTHROPIC_MODEL,
        "max_tokens": max_tokens,
        "messages":   [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type":      "application/json",
            "x-api-key":         cfg.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.loads(r.read().decode("utf-8"))
        return data["content"][0]["text"].strip()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"Anthropic API errore {e.code}: {body[:400]}")


PROMPT_FILTRO_POCUS = """Sei un medico di Pronto Soccorso italiano esperto in ecografia clinica (POCUS).

Dalla lista qui sotto, seleziona i 5 articoli piu rilevanti per la pratica della
Point-of-Care Ultrasound (POCUS) in ambito di medicina d'urgenza, emergenza,
rianimazione e terapia intensiva.

INCLUDI articoli su:
- POCUS in PS e area critica (FAST, e-FAST, ecografia polmonare, ecocardiografia bedside)
- Ecografia procedurale (accessi vascolari eco-guidati, toracentesi, paracentesi, blocchi nervosi)
- Nuove applicazioni ecografiche in emergenza
- Validazione di protocolli ecografici (RUSH, BLUE, FALLS, etc.)
- Ecografia in rianimazione (valutazione emodinamica, VCI, contrattilita)
- Training e competenze ecografiche in medicina d'urgenza
- Ecografia muscoloscheletrica d'urgenza
- Ecografia nel trauma

ESCLUDI:
- Ecografia ostetrica di routine
- Ecocardiografia ambulatoriale avanzata (non bedside/emergenza)
- Imaging radiologico non ecografico
- Case reports, lettere, errata, commenti, corrispondenza
- Ricerca di base senza implicazioni cliniche

ARTICOLI CANDIDATI:
{articoli}

Restituisci SOLO una lista di 5 PMID, uno per riga, in ordine di rilevanza decrescente.
Nessun commento, nessuna spiegazione, solo i 5 PMID.

Esempio output:
12345678
23456789
34567890
45678901
56789012"""


def filtra_top_articoli(candidati):
    if len(candidati) <= ARTICOLI_FINALI:
        return candidati
    blocchi = []
    for a in candidati:
        blocchi.append(
            f"PMID: {a['pmid']}\n"
            f"RIVISTA: {a['rivista']} ({a['data']})\n"
            f"TITOLO: {a['titolo']}\n"
            f"ABSTRACT: {a['abstract'][:700]}"
        )
    prompt = PROMPT_FILTRO_POCUS.format(articoli="\n\n---\n\n".join(blocchi))
    log.info(f"Opus filtra {len(candidati)} -> {ARTICOLI_FINALI}")
    risposta = chiama_opus(prompt, max_tokens=200)
    pmids_sel = re.findall(r"\b\d{7,9}\b", risposta)[:ARTICOLI_FINALI]
    log.info(f"Opus selezionati: {pmids_sel}")
    map_pmid = {a["pmid"]: a for a in candidati}
    selezionati = [map_pmid[p] for p in pmids_sel if p in map_pmid]
    return selezionati


def sintetizza_articolo(art):
    prompt = cfg.PROMPT_SINTESI.format(
        titolo=art["titolo"],
        autori=art["autori"],
        rivista=art["rivista"],
        data=art["data"],
        abstract=art["abstract"][:2000] if art["abstract"] else "(non disponibile)",
    )
    try:
        risposta = chiama_opus(prompt, max_tokens=600)
        sintesi_m   = re.search(r"^SINTESI:\s*([\s\S]+?)(?=\nRILEVANZA:)", risposta, re.MULTILINE)
        rilevanza_m = re.search(r"^RILEVANZA:\s*(.+)", risposta, re.MULTILINE)
        art["sintesi_it"] = sintesi_m.group(1).strip() if sintesi_m else risposta[:400]
        art["rilevanza"]  = rilevanza_m.group(1).strip() if rilevanza_m else ""
    except Exception as e:
        log.error(f"Sintesi fallita PMID {art['pmid']}: {e}")
        art["sintesi_it"] = ""
        art["rilevanza"]  = ""
    return art


def build_html(articoli):
    wl = numero_settimana()
    arts_html = ""
    for i, a in enumerate(articoli):
        doi_link = (
            f'&nbsp;|&nbsp;<a href="https://doi.org/{a["doi"]}" '
            f'style="font-family:monospace;font-size:11px;color:#0a4d68;text-decoration:none;">&#x2197; DOI</a>'
        ) if a.get("doi") else ""
        sintesi_html = ""
        if a.get("sintesi_it"):
            rilevanza_html = (
                f'<br/><strong style="color:{COLOR_ACCENT};">{a["rilevanza"]}</strong>'
                if a.get("rilevanza") else ""
            )
            sintesi_html = f"""
            <div style="background:#f4f8f9;border-left:3px solid {COLOR_ACCENT};
                        padding:12px 16px;font-family:Georgia,serif;font-size:14px;
                        color:#2a2a2a;line-height:1.6;margin-bottom:12px;">
              {a['sintesi_it']}{rilevanza_html}
            </div>"""
        abstract_html = ""
        if a.get("abstract"):
            abstract_html = f"""
            <details style="margin-bottom:10px;">
              <summary style="font-family:monospace;font-size:10px;color:#0a4d68;
                             cursor:pointer;letter-spacing:1px;text-transform:uppercase;
                             list-style:none;">&#x25B8; Abstract originale (EN)</summary>
              <p style="font-family:Georgia,serif;font-size:12px;color:#666;
                        line-height:1.65;margin-top:8px;padding:10px 12px;
                        background:#fafafa;border:1px solid #eee;">{a['abstract']}</p>
            </details>"""
        arts_html += f"""
        <tr>
          <td style="padding:28px 32px 24px;border-bottom:1px solid #e0e8eb;">
            <div style="margin-bottom:10px;">
              <span style="font-family:monospace;font-size:12px;color:{COLOR_ACCENT};font-weight:700;">{str(i+1).zfill(2)}</span>
              <span style="font-family:monospace;font-size:11px;color:#aaa;margin-left:8px;">{a['rivista']} &middot; {a['data']}</span>
            </div>
            <a href="{a['url']}" style="font-family:Georgia,serif;font-size:19px;font-weight:700;
                                        color:#1a1a1a;text-decoration:none;line-height:1.35;
                                        display:block;margin-bottom:6px;">{a['titolo']}</a>
            <div style="font-family:monospace;font-size:12px;color:#999;font-style:italic;margin-bottom:14px;">{a['autori']}</div>
            {sintesi_html}
            {abstract_html}
            <div>
              <a href="{a['url']}" style="font-family:monospace;font-size:11px;color:#0a4d68;text-decoration:none;">&#x2197; PubMed {a['pmid']}</a>
              {doi_link}
            </div>
          </td>
        </tr>"""

    riviste_pocus_str = " &middot; ".join(r["nlmta"] for r in RIVISTE_POCUS[:4])

    return f"""<!DOCTYPE html>
<html lang="it">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{cfg.NOME_NEWSLETTER}</title></head>
<body style="margin:0;padding:0;background:#eaf0f2;">
<table width="100%" cellpadding="0" cellspacing="0" bgcolor="#eaf0f2">
  <tr><td align="center" style="padding:32px 16px;">
    <table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;">
      <tr>
        <td style="background:{cfg.COLOR_DARK};padding:0;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr><td style="background:{COLOR_ACCENT};height:4px;"></td></tr>
            <tr>
              <td style="padding:28px 32px 24px;">
                <div style="font-family:monospace;font-size:10px;color:#778;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">
                  {cfg.NOME_SERVIZIO}
                </div>
                <h1 style="font-family:Georgia,serif;font-size:32px;color:#ffffff;margin:0 0 6px;font-weight:700;letter-spacing:-0.5px;">
                  POCUS<br/>
                  <em style="color:{COLOR_ACCENT};font-style:italic;">Weekly Digest</em>
                </h1>
                <div style="font-family:monospace;font-size:11px;color:#667;">
                  Settimana {wl['settimana']} &middot; {wl['giorno']} {wl['mese']} {wl['anno']} &middot; {len(articoli)} articoli
                </div>
              </td>
              <td style="padding:28px 32px 24px;text-align:right;vertical-align:top;">
                <div style="font-family:monospace;font-size:52px;font-weight:700;color:#2a3a40;letter-spacing:-3px;line-height:1;">
                  {str(wl['settimana']).zfill(2)}
                </div>
                <div style="font-family:monospace;font-size:10px;color:#556;letter-spacing:3px;">WEEK</div>
              </td>
            </tr>
          </table>
        </td>
      </tr>
      <tr>
        <td style="background:#f0f5f7;padding:12px 32px;border-bottom:2px solid {cfg.COLOR_DARK};">
          <span style="font-family:monospace;font-size:10px;color:#889;letter-spacing:1px;">
            POCUS: {riviste_pocus_str} &middot; Generaliste: NEJM &middot; Lancet &middot; JAMA &middot; e altre
          </span>
        </td>
      </tr>
      <tr><td style="background:#ffffff;"><table width="100%" cellpadding="0" cellspacing="0">{arts_html}</table></td></tr>
      <tr>
        <td style="background:{cfg.COLOR_DARK};padding:22px 32px;">
          <p style="font-family:monospace;font-size:10px;color:#556;margin:0;line-height:1.8;">
            Generato con Claude Opus 4.5 (Anthropic) &middot; Fonte dati: PubMed RSS feeds<br/>
            Le sintesi sono prodotte da AI e devono essere verificate prima dell'applicazione clinica.<br/>
            Per cancellarsi rispondere con oggetto UNSUBSCRIBE.
          </p>
        </td>
      </tr>
    </table>
  </td></tr>
</table></body></html>"""


def invia_email(oggetto, html):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build as gmail_build

    token_json = os.environ.get("GMAIL_TOKEN_POCUS", "")
    if not token_json:
        log.error("GMAIL_TOKEN_POCUS non trovato nei secrets")
        return False

    token_data = json.loads(token_json)

    creds = Credentials(
        token=token_data['token'],
        refresh_token=token_data['refresh_token'],
        token_uri=token_data['token_uri'],
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        scopes=token_data['scopes'],
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = oggetto
    msg["From"]    = f"POCUS Weekly Digest <{cfg.GMAIL_USER}>"
    msg["To"]      = ", ".join(DESTINATARI)

    msg.attach(MIMEText(f"POCUS Weekly Digest — {oggetto}\nApri in HTML.", "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        service = gmail_build('gmail', 'v1', credentials=creds)
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId='me', body={'raw': raw}).execute()
        log.info(f"Email inviata a {len(DESTINATARI)} destinatari")
        return True
    except Exception as e:
        log.error(f"Invio fallito: {e}")
        return False


def main():
    cfg.valida_config()
    wl = numero_settimana()
    log.info(f"=== POCUS Weekly Digest — settimana {wl['settimana']}/{wl['anno']} ===")
    log.info(f"=== Destinatari: {', '.join(DESTINATARI)} ===")

    candidati = raccogli_candidati(giorni=7)

    if len(candidati) < ARTICOLI_FINALI + 3:
        log.warning(f"Solo {len(candidati)} candidati a 7 giorni — estendo a 14 giorni")
        candidati = raccogli_candidati(giorni=14)

    if not candidati:
        log.error("Nessun articolo trovato nemmeno a 14 giorni")
        return False

    selezionati = filtra_top_articoli(candidati)
    log.info(f"Selezionati {len(selezionati)} articoli finali")

    if not selezionati:
        log.error("Filtro Opus non ha selezionato nessun articolo")
        return False

    log.info("Sintesi con Claude Opus…")
    for i, art in enumerate(selezionati):
        log.info(f"  Sintesi {i+1}/{len(selezionati)}: PMID {art['pmid']}")
        selezionati[i] = sintetizza_articolo(art)
        time.sleep(1)

    html = build_html(selezionati)

    oggetto = f"POCUS Weekly Digest — Settimana {wl['settimana']}/{wl['anno']}"
    ok = invia_email(oggetto, html)
    log.info("=== OK ===" if ok else "=== FALLITO ===")
    return ok


if __name__ == "__main__":
    main()
