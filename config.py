"""
Config POCUS Weekly Digest — versione sicura per repo pubblico
Tutte le credenziali vengono dai GitHub Secrets / variabili d'ambiente
"""

import os

ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL    = "claude-sonnet-5"
GMAIL_USER         = os.environ.get("GMAIL_USER_POCUS", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
NCBI_TOOL          = "pocus_weekly_digest_torino"

# URL PUBBLICO del logo (vuoto = nessun logo). Deve puntare a un file immagine
# raggiungibile pubblicamente (le email non supportano immagini locali/base64).
LOGO_URL           = "https://raw.githubusercontent.com/areacriticaprontosoccorso/newsletter-pocus/main/logo.jpg"

RIVISTE = [
    {"nome": "New England Journal of Medicine", "nlmta": "N Engl J Med",       "issn": "0028-4793"},
    {"nome": "The Lancet",                      "nlmta": "Lancet",             "issn": "0140-6736"},
    {"nome": "JAMA",                            "nlmta": "JAMA",               "issn": "0098-7484"},
    {"nome": "BMJ",                             "nlmta": "BMJ",                "issn": "0959-8138"},
    {"nome": "Circulation",                     "nlmta": "Circulation",        "issn": "0009-7322"},
    {"nome": "Chest",                           "nlmta": "Chest",              "issn": "0012-3692"},
    {"nome": "Annals of Emergency Medicine",    "nlmta": "Ann Emerg Med",      "issn": "0196-0644"},
    {"nome": "Critical Care Medicine",          "nlmta": "Crit Care Med",      "issn": "0090-3493"},
    {"nome": "Intensive Care Medicine",         "nlmta": "Intensive Care Med", "issn": "0342-4642"},
    {"nome": "Resuscitation",                   "nlmta": "Resuscitation",      "issn": "0300-9572"},
    {"nome": "Academic Emergency Medicine",     "nlmta": "Acad Emerg Med",     "issn": "1069-6563"},
    {"nome": "Emergency Medicine Journal",      "nlmta": "Emerg Med J",        "issn": "1472-0205"},
]

ARTICOLI_FINALI      = 5
GIORNI_RICERCA       = 7

NOME_NEWSLETTER     = "POCUS Weekly Digest"
NOME_SERVIZIO       = "Area Critica e Pronto Soccorso · San Giovanni Bosco · Torino"
COLOR_ACCENT        = "#0a6e8a"
COLOR_DARK          = "#1a2a30"
NEWSLETTER_PAGE_URL = "https://areacriticaprontosoccorso.github.io/newsletter-pocus/"

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "newsletter_pocus.log")

# ─── Prompt Claude ───────────────────────────────────────────

# Sintesi di TUTTI gli articoli in una sola chiamata API.
PROMPT_SINTESI_MULTI = """Sei un medico di Area Critica e Pronto Soccorso italiano esperto in ecografia clinica (POCUS).

Analizza OGNI articolo della lista e produci per ciascuno, in italiano:
1. SINTESI: 3-4 frasi che rispondano a — domanda clinica, risultato principale (con i numeri chiave), impatto per la pratica ecografica in PS/ICU
2. RILEVANZA: una sola frase sulla rilevanza pratica per l'ecografia bedside in Pronto Soccorso

Attieniti SOLO ai dati dell'abstract: non aggiungere, non inferire, non inventare.
NON alterare numeri, dosi, unita di misura, percentuali.

ARTICOLI:
{articoli}

Rispondi SOLO in questo formato, ripetuto per ogni articolo, nello stesso ordine
della lista, senza alcun altro testo prima o dopo:

### PMID: [pmid]
SINTESI: [testo]
RILEVANZA: [testo]"""

# Sintesi di un singolo articolo (fallback se dal multi manca qualcosa).
PROMPT_SINTESI = """Sei un medico di Area Critica e Pronto Soccorso italiano esperto in ecografia clinica (POCUS).

Analizza questo articolo e produci in italiano:
1. SINTESI: 3-4 frasi che rispondano a — domanda clinica, risultato principale, impatto per la pratica ecografica in PS/ICU
2. RILEVANZA: una sola frase sulla rilevanza pratica per l'ecografia bedside in Pronto Soccorso

Articolo:
Titolo: {titolo}
Autori: {autori}
Rivista: {rivista} ({data})
Abstract: {abstract}

Rispondi SOLO in questo formato:
SINTESI: [testo]
RILEVANZA: [testo]"""

PROMPT_FILTRO_POCUS = """Sei un medico di Area Critica e Pronto Soccorso italiano esperto in ecografia clinica (POCUS).

Dalla lista qui sotto, seleziona i {n} articoli piu rilevanti per la pratica della
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

Restituisci SOLO una lista di {n} PMID, uno per riga, in ordine di rilevanza decrescente.
Nessun commento, nessuna spiegazione, solo i {n} PMID.

Esempio output:
12345678
23456789
34567890
45678901
56789012"""


def valida_config():
    mancanti = []
    if not ANTHROPIC_API_KEY:  mancanti.append("ANTHROPIC_API_KEY")
    if not GMAIL_USER:         mancanti.append("GMAIL_USER_POCUS")
    if not GMAIL_APP_PASSWORD: mancanti.append("GMAIL_APP_PASSWORD")
    if mancanti:
        raise RuntimeError(
            f"Variabili d'ambiente mancanti: {', '.join(mancanti)}.\n"
            "Configurale nei GitHub Secrets."
        )
    return True
