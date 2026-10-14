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
