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
GIORNI_RICERCA_ESTESO = 14  # fallback se la settimana è troppo povera
ARTICOLI_FINALI = 5   # numero articoli nel digest finale
ARTICOLI_RICHIESTI = 8  # quanti chiederne al modello: i 3 in più sono la riserva
                        # da cui il codice attinge per rispettare i vincoli
MIN_EM_GEN = 2        # minimo di articoli dal nucleo tematico (eco/em)
GRUPPI_PRIORITARI = {"eco", "em"}
ETICHETTA_GRUPPO = {"eco": "ecografia", "em": "urgenza",
                    "gen": "generale", "spec": "specialistica"}
MINIMO_ARTICOLI = 3   # sotto questa soglia scatta il fallback di riempimento
MAX_PER_TEMA    = 2   # max articoli sullo stesso tema clinico nello stesso digest
MAX_CANDIDATI_PROMPT = 150  # tetto di candidati inviati al filtro (protegge i token)

# Token per tipo di chiamata.
# NB: NON reintrodurre il parametro "temperature": è deprecato per questo modello
# e l'API risponde 400 (verificato sul run del 03/08/2026).
MAX_TOKENS_FILTRO          = 800
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
    "Retracted Publication", "Expression of Concern", "Case Reports", "News",
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
LOGO_URL        = "https://raw.githubusercontent.com/areacriticaprontosoccorso/newsletter-pocus/main/logo.jpg"
NEWSLETTER_PAGE_URL = "https://areacriticaprontosoccorso.github.io/newsletter-pocus/"

# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT CLAUDE
# ═══════════════════════════════════════════════════════════════════════════════
# Contesto operativo del PS. Serve al filtro per scartare articoli inapplicabili
# (percorsi organizzativi esteri, farmaci non in commercio in Italia, risorse assenti).
CONTESTO_POCUS = """CONTESTO DEL LETTORE:
- Medici di Pronto Soccorso, Medicina d'Urgenza e Area Critica che praticano
  ecografia clinica al letto del paziente (POCUS), in un DEA di II livello
  urbano di Torino, Servizio Sanitario Nazionale italiano.
- Casistica adulta indifferenziata, con quota rilevante di anziani fragili.
- L'ecografo è disponibile in shock room, in OBI e nelle sale visita;
  l'esame lo esegue e lo interpreta il medico d'urgenza, non il radiologo.

COSA RENDE UN ARTICOLO PERTINENTE: deve riguardare l'ecografia eseguita dal
clinico al letto del paziente per rispondere a una domanda binaria e immediata,
oppure per guidare una procedura. Il criterio non è che l'articolo nomini
l'ecografia, ma che cambi il modo in cui il lettore impugna la sonda o
interpreta ciò che vede.

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
- Case report e case series.
- Studi su sistemi sanitari non europei senza trasferibilità.

ARTICOLI CANDIDATI:
{articoli}

IMPORTANTE - LUNGHEZZA DELLA GRADUATORIA: devi restituire ESATTAMENTE {n} voci,
non {n_finali}. Ne verranno pubblicate soltanto le prime {n_finali}: le voci
successive sono la riserva da cui il sistema attinge per rispettare i vincoli di
composizione, e servono anche quando sono meno interessanti delle prime.
Restituisci meno di {n} voci solo se i candidati davvero pertinenti sono meno.
Meglio una graduatoria corta che riempita con articoli in cui l'ecografia è
marginale.

FORMATO DI RISPOSTA - restituisci SOLO un array JSON valido, senza testo prima o
dopo, senza blocchi markdown. Scegli esclusivamente PMID presenti nella lista qui
sopra: non inventare né modificare PMID.

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
LOG_FILE = os.path.join(DIR_BASE, "newsletter_pocus.log")


def valida_config():
    mancanti = []
    if not ANTHROPIC_API_KEY: mancanti.append("ANTHROPIC_API_KEY")
    # In prova a vuoto non si invia nulla: le credenziali SMTP non servono,
    # così la prova gira anche in locale con la sola chiave Anthropic.
    if not DRY_RUN:
        if not GMAIL_USER:         mancanti.append("GMAIL_USER_POCUS")
        if not GMAIL_APP_PASSWORD: mancanti.append("GMAIL_APP_PASSWORD")
    if mancanti:
        raise RuntimeError(
            f"Variabili d'ambiente mancanti: {', '.join(mancanti)}.\n"
            "Configurale nei GitHub Secrets."
        )
    return True
