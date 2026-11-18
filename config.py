"""
POCUS Weekly Digest — Configurazione centralizzata
Emergency Ultrasound School in Turin, San Giovanni Bosco, Torino
Tutti i parametri configurabili in un solo posto.
Le credenziali vere stanno in variabili d'ambiente (secrets GitHub Actions).
"""
import os

# ═══════════════════════════════════════════════════════════════════════════════
# CREDENZIALI E DESTINATARI (letti da variabili d'ambiente — MAI hardcoded)
# ═══════════════════════════════════════════════════════════════════════════════
ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL    = "claude-sonnet-5"
# Invio via SMTP con password per le app: nessuna dipendenza da Google Cloud.
GMAIL_USER         = os.environ.get("GMAIL_USER_POCUS", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
# I destinatari sono l'unione di DESTINATARI_FISSI (nello script) e
# subscribers.json, gestita da carica_destinatari().

# Modalità prova a vuoto: esegue tutta la pipeline (feed, efetch, filtro, sintesi)
# ma NON invia l'email; scrive l'HTML su file e logga la selezione per esteso.
# Attivazione: DRY_RUN=1 (accettati anche true/yes/si).
DRY_RUN      = os.environ.get("DRY_RUN", "").strip().lower() in ("1", "true", "yes", "si")
DRY_RUN_FILE = "anteprima_digest.html"

# Modalità solo Facebook: esegue la pipeline e pubblica i post programmati, ma
# NON invia né email né Telegram. Ha effetto solo se DRY_RUN non è attivo.
SOLO_FACEBOOK = os.environ.get("SOLO_FACEBOOK", "").strip().lower() in ("1", "true", "yes", "si")
# Prova dell'invio su Instagram: stessa selezione e sintesi di una corsa vera, ma pubblica SOLO su
# Instagram (carosello e Reel veri, didascalia normale): niente mail, Telegram
# o Facebook. Attivazione: SOLO_INSTAGRAM=1. Ha effetto solo se DRY_RUN non e' attivo.
SOLO_INSTAGRAM = os.environ.get("SOLO_INSTAGRAM", "").strip().lower() in ("1", "true", "yes", "si")
# Solo podcast: stessa selezione e sintesi di una corsa vera, genera il podcast e lo manda SOLO a
# AVVISI_EMAIL (o, se manca, alla casella GMAIL_USER), con la mail come la vedrebbero gli iscritti.
# Niente iscritti, Telegram o social. Attivazione: SOLO_PODCAST=1.
SOLO_PODCAST = os.environ.get("SOLO_PODCAST", "").strip().lower() in ("1", "true", "yes", "si")
SOLO_PODCAST_A = os.environ.get("AVVISI_EMAIL", "").strip()
IG_PREFISSO_PROVA = ""      # vuoto: la didascalia e' quella di sempre (serve a recuperare un'uscita mancata)


# ═══════════════════════════════════════════════════════════════════════════════
# IMMAGINI DEGLI ARTICOLI
# ═══════════════════════════════════════════════════════════════════════════════
# Una scheda PNG per articolo, allegata all'email e utile per la condivisione.
# Gli abstract in inglese sono esclusi: senza, la scheda resta di altezza leggibile.
IMMAGINI_ABILITATE = True
IMG_DIR        = "immagini"
IMG_LARGHEZZA  = 720   # px CSS della scheda
IMG_SCALA      = 2     # device scale factor: 2 = testo nitido su schermi retina
IMG_TIMEOUT_MS = 20000
IMG_MAX_MB     = 20    # oltre questa soglia gli allegati vengono omessi

# ═══════════════════════════════════════════════════════════════════════════════
# PUBBLICAZIONE SU PAGINA FACEBOOK
# ═══════════════════════════════════════════════════════════════════════════════
# Le schede PNG vengono pubblicate come UNICO post multi-foto sulla Pagina.
# NB: nei GRUPPI non è più possibile pubblicare via API — Meta ha rimosso le
# Groups API il 22/04/2024. Dalla Pagina il post si condivide nel gruppo a mano.
# Permessi necessari sul token di Pagina: pages_manage_posts, pages_read_engagement.
FB_ABILITATO   = True
FB_API_VERSION = "v21.0"
FB_PAGE_ID     = os.environ.get("FB_PAGE_ID", "")
FB_PAGE_TOKEN  = os.environ.get("FB_PAGE_TOKEN", "")
FB_TIMEOUT     = 60

# Pubblicazione distribuita: un post al giorno nei giorni feriali, uno per articolo.
# La corsa del lunedì crea tutti e cinque i post già programmati; a pubblicarli
# è poi Facebook. Vincolo API: l'orario deve essere almeno 10 minuti nel futuro.
FB_UN_POST_AL_GIORNO = True
FB_FUSO              = "Europe/Rome"
FB_ORA               = 9    # ora di pubblicazione (0-23), fuso di Roma.
                            # EM pubblica alle 16:00 sulla STESSA Pagina: orari
                            # distinti per non sovrapporre i due digest.
FB_MINUTO            = 0
# Post sui corsi (da corsi.json): un post per corso, a un orario proprio.
FB_ORA_CORSI         = 12
FB_MINUTO_CORSI      = 30
FB_GIORNI_FERIALI    = {0, 1, 2, 3, 4}   # lunedì=0 ... venerdì=4

# Didascalia del singolo post giornaliero.
POST_GIORNALIERO = """POCUS Weekly Digest — Settimana {settimana}/{anno} · articolo {i} di {tot}

{titolo}
{rivista}, {data}{badge}

{sintesi}

{rilevanza}{limite}

Fonte: pubmed.ncbi.nlm.nih.gov/{pmid}

Sintesi generata con supporto di intelligenza artificiale: verificare prima
dell'applicazione clinica.

#POCUS #EcografiaClinica #MedicinaDUrgenza #ProntoSoccorso #EBM"""

# Intestazione del post. {settimana}, {anno} e {n} vengono sostituiti.
# Instagram: un carosello a ogni uscita (schede degli articoli e locandina del corso POCUS).
# Attivo solo con IG_USER_ID (ID dell'account Instagram Business collegato alla Pagina) e con
# FB_PAGE_ID / FB_PAGE_TOKEN; senza, non fa nulla. IG_ABILITATO=0 lo spegne.
IG_ABILITATO    = os.environ.get("IG_ABILITATO", "1").strip().lower() not in ("0", "false", "no")
IG_USER_ID      = os.environ.get("IG_USER_ID", "").strip()

# X (ex Twitter): un post con il Reel delle schede e un testo breve (x_social.py). Servono le quattro chiavi
# dell'app X, come secret del repo; senza, X viene saltato. X_REEL = False lo spegne. X addebita ogni post
# sui crediti dell'app. X_HASHTAG / X_INVITO: hashtag e riga d'invito (se vuoti: i primi tre di IG_HASHTAG, nessun invito).
X_REEL          = True
X_API_KEY       = os.environ.get("X_API_KEY", "").strip()
X_API_SECRET    = os.environ.get("X_API_SECRET", "").strip()
X_ACCESS_TOKEN  = os.environ.get("X_ACCESS_TOKEN", "").strip()
X_ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET", "").strip()
X_HASHTAG       = ""
X_INVITO        = ""

# YouTube (youtube.py): Reel come Shorts. Servono i secret YT_CLIENT_ID, YT_CLIENT_SECRET e
# YT_REFRESH_TOKEN (youtube_autorizza.py); senza, YouTube viene saltato. YT_ABILITATO = False lo spegne.
# Un progetto Google non verificato da YouTube ha i video dell'API bloccati come PRIVATI (README).
YT_ABILITATO     = True
YT_CLIENT_ID     = os.environ.get("YT_CLIENT_ID", "").strip()
YT_CLIENT_SECRET = os.environ.get("YT_CLIENT_SECRET", "").strip()
YT_REFRESH_TOKEN = os.environ.get("YT_REFRESH_TOKEN", "").strip()
YT_PRIVACY       = "public"          # 'public', 'unlisted' o 'private'
YT_CATEGORIA     = "27"              # 27 = Istruzione
YT_TAGS          = ["POCUS", "ecografia clinica", "ecografia in emergenza", "pronto soccorso", "newsletter", "San Giovanni Bosco"]
# Titoli (la data si aggiunge da sola): 'schede' = Short con le schede
YT_TITOLI        = {"schede": "POCUS Weekly Digest · gli articoli della settimana",
                    "podcast": "POCUS Weekly Digest · estratto del podcast",
                    "completo": "POCUS Weekly Digest · il podcast della settimana"}
# Token della Pagina usato solo da Instagram: se manca si usa FB_PAGE_TOKEN (che resta dei post Facebook).
IG_PAGE_TOKEN   = os.environ.get("IG_PAGE_TOKEN", "").strip()
IG_DIR          = "instagram"

# Archivio della corsa (articoli scelti con sintesi): finisce nell'artifact e serve a ripubblica.py
# per rifare solo i Reel falliti. RIPUBBLICA_PREDEFINITE: voci ripubblicate se non se ne scelgono.
ARCHIVIO_ABILITATO = True
ARCHIVIO_DIR       = "archivio"
ARCHIVIO_FILE      = "digest-s{settimana}-{anno}.json"
RIPUBBLICA_PREDEFINITE = "ig_schede,ig_podcast"

IG_INTESTAZIONE = "POCUS Weekly Digest — Settimana {settimana}/{anno}\nGli articoli più rilevanti per l'ecografia clinica in Pronto Soccorso e Area Critica."
IG_CHIUSURA     = "Sintesi generate con supporto di intelligenza artificiale: verifica sempre la fonte originale. Iscrizione alla newsletter dal link in bio."
# Reel: stesse diapositive del carosello, una dopo l'altra (IG_REEL_SCHEDE=False lo spegne). Senza
# musica; se esiste il file IG_MUSICA (senza diritti d'autore: va controllata la licenza) viene
# messo sotto le schede.
IG_REEL_SCHEDE  = True
IG_MUSICA       = "musica/sottofondo.mp3"
# Credito della musica dei Reel, in fondo alla didascalia (solo se il file IG_MUSICA esiste).
IG_MUSICA_CREDITO = "Musica: «Soft Corporate» di Yuri Megis (CC BY 4.0, freemusicarchive.org)"
# Invito scritto in testa alle locandine dei corsi nei Reel (Instagram, Facebook, X); il carosello non cambia.
# Vuoto = nessuna scritta. Sotto l'invito: REEL_INVITO_SOTTO.
REEL_INVITO_LOCANDINA = "Sei un medico d'emergenza-urgenza? Partecipa ai nostri corsi!"
REEL_INVITO_SOTTO     = "Date, sede e iscrizioni nella newsletter"
# Diapositiva con i tre loghi: sempre l'ultima del carosello e dei Reel (se il file esiste).
IG_LOGHI        = "loghi/chiusura.png"
# Prima diapositiva del carosello e del Reel: la schermata della pagina di iscrizione (index.html)
# con titolo di presentazione e invito a iscriversi. IG_COPERTINA_ISCRIZIONE=False la toglie.
IG_COPERTINA_ISCRIZIONE = True
IG_COPERTINA_TITOLO = "POCUS Weekly Digest"
IG_COPERTINA_SOTTOTITOLO = "La newsletter settimanale sull'ecografia clinica in emergenza-urgenza"
IG_COPERTINA_INVITO = "Iscriviti alla newsletter"
IG_HASHTAG      = "#POCUS #EcografiaClinica #MedicinaDUrgenza #ProntoSoccorso #EBM #FOAMed"
# Reel con l'estratto del podcast (60-90 s, poi i saluti sui loghi), dopo il carosello e il Reel
# delle schede. Solo se il podcast di questa corsa e' riuscito. IG_REEL_PODCAST=False lo spegne.
IG_REEL_PODCAST = True
IG_PODCAST_INTESTAZIONE = ("POCUS Weekly Digest — il podcast della settimana {settimana}/{anno}\n"
                           "Un estratto: il podcast completo arriva con la newsletter.")

FB_INTESTAZIONE = """POCUS Weekly Digest — Settimana {settimana}/{anno}

I {n} articoli più rilevanti per l'ecografia clinica in Pronto Soccorso e Area
Critica, selezionati dalla letteratura internazionale della settimana."""

# Testo da incollare nel gruppo Facebook il lunedì: nel gruppo non si può
# pubblicare via API (Meta ha rimosso le Groups API il 22/04/2024), quindi il
# workflow prepara il messaggio con il link al primo post e resta il copia-incolla.
POST_GRUPPO = """{nome} — settimana {settimana}/{anno}

Ogni settimana leggiamo le principali riviste internazionali di ecografia clinica,
medicina d'urgenza e area critica e selezioniamo i cinque lavori che possono
davvero cambiare come si usa la sonda al letto del paziente. Per ciascuno: sintesi in italiano con i
numeri chiave, ricaduta pratica e limite metodologico.

Questa settimana si parte con:
{primo_titolo}

{link}

Un articolo al giorno fino a venerdì sulla pagina {pagina} — seguitela per
riceverli tutti."""

# Nome della Pagina come compare nel testo per il gruppo.
FB_NOME_PAGINA = "Emergency Ultrasound School in Turin"
FB_FILE_GRUPPO = "post_gruppo.txt"

FB_CHIUSURA = """Le sintesi sono generate con supporto di intelligenza artificiale
e vanno verificate prima dell'applicazione clinica.

#POCUS #EcografiaClinica #MedicinaDUrgenza #ProntoSoccorso #EBM"""
NCBI_TOOL          = "pocus_weekly_digest_torino"  # User-Agent per i feed PubMed

# ═══════════════════════════════════════════════════════════════════════════════
# RIVISTE TARGET (20)
# "gruppo": eco = riviste di ecografia | em = medicina d'urgenza |
#           gen = medicina generale | spec = specialistica.
# Le riviste "eco" erano finora hardcoded nello script: qui hanno finalmente
# gruppo e limit come tutte le altre. Producono la gran parte del materiale
# pertinente, quindi il vincolo di composizione garantisce loro una quota.
# ═══════════════════════════════════════════════════════════════════════════════
RIVISTE = [
    # ─── Ecografia (nucleo tematico) ──────────────────────────────────────────
    {"nome": "Journal of Ultrasound in Medicine",   "nlmta": "J Ultrasound Med",     "issn": "0278-4297", "gruppo": "eco", "limit": 50},
    {"nome": "Ultrasound in Medicine and Biology",  "nlmta": "Ultrasound Med Biol",  "issn": "0301-5629", "gruppo": "eco", "limit": 50},
    {"nome": "The Ultrasound Journal",              "nlmta": "Ultrasound J",         "issn": "2524-8987", "gruppo": "eco"},
    {"nome": "J Am Society of Echocardiography",    "nlmta": "J Am Soc Echocardiogr","issn": "0894-7317", "gruppo": "eco", "limit": 50},
    # Journal of Ultrasound: rivista SIUMB, spesso con lavori italiani.
    {"nome": "Journal of Ultrasound",               "nlmta": "J Ultrasound",         "issn": "1971-3495", "gruppo": "eco"},
    # NB: Critical Ultrasound Journal (2036-3176 / 2036-7902) NON va reinserita:
    # ha pubblicato fino al 2018 ed è stata continuata da The Ultrasound Journal,
    # gia' presente qui sopra. Il suo feed produrrebbe solo articoli storici,
    # sempre fuori dalla finestra dei 7 giorni, oppure un feed vuoto.
    # ─── Medicina d'urgenza ───────────────────────────────────────────────────
    {"nome": "Annals of Emergency Medicine",        "nlmta": "Ann Emerg Med",        "issn": "0196-0644", "gruppo": "em"},
    {"nome": "Academic Emergency Medicine",         "nlmta": "Acad Emerg Med",       "issn": "1069-6563", "gruppo": "em"},
    {"nome": "Emergency Medicine Journal",          "nlmta": "Emerg Med J",          "issn": "1472-0205", "gruppo": "em"},
    {"nome": "Resuscitation",                       "nlmta": "Resuscitation",        "issn": "0300-9572", "gruppo": "em"},
    # ─── Medicina generale ────────────────────────────────────────────────────
    {"nome": "New England Journal of Medicine",     "nlmta": "N Engl J Med",         "issn": "0028-4793", "gruppo": "gen"},
    {"nome": "The Lancet",                          "nlmta": "Lancet",               "issn": "0140-6736", "gruppo": "gen"},
    {"nome": "JAMA",                                "nlmta": "JAMA",                 "issn": "0098-7484", "gruppo": "gen"},
    {"nome": "BMJ",                                 "nlmta": "BMJ",                  "issn": "0959-8138", "gruppo": "gen"},
    # ─── Specialistiche ───────────────────────────────────────────────────────
    {"nome": "Circulation",                         "nlmta": "Circulation",          "issn": "0009-7322", "gruppo": "spec"},
    {"nome": "Chest",                               "nlmta": "Chest",                "issn": "0012-3692", "gruppo": "spec"},
    {"nome": "Critical Care Medicine",              "nlmta": "Crit Care Med",        "issn": "0090-3493", "gruppo": "spec"},
    {"nome": "Intensive Care Medicine",             "nlmta": "Intensive Care Med",   "issn": "0342-4642", "gruppo": "spec"},
    {"nome": "Critical Care",                       "nlmta": "Crit Care",            "issn": "1364-8535", "gruppo": "spec"},
    {"nome": "Annals of Intensive Care",            "nlmta": "Ann Intensive Care",   "issn": "2110-5820", "gruppo": "spec"},
]

# ═══════════════════════════════════════════════════════════════════════════════
# PARAMETRI PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════
GIORNI_RICERCA  = 7   # finestra temporale: ultimi 7 giorni (settimana)
# ESearch per argomento su TUTTA PubMed, non sui soli RSS delle riviste.
ESEARCH_RETMAX = 500
ESTENDI_RICERCA = False  # evita riutilizzo articoli di settimane precedenti
GIORNI_RICERCA_ESTESO = 14  # fallback se la settimana è troppo povera
ARTICOLI_FINALI = 5   # MASSIMO di 5 articoli pertinenti, non quota obbligatoria
ARTICOLI_RICHIESTI = 8  # quanti chiederne al modello: i 3 in più sono la riserva
                        # da cui il codice attinge per rispettare i vincoli
MIN_EM_GEN = 0        # rilevanza POCUS prima delle quote per rivista
GRUPPI_PRIORITARI = {"eco", "em"}
ETICHETTA_GRUPPO = {"eco": "ecografia", "em": "urgenza",
                    "gen": "generale", "spec": "specialistica"}
MINIMO_ARTICOLI = 1   # nessun articolo non validato aggiunto per fare numero
MAX_PER_TEMA    = 2   # max articoli sullo stesso tema clinico nello stesso digest
MAX_CANDIDATI_PROMPT = 150  # tetto di candidati inviati al filtro (protegge i token)

# Token per tipo di chiamata.
# NB: NON reintrodurre il parametro "temperature": è deprecato per questo modello
# e l'API risponde 400 (verificato sul run del 03/08/2026).
MAX_TOKENS_FILTRO          = 1200
MAX_TOKENS_SINTESI_MULTI   = 4000
MAX_TOKENS_SINTESI_SINGOLA = 800

# Finestra RSS per rivista: PubMed accetta 15/20/50/100. Le riviste ad alto volume
# vanno alzate, altrimenti 20 item non coprono 7 giorni e si perdono articoli.
RSS_LIMIT_DEFAULT = 20

# Classificazione dell'articolo -> badge nell'email. Le chiavi sono i soli valori
# accettati dal parser: qualunque altro valore viene scartato.
TIPI_ARTICOLO = {
    "cambia-pratica": {"label": "Cambia la pratica", "colore": "#c41e3a"},
    "conferma":       {"label": "Conferma",          "colore": "#4a7c59"},
    "controverso":    {"label": "Controverso",       "colore": "#b8860b"},
    "esplorativo":    {"label": "Esplorativo",       "colore": "#6b7a8f"},
    "revisione":      {"label": "Revisione",         "colore": "#6f5b8e"},
}

# Frase fissa richiesta al modello quando l'abstract non permette di giudicare:
# essendo fissa, in build_html si può decidere di non stampare la riga.
LIMITE_NON_DESUMIBILE = "Limiti non desumibili dall'abstract."

# ═══════════════════════════════════════════════════════════════════════════════
# PRE-FILTRO DETERMINISTICO
# ═══════════════════════════════════════════════════════════════════════════════
# Il feed RSS di PubMed non espone il campo PublicationType, ma questi tipi di
# pubblicazione sono riconoscibili dal titolo. Filtrarli qui è deterministico
# e a costo zero, invece di delegarlo al prompt di filtro.
ESCLUSIONI_TITOLO = [
    r"^correction\b", r"^corrigendum\b", r"^erratum\b", r"^retraction\b",
    r"^withdrawn\b", r"^expression of concern\b", r"^notice of\b",
    r"^comments? on\b", r"^reply\b", r"^in reply\b", r"^response to\b",
    r"^re:\s", r"^letter\b", r"^correspondence\b", r"^authors?'? repl",
    r"^editorial\b", r"^this month in\b", r"^highlights\b", r"^in this issue\b",
    r"^images? in\b", r"^image of\b", r"^clinical picture\b",
    r"^visual diagnosis\b", r"^obituary\b", r"^in memoriam\b",
    r"^podcast\b", r"^book review\b",
]

# Lunghezza minima dell'abstract. A 200 il run del 03/08 scartava anche ricerca
# originale (SEP-1 e sepsi, arresto cardiaco pediatrico, blocco PENG ecoguidato):
# abbassata a 120, ora che il filtro sui titoli intercetta lettere e correzioni.
# La lunghezza effettiva è loggata a ogni scarto, per tararla sui dati.
ABSTRACT_MIN_CHARS = 120

# Troncatura degli abstract passati al modello.
# Al FILTRO basta l'inizio: conta il quesito e il disegno, e la lista è lunga.
# Alla SINTESI serve tutto: con gli abstract completi di efetch, 2000 caratteri
# mutilavano i trial maggiori (ICECAP è stato sintetizzato su un testo troncato,
# e il modello lo ha segnalato come limite). 6000 copre ogni abstract PubMed.
ABSTRACT_MAX_FILTRO  = 700
ABSTRACT_MAX_SINTESI = 6000

# ═══════════════════════════════════════════════════════════════════════════════
# E-UTILITIES efetch — abstract veri e tipi di pubblicazione
# ═══════════════════════════════════════════════════════════════════════════════
# Il feed RSS di PubMed non contiene l'abstract per una larga quota di record
# (segnaposto di 11 caratteri) né il campo PublicationType. efetch fornisce
# entrambi con una sola richiesta per lotto di PMID.
EFETCH_URL     = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
EFETCH_BATCH   = 200   # PMID per richiesta (POST, nessun limite di lunghezza URL)
EFETCH_TIMEOUT = 30
EFETCH_RETRY   = 2     # tentativi aggiuntivi prima di degradare sulla description RSS
NCBI_TOOL      = "newsletter-pocus"
NCBI_EMAIL     = ""    # opzionale: NCBI chiede un contatto per usi automatizzati

# PublicationType da escludere. Etichette ufficiali PubMed: esatte, non euristiche.
# NB: "Review" e "Practice Guideline" NON sono qui: revisioni sistematiche e linee
# guida sono fra i contenuti più utili del digest.
PUBTYPE_ESCLUSI = {
    "Letter", "Comment", "Editorial", "Published Erratum", "Retraction of Publication",
    "Retracted Publication", "Expression of Concern", "News",
    "Newspaper Article", "Biography", "Historical Article", "Portrait", "Interview",
    "Congress", "Video-Audio Media", "Address", "Autobiography", "Bibliography",
    "Personal Narrative", "Introductory Journal Article", "Patient Education Handout",
}

# Tipi da segnalare al filtro come indizio di qualità metodologica.
# PublicationType che identificano una sintesi di letteratura senza dati primari:
# su questi il badge "revisione" viene imposto in codice, senza chiederlo al modello.
# "Meta-Analysis" è escluso di proposito: una metanalisi produce stime quantitative
# proprie e può legittimamente essere "cambia-pratica".
PUBTYPE_REVISIONE = {
    "Review", "Systematic Review", "Scoping Review", "Practice Guideline",
    "Guideline", "Consensus Development Conference",
    "Consensus Development Conference, NIH",
}

PUBTYPE_PRIORITARI = [
    "Randomized Controlled Trial", "Meta-Analysis", "Systematic Review",
    "Multicenter Study", "Clinical Trial, Phase III", "Practice Guideline",
]

# Schedulazione (trigger esterno via cron-job.org -> workflow_dispatch)
# Lunedì 13:00 ora di Roma. Il fuso/DST è gestito da cron-job.org, non da GitHub.
GIORNO_INVIO    = "mercoledì"
ORARIO_INVIO    = "07:00"  # ora di Roma; impostare così su cron-job.org

# Branding
NOME_NEWSLETTER = "POCUS Weekly Digest a cura di Francesco Panero"
NOME_SERVIZIO   = "Area Critica e Pronto Soccorso · San Giovanni Bosco · Torino"
COLOR_ACCENT    = "#0a6e8a"  # teal
COLOR_DARK      = "#1a2a30"
# URL PUBBLICO del logo (vuoto = nessun logo). Deve puntare a un file immagine
# raggiungibile pubblicamente (le email non supportano immagini locali/base64).
BASE_URL_LOGHI  = "https://raw.githubusercontent.com/areacriticaprontosoccorso/newsletter-pocus/main/"
# Loghi nell'intestazione della mail, affiancati da sinistra a destra.
LOGHI = [
    {"url": BASE_URL_LOGHI + "logo-medicina-urgenza.png",
     "alt": "Medicina d'Emergenza-Urgenza - Pronto Soccorso e Area Critica, Ospedale San Giovanni Bosco"},
    {"url": BASE_URL_LOGHI + "logo-eus-turin.png", "alt": "Emergency Ultrasound School Turin"},
]
LOGO_ALTEZZA    = 100   # px
LOGO_URL        = LOGHI[0]["url"]   # compatibilita'
# Base pubblica dei file del repo (locandine dei corsi): https://.../main/<percorso>
URL_RAW_REPO    = "https://raw.githubusercontent.com/areacriticaprontosoccorso/newsletter-pocus/main/"
NEWSLETTER_PAGE_URL = "https://areacriticaprontosoccorso.github.io/newsletter-pocus/"
# Reel anche su Facebook: lo stesso video di Instagram, pubblicato sulla Pagina (FB_PAGE_ID / FB_PAGE_TOKEN).
# Dove la didascalia di Instagram dice «dal link in bio», su Facebook va l'indirizzo vero (qui i link si cliccano).
FB_REEL = True
FB_REEL_INVITO = "Iscriviti alla newsletter: " + NEWSLETTER_PAGE_URL

# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT CLAUDE
# ═══════════════════════════════════════════════════════════════════════════════
# Contesto operativo del PS. Serve al filtro per scartare articoli inapplicabili
# (percorsi organizzativi esteri, farmaci non in commercio in Italia, risorse assenti).
CONTESTO_POCUS = """CONTESTO DEL LETTORE:
- Medici di Pronto Soccorso, Medicina d'Urgenza e Area Critica che praticano
  ecografia clinica al letto del paziente (POCUS), in un DEA di II livello
  urbano di Torino, Servizio Sanitario Nazionale italiano.
- Casistica adulta e pediatrica, compresi pazienti critici e anziani fragili.
- Includere POCUS in ambito preospedaliero e durante il trasporto sanitario.
- L'ecografo è disponibile in shock room, in OBI e nelle sale visita;
  l'esame lo esegue e lo interpreta il medico d'urgenza, non il radiologo.

COSA RENDE UN ARTICOLO PERTINENTE: deve riguardare l'ecografia eseguita dal
clinico al letto del paziente per rispondere a una domanda binaria e immediata,
oppure per guidare una procedura. Il criterio non è che l'articolo nomini
l'ecografia, ma che cambi il modo in cui il lettore impugna la sonda o
interpreta ciò che vede.

Sono di interesse anche POCUS pediatrico, neonatale in urgenza e preospedaliero,
quando il risultato guida una decisione clinica o una procedura.
Sono di interesse: protocolli e applicazioni POCUS in urgenza (FAST ed e-FAST,
ecografia polmonare, ecocardiografia mirata, valutazione della vena cava,
ecografia vascolare, RUSH, BLUE, FALLS); ecografia procedurale (accessi
vascolari, toracentesi, paracentesi, blocchi nervosi, pericardiocentesi);
accuratezza diagnostica di segni ecografici rispetto a uno standard di
riferimento; integrazione dell'ecografia nei percorsi decisionali del PS;
formazione, curve di apprendimento e affidabilità fra operatori.

NON sono di interesse: ecografia ostetrico-ginecologica di routine, ecografia
internistica ambulatoriale, ecocardiografia specialistica avanzata eseguita dal
cardiologo, elastografia e mezzi di contrasto in ambito non urgente, imaging
non ecografico, e la ricerca su fisica o ingegneria degli ultrasuoni senza
ricaduta clinica diretta.

ATTENZIONE: un articolo che usa l'ecografia solo come strumento di misura in uno
studio su altro argomento NON è un articolo POCUS. Conta che l'oggetto dello
studio sia l'ecografia stessa o il suo impiego decisionale."""

PROMPT_FILTRO_RILEVANZA = """COMPITO: dalla lista di articoli candidati, restituisci
una GRADUATORIA di {n} articoli, i più rilevanti per la pratica dell'ecografia
clinica (POCUS) in Pronto Soccorso, Medicina d'Urgenza e Area Critica.

CRITERI DI SELEZIONE, in ordine di priorità decrescente:
1. PERTINENZA POCUS - l'ecografia al letto del paziente è l'oggetto dello studio,
   non un semplice strumento di misura. Se togliendo l'ecografia lo studio
   resterebbe sostanzialmente lo stesso, non è un articolo POCUS.
2. IMPATTO DECISIONALE - il risultato può modificare come il lettore usa la sonda:
   quando eseguire l'esame, quale segno cercare, come interpretarlo, quale
   decisione prenderne. Vale anche per l'ecoguida procedurale.
3. QUALITÀ METODOLOGICA - studi di accuratezza diagnostica con standard di
   riferimento esplicito, trial randomizzati, meta-analisi e revisioni
   sistematiche prima di serie osservazionali; numerosità adeguata.
   Il campo TIPO riporta i PublicationType ufficiali di PubMed: usalo come
   indizio diretto del disegno dello studio.
4. NOVITÀ - a parità di tutto il resto, preferisci ciò che cambia una pratica
   consolidata rispetto a ciò che conferma quanto già noto.

VINCOLI DI COMPOSIZIONE:
- Massimo 2 articoli sullo stesso tema clinico (es. non 3 studi sull'ecografia
  polmonare).
- Massimo 2 articoli dalla stessa rivista.
- Preferisci una selezione che copra applicazioni ecografiche diverse.

ESCLUDI:
- Ecografia ostetrico-ginecologica di routine ed ecografia internistica
  ambulatoriale.
- Ecocardiografia specialistica avanzata non eseguibile al letto dal medico
  d'urgenza.
- Imaging non ecografico (TC, RM, radiologia convenzionale).
- Ricerca su fisica, ingegneria o bioeffetti degli ultrasuoni senza ricaduta
  clinica immediata.
- Case series senza informazioni metodologiche o insegnamenti POCUS utili.
- I case report POCUS sono AMMESSI, se descrivono una manovra, un reperto
  o una decisione clinica ecoguidata trasferibile alla pratica; valutarli
  con peso metodologico inferiore a studi comparativi e revisioni.
- Studi su sistemi sanitari non europei senza trasferibilità.

ARTICOLI CANDIDATI:
{articoli}

IMPORTANTE - LUNGHEZZA DELLA GRADUATORIA: devi restituire ESATTAMENTE {n} voci,
non {n_finali}. Ne verranno pubblicate soltanto le prime {n_finali}: le voci
successive sono la riserva da cui il sistema attinge per rispettare i vincoli di
composizione, e servono anche quando sono meno interessanti delle prime.
Restituisci meno di {n} voci solo se i candidati davvero pertinenti sono meno.
Meglio una graduatoria corta (anche UNA SOLA VOCE o vuota) che includere
studi in cui l'ecografia e' marginale o specialistica non POCUS.
Non includere articoli per raggiungere una quota numerica.

FORMATO DI RISPOSTA - restituisci SOLO un array JSON valido, senza testo prima o
dopo, senza blocchi markdown. Scegli esclusivamente PMID presenti nella lista qui
sopra: non inventare né modificare PMID.
Nei valori testuali NON usare mai virgolette doppie: per citare un nome, un termine o una frase usa gli apici singoli ('...') oppure le caporali «...». Una virgoletta doppia dentro il testo rompe il formato JSON.

[
  {{"pmid": "12345678", "tema": "ecografia polmonare", "perche": "motivo in max 15 parole"}},
  {{"pmid": "23456789", "tema": "accessi vascolari", "perche": "..."}}
]

L'ORDINE CONTA: ordina dalla più rilevante alla meno rilevante con cura, perché la
posizione determina cosa viene pubblicato."""

# Regole di traduzione condivise. Vivono nel system prompt delle chiamate di sintesi.
REGOLE_TRADUZIONE = """REGOLE DI TRADUZIONE (obbligatorie):
- ORTOGRAFIA: usa gli accenti italiani corretti (è, à, ì, ò, ù, é). Non sostituirli
  mai con l'apostrofo: si scrive "qualità", non "qualita\'"; "è", non "e\'";
  "più", non "piu\'"; "perché", non "perche\'".
- ORTOGRAFIA DI TERMINI RICORRENTI, spesso storpiati: si scrive "preospedaliero"
  (non "preistospedaliero" né "prestospedaliero"), "intraospedaliero",
  "extraospedaliero", "endovenoso", "endotracheale", "emogasanalisi".
- Traduci il SIGNIFICATO clinico, mai parola per parola. Vietati i calchi dall'inglese.
- Evita i falsi amici: "severe"=grave (non "severo"); "evidence"=prove/evidenze
  (non "evidenza"); "eventually"=infine (non "eventualmente"); "actual"=effettivo/reale
  (non "attuale"); "consistent"=coerente/costante (non "consistente"); "to require"=
  necessitare; "to administer"=somministrare; "rate"=tasso; "significant"
  (statistico)=statisticamente significativo; "mortality"=mortalità;
  "morbidity"=morbilità; "compliance"=aderenza; "management"=gestione;
  "care"=assistenza/cure; "to realize"=rendersi conto.
- Usa la terminologia clinica italiana corrente: stroke=ictus, seizure=crisi epilettica,
  bleeding=sanguinamento/emorragia, airway=vie aeree, ward=reparto,
  critically ill=pazienti critici, drug=farmaco, physician=medico, wound=ferita.
- Lessico dei trial: "trial"=studio/sperimentazione clinica; "arm"=braccio;
  "blinded"=in cieco; "double-blind"=in doppio cieco; "open-label"=in aperto;
  "primary/secondary endpoint"=endpoint primario/secondario; "number needed to
  treat"=NNT; "confounding"=confondimento; "adherence"=aderenza.
- Lascia in inglese SOLO i termini realmente in uso in clinica italiana: ARDS, shock,
  outcome, endpoint, follow-up, weaning, screening, setting, cut-off, bias,
  propensity score, hazard, washout; usa "basale" per baseline.
- Riporta con precisione le misure statistiche: odds ratio (OR), hazard ratio (HR),
  rischio relativo (RR), intervallo di confidenza (IC) al 95%, valore di p.
- NUMERI: riporta cifre e separatore decimale ESATTAMENTE come nell'originale
  (punto decimale: 0.85; p<0.001). Non convertire il punto in virgola: ogni
  riscrittura di un numero è un'occasione di errore. Non alterare dosi,
  unità di misura, percentuali.
- Mantieni in forma originale le scale validate (GCS, SOFA, qSOFA, NEWS2, CURB-65).
- Espandi ogni acronimo alla prima comparsa, poi usa la sigla.
- Non usare mai "significativo" da solo: specifica "statisticamente significativo"
  oppure "clinicamente rilevante".
- Attieniti SOLO ai dati dell'abstract: non aggiungere, non inferire, non inventare."""

# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────
# Persona, contesto e regole stabili vivono qui: sono identici a ogni esecuzione,
# mentre il messaggio utente contiene solo il compito e i dati della settimana.
SYSTEM_FILTRO = """Sei un medico strutturato di Pronto Soccorso italiano con
esperienza consolidata in ecografia clinica (POCUS). Selezioni la letteratura
settimanale di ecografia d'urgenza per i colleghi del tuo reparto e per la scuola
di ecografia d'urgenza.

""" + CONTESTO_POCUS

SYSTEM_SINTESI = """Sei un medico di Pronto Soccorso italiano esperto di ecografia
clinica, di letteratura scientifica e di traduzione medico-scientifica
dall'inglese all'italiano. Scrivi in
italiano, con linguaggio medico-scientifico preciso, del registro usato nelle riviste
italiane di area critica.

""" + REGOLE_TRADUZIONE

# ── PROMPT DI SINTESI ─────────────────────────────────────────────────────────
# Sintesi di TUTTI gli articoli in una sola chiamata API.
PROMPT_SINTESI_MULTI = """Analizza OGNI articolo della lista e produci per ciascuno
quattro campi:

1. "sintesi" - da 90 a 120 parole, che rispondano nell'ordine a: quesito clinico;
   disegno dello studio e popolazione, con numerosità; risultato principale con i
   numeri chiave e la misura di effetto (per gli studi di accuratezza: sensibilità,
   specificità, rapporti di verosimiglianza, con gli intervalli di confidenza);
   ricaduta sulla pratica ecografica al letto in PS/Area Critica.
2. "rilevanza" - UNA sola frase, massimo 30 parole, sulla ricaduta concreta per
   l'ecografia bedside in Pronto Soccorso.
3. "limite" - UNA sola frase, massimo 25 parole, sul principale limite metodologico:
   monocentrico, non in cieco, endpoint surrogato, campione ridotto, popolazione
   selezionata, follow-up breve, conflitti di interesse. Per gli studi ecografici
   sono limiti tipici anche: operatori esperti non rappresentativi della pratica
   corrente, assenza di cecità rispetto al quadro clinico, standard di riferimento
   inadeguato, mancata valutazione della concordanza fra operatori.
   Per le sintesi di letteratura il limite riguarda il metodo della revisione:
   narrativa e non sistematica, selezione degli studi non riproducibile, assenza
   di valutazione formale della qualità, eterogeneità degli studi inclusi.
   Solo se l'abstract non consente davvero di identificare alcun limite, scrivi
   esattamente: "Limiti non desumibili dall'abstract."
4. "tipo" - UNO SOLO fra questi valori, riportato esattamente così:
   "cambia-pratica" = lo studio modifica una condotta oggi diffusa
   "conferma"       = rafforza una pratica già consolidata
   "controverso"    = risultati discordanti con evidenze o linee guida attuali
   "esplorativo"    = ipotesi generatrice, dati preliminari, campione insufficiente
   "revisione"      = sintesi di letteratura senza dati primari originali: review
                      narrativa, scoping review, revisione sistematica, linea guida.
                      Usa SEMPRE questo valore per le sintesi di letteratura, anche
                      quando le conclusioni sono preliminari: "esplorativo" è
                      riservato agli studi con dati primari.

SE L'ABSTRACT E' ASSENTE O PRIVO DI RISULTATI NUMERICI: scrivi nella "sintesi" una
sola frase che lo dichiari esplicitamente, non inferire nulla dal titolo, usa
"esplorativo" come tipo.

ARTICOLI:
{articoli}

FORMATO DI RISPOSTA - restituisci SOLO un array JSON valido, senza testo prima o dopo,
senza blocchi markdown, con un oggetto per articolo, nello stesso ordine della lista.
Riporta il "pmid" esattamente come ti è stato fornito.
Nei valori testuali NON usare mai virgolette doppie: per citare un nome, un termine o una frase usa gli apici singoli ('...') oppure le caporali «...». Una virgoletta doppia dentro il testo rompe il formato JSON.

[
  {{
    "pmid": "12345678",
    "sintesi": "...",
    "rilevanza": "...",
    "limite": "...",
    "tipo": "cambia-pratica"
  }}
]"""

# Sintesi di un singolo articolo (fallback se dal multi manca qualcosa).
# Restituisce un array di UN elemento, così da riusare lo stesso parser del multi.
PROMPT_SINTESI = """Analizza l'articolo e produci quattro campi:

1. "sintesi" - 90-120 parole: quesito clinico; disegno e popolazione con numerosità;
   risultato principale con i numeri chiave; ricaduta per l'ecografia bedside
   in PS/Area Critica.
2. "rilevanza" - una sola frase, massimo 30 parole.
3. "limite" - una sola frase, massimo 25 parole, sul principale limite metodologico.
   Per le revisioni: limite del metodo della revisione (narrativa, selezione non
   riproducibile, eterogeneità degli studi). Solo se davvero non desumibile,
   scrivi esattamente: "Limiti non desumibili dall'abstract."
4. "tipo" - uno fra: "cambia-pratica", "conferma", "controverso", "esplorativo",
   "revisione" (quest'ultimo per ogni sintesi di letteratura senza dati primari).

Se l'abstract è assente o privo di risultati numerici, dichiaralo nella "sintesi"
in una sola frase, non inferire dal titolo, e usa tipo "esplorativo".

Articolo:
PMID: {pmid}
Titolo: {titolo}
Autori: {autori}
Rivista: {rivista} ({data})
Abstract: {abstract}

FORMATO DI RISPOSTA - restituisci SOLO un array JSON valido con UN solo oggetto,
senza testo prima o dopo, senza blocchi markdown:
Nei valori testuali NON usare mai virgolette doppie: per citare un nome, un termine o una frase usa gli apici singoli ('...') oppure le caporali «...». Una virgoletta doppia dentro il testo rompe il formato JSON.

[
  {{
    "pmid": "{pmid}",
    "sintesi": "...",
    "rilevanza": "...",
    "limite": "...",
    "tipo": "conferma"
  }}
]"""

# ═══════════════════════════════════════════════════════════════════════════════
# PATH FILE
# ═══════════════════════════════════════════════════════════════════════════════
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
# ═══════════════════════════════════════════════════════════════════════════════
# PODCAST SETTIMANALE (podcast.py, lo stesso file di newsletter-ps)
# ═══════════════════════════════════════════════════════════════════════════════
# Il podcast (video MP4 con le schede e la voce, o in ripiego l'MP3) si genera prima della mail e
# parte ALLEGATO alla mail degli iscritti. Mai bloccante: se manca, la mail esce senza.
# Serve il secret GEMINI_API_KEY. PODCAST=0 (variabile d'ambiente) lo spegne.
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
PODCAST_ABILITATO  = os.environ.get("PODCAST", "1").strip().lower() not in ("0", "false", "no")
PODCAST_DIR        = "podcast"
PODCAST_ARCHIVIO   = os.path.join(PODCAST_DIR, "digest.json")     # articoli e schede per podcast.py
PODCAST_ESITO      = os.path.join(PODCAST_DIR, "esito.json")
# Il podcast si genera dentro la newsletter, prima della mail, e l'MP3 parte allegato.
# Oltre PODCAST_TIMEOUT_MAIL secondi il processo viene chiuso e la mail esce senza.
PODCAST_TIMEOUT_MAIL = 25 * 60
# Cosa allegare alla mail, in ordine: il video (MP4, ~4 MB, audio + schede) e, se
# l'invio col video fallisce, l'MP3 (~2 MB). Nessuno dei due se gli allegati
# supererebbero MAIL_MAX_MB (Gmail accetta 25 MB; molte caselle aziendali meno).
PODCAST_MAIL_ALLEGATI = ["mp4", "mp3"]
MAIL_MAX_MB           = 15
# In POCUS la mail porta anche le schede PNG: podcast + schede entro questo totale (Gmail: 25 MB
# compresa la codifica, che aggiunge circa un terzo).
MAIL_TOTALE_MAX_MB    = 17
# Il workflow passa l'esito del passo che installa torch/chatterbox: se è fallito
# non si perde tempo a tentare. In locale (variabile assente) si tenta.
PODCAST_DIPENDENZE_OK = os.environ.get("PODCAST_DIPENDENZE", "success").strip() in ("success", "")
# Motore della voce: "gemini" (Gemini TTS, API di Google: voci italiane native, serve
# il secret GEMINI_API_KEY) oppure "chatterbox" (modello locale sul runner, imita
# podcast_voce.wav; richiede torch e chatterbox nel passo delle dipendenze).
PODCAST_MOTORE = os.environ.get("PODCAST_MOTORE", "gemini").strip().lower()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
# Se Gemini non risponde (quota, chiave, blocchi) il podcast si rifà con Chatterbox
# sul runner: stesso copione, nessuna chiamata API in più, ma 20-30 minuti e voce
# meno italiana. "0" nella variabile di repository PODCAST_RIPIEGO lo disattiva.
PODCAST_RIPIEGO_CHATTERBOX = False     # in POCUS il ripiego locale non e' installato: senza Gemini niente podcast
# Modelli provati in ordine: se uno non esiste (404) si passa al successivo.
PODCAST_GEMINI_MODELLI = ["gemini-3.8-flash-tts", "gemini-3.1-flash-tts-preview",
                          "gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts"]
PODCAST_GEMINI_VOCE    = "Charon"     # voce predefinita di Gemini (informativa, maschile)
# Parole per chiamata: nelle letture oltre il minuto il modello cambia timbro verso la
# fine, quindi il podcast si genera in blocchi di sezioni intere (~40 s ciascuno).
PODCAST_GEMINI_PAROLE_BLOCCO = 100
# Fra una chiamata e l'altra il timbro cambia un po': lo spettro medio di ogni blocco
# viene portato su quello del primo (correzione massima in dB) e il volume pareggiato.
PODCAST_GEMINI_UNIFORMA = True
PODCAST_GEMINI_EQ_MAX_DB = 4
# Note di regia: vanno nella sezione "NOTE DI REGIA" del prompt, separate dalla
# "TRASCRIZIONE" (se scritte come frase prima del testo, il modello le legge ad alta voce).
PODCAST_GEMINI_STILE = ("Leggi in italiano, come un medico d'urgenza che presenta ai colleghi "
                        "la rassegna settimanale della letteratura: tono professionale, caldo "
                        "e naturale, ritmo sostenuto ma ben scandito, senza enfasi. Stessa voce, "
                        "stesso timbro e stesso ritmo dall'inizio alla fine. Breve pausa "
                        "fra un paragrafo e l'altro. Nomi delle riviste e termini inglesi in "
                        "pronuncia inglese.")
PODCAST_VOCE_RIF   = "podcast_voce.wav"   # campione di voce (sintetica) da imitare

# Niente "due minuti": POCUS esce con 1-5 articoli e la durata cambia di conseguenza.
PODCAST_INTRO = ("Benvenuti! Questa è la newsletter settimanale di ecografia clinica "
                 "della Medicina d'Emergenza-Urgenza dell'ospedale San Giovanni Bosco di Torino. "
                 "{Articoli} articoli, sola ecografia in emergenza-urgenza. Buon ascolto!")
# Titolo e tema sulla copertina del video; servizio di corsi.json per le locandine in coda.
PODCAST_TITOLO = "POCUS Weekly Digest"
PODCAST_TEMA   = "ecografia clinica in emergenza-urgenza"
PODCAST_CORSI  = "pocus"
# Chiusura parlata: avvertenza, (se ci sono corsi in programma) l'invito ai corsi, saluti.
# L'invito compare anche scritto sulle locandine, che appaiono mentre lo si dice.
PODCAST_CHIUSURA_AVVISO = ("Sintesi generate con l'intelligenza artificiale: verificate sempre sulle "
                           "fonti. Le sintesi complete e i link agli articoli sono nella newsletter.")
PODCAST_CHIUSURA_CORSI = "Sei un medico d'emergenza-urgenza? Partecipa ai nostri corsi!"
PODCAST_CHIUSURA_SALUTI = "Alla prossima."
PODCAST_CHIUSURA = PODCAST_CHIUSURA_AVVISO + " " + PODCAST_CHIUSURA_SALUTI      # senza corsi

# Carattere della voce Chatterbox: valori più bassi = intonazione più calma e meno
# enfatica. 0,35 / 0,3 scelti all'ascolto il 30/10 (prima: 0,5 / 0,5).
PODCAST_ESAGERAZIONE = 0.35
PODCAST_CFG          = 0.3

# Durata: se il parlato supera PODCAST_DURATA_MAX secondi si accelera fino a
# PODCAST_ATEMPO_MAX (oltre, la voce si snatura: si pubblica comunque, con avviso).
PODCAST_DURATA_MAX = 140   # 2 minuti e 20 secondi, concessi dal 2/11 (sigla e avvertenza comprese)
PODCAST_ATEMPO_MAX = 1.10
# Parole del copione per TUTTI gli articoli insieme (intro e chiusura escluse),
# riferite a un digest di ARTICOLI_FINALI articoli: con meno articoli i limiti
# scalano in proporzione. Misurato sul run del 30/10: 235 parole + intro = 124 s anche
# a velocità 1,10, quindi il tetto è sceso a 220 (circa 120 s).
# In PODCAST_INTRO, {Articoli} diventa il numero in lettere ("Cinque", "Quattro"...).
# Dal 2/11 il podcast ha apertura, avvertenza e sigla e può durare fino a 2'20".
PODCAST_PAROLE_MIN = 175
# Loghi in coda al video, in silenzio: secondi. La voce di chiusura corre sulle locandine dei corsi (POCUS e NIV).
PODCAST_LOCANDINA_SEC = 5
# Diapositiva con i tre loghi: sempre l'ultima del video del podcast (PODCAST_LOCANDINA_SEC secondi).
PODCAST_LOGHI = "loghi/chiusura.png"
PODCAST_PAROLE_MAX = 210
# Frase d'apertura scritta da Claude ("Questa settimana: ..."), inserita prima di "Buon ascolto".
PODCAST_APERTURA_MAX_PAROLE = 16
# Sottotitoli nel video (testo del copione con i tempi delle parole di Whisper) e sigla.
PODCAST_SOTTOTITOLI = True
# Tappeto musicale sotto la voce del podcast (solo se il file esiste), PODCAST_MUSICA_DB LU sotto la voce.
PODCAST_MUSICA = "musica/podcast.mp3"
PODCAST_MUSICA_DB = -24
PODCAST_MUSICA_CREDITO = "Musica: «The Distant Sun» di Scott Buckley (CC BY 4.0, www.scottbuckley.com.au)"   # riga in fondo alla mail
PODCAST_SIGLA = True
PODCAST_SIGLA_DB = -6      # loudness della sigla rispetto alla voce (LUFS): resta sotto, senza sparire

# Verifica della voce: ogni frase viene ritrascritta con Whisper e confrontata
# col testo; sotto soglia si rigenera (fino a PODCAST_TENTATIVI volte, si tiene
# la migliore).
PODCAST_SOGLIA_WHISPER = 0.82
PODCAST_TENTATIVI      = 3
# Sotto questo punteggio complessivo (o se Gemini legge le note di regia) la voce si scarta:
# EM passa alla voce di riserva, NIV e POCUS mandano la mail senza podcast (con avviso).
PODCAST_SOGLIA_MINIMA  = 0.75
# Minimo per ogni sezione (un articolo): sotto, la voce si scarta anche se la media e' buona.
PODCAST_SOGLIA_SEZIONE = 0.65
# Pulizia della voce prima della normalizzazione (filtro passa-alto e riduzione del rumore).
PODCAST_PULIZIA        = True
PODCAST_WHISPER_MODELLO = os.environ.get("PODCAST_WHISPER", "small")

# Pronuncia: sostituzioni applicate SOLO al testo dato alla sintesi vocale.
PODCAST_PRONUNCIA_IT = {
    "Emergenza-Urgenza": "Emergenza  Urgenza",   # col trattino "Urgenza" si fonde
    "emergenza-urgenza": "emergenza  urgenza",
    "EM": "I-em",
    "POCUS": "Pòcus",
    "NIV": "Niv",
    "eFAST": "i-fàst",
    "FAST": "fàst",
    "BLUE": "blù",
    "VExUS": "vèxus",
    "TAPSE": "tàpse",
    "PS": "Pronto Soccorso",
    "OBI": "o-bi-i",
    "ASL": "a-esse-elle",
}
# Parole inglesi brevi dentro una frase italiana: invece di un segmento in voce
# inglese (che spezzerebbe il ritmo) si usa questa grafia fonetica.
PODCAST_GRAFIA_FONETICA = {
    "trial": "tràial",
    "cluster": "clàster",
    "stepped-wedge": "stèpd-uèdg",
    "outcome": "àutcam",
    "endpoint": "èndpoint",
    "score": "scòr",
    "follow-up": "follou-àp",
    "setting": "sètting",
    "timing": "tàiming",
    "point-of-care": "point-of-chèr",
    "lung ultrasound": "lang ultrasàund",
    "B-lines": "bi-lains",
    "sliding": "slàiding",
}

PODCAST_PROMPT = """Scrivi il copione parlato del podcast settimanale di un Pronto Soccorso sull'ecografia \
clinica point-of-care (POCUS) in emergenza-urgenza: una sola voce, in italiano, tono tecnico ma \
colloquiale, per medici d'urgenza. Presenta i \
{n} articoli qui sotto, nell'ordine dato. Saluto iniziale, avvertenza e congedo li aggiunge \
il programma: tu scrivi l'APERTURA e i paragrafi degli articoli.

REGOLE
1. LUNGHEZZA, il vincolo più importante: il podcast dura poco più di due minuti, quindi devi \
scegliere, non riassumere tutto. Un paragrafo per articolo, da {per_min} a {per_max} \
parole ciascuno, MAI di più (3 o 4 frasi brevi). Tutti i paragrafi insieme: fra \
{min_parole} e {max_parole} parole. Conta le parole prima di rispondere.
2. APERTURA: una sola frase, al massimo {max_apertura} parole, che comincia con \
"Questa settimana" e annuncia il tema più importante (di solito il primo articolo). \
Nessun numero.
3. Apri ogni paragrafo con un connettivo d'ordine e la rivista, per esempio: \
"Si parte da [[Circulation]], ...", "Secondo studio, su ...", "Terzo, su ...", \
"Quarto, ancora su ...", "Infine, una metanalisi su ...".
4. Ogni paragrafo, in quest'ordine: il disegno dello studio in poche parole; UN \
risultato principale, con il suo confronto ("X% contro Y%", mai un valore isolato); \
il peso dell'evidenza detto a parole, partendo dal campo "badge" (per esempio "cambia \
la pratica", "da confermare", "studio esplorativo"), oppure il limite principale. Ometti \
intervalli di confidenza, \
valori p, analisi secondarie e dettagli di metodo. Scrivi i termini medici italiani per \
esteso e nella forma corretta ("ritorno della circolazione spontanea", non "circolo \
spontaneo").
5. NUMERI: usa SOLO numeri presenti nell'abstract o nella sintesi di QUELL'articolo, \
scritti in cifre (decimali con la virgola, migliaia col punto: 60.000; percentuali col \
simbolo %). Puoi arrotondare solo premettendo "circa". NON calcolare numeri nuovi: \
niente differenze, conversioni, rapporti o percentuali derivate.
6. TERMINI INGLESI: racchiudi fra doppie parentesi quadre OGNI nome di rivista, nome o \
acronimo di studio e termine tecnico inglese: [[Critical Care Medicine]], \
[[point-of-care]], [[odds]], [[trial]]. Se la pronuncia inglese non si deduce dalla \
grafia, aggiungi dopo una barra verticale come si legge: [[ICare-FASTER|Eye-Care Faster]], \
[[ARDS|A R D S]]. Usa la parola italiana quando esiste ed è d'uso comune \
(ecografia, sonda, finestra, versamento, esito).
7. Frasi brevi, adatte all'ascolto: al massimo 30 parole per frase. Niente parentesi, \
elenchi, virgolette doppie o abbreviazioni da leggere (scrivi "intervallo di \
confidenza", non "IC"). Le sigle italiane d'uso comune (PS, TC, POCUS) vanno bene. Per \
accuratezza diagnostica dì sensibilità e specificità a parole ("sensibilità del 90%").
8. Non aggiungere nulla che non sia negli abstract o nelle sintesi.

Rispondi SOLO con un array JSON: per primo l'oggetto dell'apertura, poi un oggetto per \
articolo nello stesso ordine:
[{{"pmid": "apertura", "testo": "Questa settimana ..."}}, {{"pmid": "...", "testo": "..."}}]

ARTICOLI
{blocchi}"""


LOG_FILE = os.path.join(DIR_BASE, "newsletter_pocus.log")


def valida_config():
    mancanti = []
    if not ANTHROPIC_API_KEY: mancanti.append("ANTHROPIC_API_KEY")
    # In prova a vuoto non si invia nulla: le credenziali SMTP non servono,
    # così la prova gira anche in locale con la sola chiave Anthropic.
    if not DRY_RUN and not SOLO_FACEBOOK and not SOLO_INSTAGRAM:
        if not GMAIL_USER:         mancanti.append("GMAIL_USER_POCUS")
        if not GMAIL_APP_PASSWORD: mancanti.append("GMAIL_APP_PASSWORD")
    if mancanti:
        raise RuntimeError(
            f"Variabili d'ambiente mancanti: {', '.join(mancanti)}.\n"
            "Configurale nei GitHub Secrets."
        )
    return True
