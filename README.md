# newsletter-pocus

## Selezione scientifica POCUS (aggiornamento)

Il digest usa ESearch per cercare POCUS in **tutta PubMed** (ultimi 7 giorni,
**EDAT** = data di indicizzazione), EFetch per acquisire gli abstract completi
e una classificazione clinica con Claude **obbligatoria su ogni candidato**.

Nessun articolo viene aggiunto per raggiungere il numero minimo o massimo.
Anche un solo articolo verificato puo' essere pubblicato. Se il filtro AI non
risponde, il digest non viene inviato e GitHub Actions segnala l'errore.

Test offline: `python -m unittest discover -s tests -v`.

### Nota privacy
Il repository pubblico include `subscribers.json` con email dei destinatari.
Migrare l'elenco su storage privato prima di rimuovere il file; serve anche
affrontare la cronologia Git, poiche' la cancellazione ordinaria lascia visibili
i dati nelle commit precedenti.

## Avvisi dei corsi

I corsi organizzati da Francesco Panero compaiono ogni settimana, finche' non sono passati:
in cima alla mail, in un messaggio Telegram subito dopo l'intestazione, e in un post Facebook programmato sulla Pagina (un corso al giorno, alle 12:30).
Si gestiscono dal file **`corsi.json`** (da GitHub: apri il file, matita, modifica,
*Commit changes*). Nessuna modifica al codice.

```json
{
  "corsi": [
    {
      "titolo": "Corso base di ecografia in emergenza-urgenza",
      "data_inizio": "2026-11-14",
      "data_fine": "2026-11-15",
      "ora": "9:00–17:00",
      "luogo": "Torino, Ospedale San Giovanni Bosco",
      "descrizione": "Due giornate con parte pratica su simulatori e modelli vivi.",
      "posti": "Massimo 20 partecipanti",
      "iscrizioni_fino": "2026-11-07",
      "link": "https://...",
      "newsletter": ["pocus", "niv"],
      "mostra_dal": "2026-10-01",
      "attivo": true
    }
  ]
}
```

- Obbligatori: `titolo` e `data_inizio` (formato `AAAA-MM-GG`). Tutto il resto e' facoltativo.
- `data_fine`: per i corsi di piu' giorni. L'avviso resta fino all'ultimo giorno incluso, poi sparisce da solo.
- `newsletter`: dove mostrarlo (`pocus`, `niv`); se manca, compare in entrambe.
- `ogni_settimane`: frequenza dell'avviso (es. `2` = a settimane alterne; se manca, ogni settimana). L'ultima uscita prima del corso lo annuncia sempre; con `mostra_dal` le settimane si contano da quella data.
- `mostra_dal`: non mostrarlo prima di quella data. `attivo: false`: sospende l'avviso senza cancellarlo.
- Al massimo **2 corsi** per uscita, i piu' vicini nel tempo.
- `immagine`: locandina del corso. Carica il file nella cartella `locandine/` (GitHub: *Add file > Upload files*) e scrivi `"immagine": "locandine/nome-file.jpg"`; in alternativa un URL `https://...`. Formati jpg, png, gif, massimo 5 MB (meglio sotto 1 MB). Compare in cima all'avviso nella mail (cliccabile se c'e' il `link`), come foto su Telegram e come foto nel post Facebook. Se il file manca o e' troppo grande l'avviso esce senza locandina.
- Un esempio completo e' in `corsi.esempio.json`.
- Se il file ha un errore, la newsletter parte lo stesso senza avvisi e il run di GitHub Actions mostra un avviso giallo ("Controlla corsi.json"). `python corsi.py` lo controlla in locale.

## Instagram

Il mercoledì, dopo la mail, esce su Instagram **un carosello** con le schede degli articoli e la locandina del corso POCUS. Le diapositive sono
JPEG 4:5 (1080x1350): le schede e le locandine stanno intere, con bande bianche ai lati. Nel testo
ci sono l'elenco degli articoli, i corsi in programma e `www.ecm.unito.it`; la didascalia rispetta i
limiti di Instagram (2200 caratteri, 30 hashtag). La locandina esce ogni settimana, a prescindere
dalla frequenza dell'avviso su Telegram e in mail.

**Schede essenziali.** Le schede di Instagram sono diverse da quelle della mail e di Facebook: solo
numero, tipo di studio, rivista e data, titolo (in italiano) e il riquadro «Perché conta» (la rilevanza;
in mancanza, la prima frase della sintesi), con il PubMed ID. I caratteri si adattano da soli alla
lunghezza del titolo. Il codice è `instagram.py` (`dati_scheda`, `html_scheda`, `genera_schede`).

**Loghi in chiusura.** L'ultima diapositiva del carosello e l'ultima dei Reel (3 s; anche in coda all'estratto del podcast, in EM) è sempre `loghi/chiusura.png`, con i tre loghi (Medicina d'Emergenza-Urgenza, Pronto Soccorso Area Critica, Emergency Ultrasound School Turin). Per cambiarla basta sostituire il file (1080x1350); `IG_LOGHI` in `config.py` ne indica il percorso.

**Reel delle schede.** Subito dopo il carosello esce un Reel 9:16 con le stesse diapositive, una dopo
l'altra: 3 s la copertina, da 5 a 8 s ogni scheda (secondo le parole da leggere), 4 s ogni locandina.
Le diapositive stanno in un riquadro 4:5 sotto i 240 px di sopra, che l'app copre col profilo. Senza
musica: se esiste il file `IG_MUSICA` (`musica/sottofondo.mp3` nel repo), viene messo sotto, a volume
basso e con dissolvenza finale. Va scelta una traccia senza diritti d'autore e con licenza che consenta
l'uso commerciale. `IG_REEL_SCHEDE = False` in `config.py` spegne il Reel.
Il Reel si carica con l'upload «resumable» dell'API (`rupload.facebook.com`), senza indirizzi pubblici.
Non è stato provato con l'API reale (nei test è simulata): se il primo Reel non esce, nel log cerca
«Instagram: Reel non pubblicato».

Serve un account Instagram **Business o Creator collegato alla Pagina Facebook**, e tre secret del repo:
`FB_PAGE_ID`, `FB_PAGE_TOKEN` (il token deve avere i permessi `instagram_basic`,
`instagram_content_publish` e `pages_read_engagement`) e `IG_USER_ID` (l'ID dell'account Instagram).
Facoltativo: `IG_PAGE_TOKEN`, un token solo per Instagram; se c'è si usa quello e `FB_PAGE_TOKEN`
(i post Facebook) non va toccato, altrimenti Instagram usa `FB_PAGE_TOKEN`.
Senza `IG_USER_ID` non succede nulla; `IG_ABILITATO=0` lo spegne. Le diapositive passano dalla Pagina
come foto **non pubblicate** (Instagram scarica da lì l'indirizzo pubblico): nulla compare su Facebook.
Un errore Instagram non blocca mai l'invio. Con `dry_run` non si chiama nessuna API: diapositive, Reel (`reel-schede.mp4`) e didascalia finiscono nell'artefatto del run (cartella `instagram/`). Il codice sta in `instagram.py`.

