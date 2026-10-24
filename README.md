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
- `mostra_dal`: non mostrarlo prima di quella data. `attivo: false`: sospende l'avviso senza cancellarlo.
- Al massimo **2 corsi** per uscita, i piu' vicini nel tempo.
- Un esempio completo e' in `corsi.esempio.json`.
- Se il file ha un errore, la newsletter parte lo stesso senza avvisi e il run di GitHub Actions mostra un avviso giallo ("Controlla corsi.json"). `python corsi.py` lo controlla in locale.
