# servizi.lazio: mirror statico di servizi.lazio.it

Repo `cialdecompatibili-netizen/servizi.lazio`, cartella `Desktop\repository\servizi.lazio`. Anteprima: https://cialdecompatibili-netizen.github.io/servizi.lazio/ . Il sito originale (WordPress + Avada 6.2.2) e' di Mirco: si puo' copiare. Quando e' pronto i DNS di `servizi.lazio.it` passano qui (serve il file `CNAME`, ancora da mettere). Obiettivo: stessi URL, stessa struttura, aspetto simile ad Avada.

## Cose che funzionano

- **Contenuti dall'API REST pubblica di WordPress** (nessuna credenziale): `claudetemp\lazio_import.py` importa articoli, portfolio, categorie sotto `/servizi/...` e le immagini con lo stesso percorso `/wp-content/uploads/...`.
- **Mirror fedele delle pagine**: `claudetemp\lazio_mirror.py` scarica l'HTML Avada di ogni URL della sitemap e lo riscrive con URL relativi e asset locali; toglie WooCommerce, CF7 e cdn-cgi, decodifica le email Cloudflare ed esclude lo spam (`SKIP`). Alla fine lancia `lazio_clean_hidden`, `lazio_clean_spam` e `lazio_toc`, quindi rifare il mirror rilancia da solo la bonifica.
- **Verifica URL per URL**: `python lazio_import.py verifica <_site>` confronta sitemap e API con la build. Ultimo esito: 167 su 167, 0 mancanti, 0 immagini rotte. Non dire "fatto" senza questo risultato.
- **Controllo link rotti e residui**: `claudetemp\lazio_audit.py` (link/asset morti, shortcode, liquid, form, link assoluti al vecchio dominio).
- **Checkpoint prima di toccare la repo**: branch `checkpoint-2026-10-18`.
- **Spam del sito hackerato**: escluso il post `/blog/online-kasyno-vavada/` e le categorie `/servizi/casino/`, `/servizi/steroid-6/`, `/servizi/bez-rubriki/` (danno 404 di proposito). Rimossi anche i link nascosti iniettati nelle pagine e controllate le versioni codificate (%D0..., #Mostbet_...). Ultimo deploy pulito: `bcb892f`.
- **Indice (TOC)**: solo negli articoli, mai in home.

## Ancora da fare

- Link morti in home: `about/`, `get-quote/`, `work/`, `construction-articles/` (404) e `author/admin/`; `/admin/` rimanda a `wp-admin`. Servono destinazioni sensate.
- Form di contatto CF7: nel mirror non funzionano. Collegarli al Worker `contatti-form` (vedi punto 32 di `CLAUDE.md`).
- Logo: `wp-content/uploads/2020/05/logo-araldico-ultimo-effettivo-leone-nero-giallo.jpg` e' gia' scaricato dal mirror; da adattare al resto.
- Pagine demo del template ecommerce (`/negozio/`, `/carrello/`, `/ordine/`, `/chi-siamo/`, blog di prova, 8 servizi di esempio) da togliere prima dei DNS.
- File `CNAME` con `servizi.lazio.it` e sitemap rigenerata.
- Cambiare le password di WordPress, FTP e hosting prima di spostare i DNS.
