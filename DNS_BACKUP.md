# Backup DNS villatrecolli.com (prima del passaggio a GitHub Pages)

- Data: 2026-11-11
- Record A @ (vecchio WordPress): **89.46.108.58**
- Record AAAA @ (vecchio WordPress): 2a00:6d40:4:1::c279:58
- DNS gestito da: dns.technorail.com

Per ripristinare: rimettere questi record A/AAAA su @ e togliere i 4 A di GitHub (185.199.108-111.153).

## Config DNS precedente (Aruba, visto nel pannello il 2026-11-11)
Pannello: Aruba, Name Server Aruba (dns.technorail.com, dns2.technorail.com, dns3.arubadns.net, dns4.arubadns.cz). Totale 46 righe, qui solo quelle viste.

| Tipo | Host | Valore | TTL |
|---|---|---|---|
| A | @ | 89.46.108.58 | 1 ora |
| AAAA | @ | 2a00:6d40:4:1::c279:58 | 1 ora |
| AAAA | www | 2a00:6d40:4:1::c279:58 | 1 ora |
| A | www | 89.46.108.58 (risolveva cosi', da verificare) | 1 ora |
| A | ftp | 89.46.104.211 | 1 ora |
| A | ftp | 89.46.104.218 | 1 ora |
| A | localhost | 127.0.0.1 | 1 ora |
| A | mail | 62.149.128.157, .151, .74, .166, .163, .160, .154 (prefisso 62.149.128.) | 1 ora |

Non toccati: mail, ftp, localhost, MX, TXT, NS.
Backup completo: nel pannello Aruba usare Esporta (BIND) e salvare qui il file.