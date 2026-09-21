# 01 — Toimintamalli

## Mitä työtila on

Yhden osakeyhtiön hallituksen työtila: rekisteri päätöksistä, kokoonpanosta ja toimivallan rajoista, sekä paikka kokousten väliselle työlle. Agentti toimii avustavana sihteerinä. Hallitus päättää.

## Tietuetyypit

| Tyyppi | Missä | Mitä |
|---|---|---|
| Kokous ja päätös | `decisions/` | Rekisterin ydin. Yksi tiedosto per tilikausi |
| Kokoonpano | `company/hallituksen-kokoonpano.yaml` | Toimikaudet ja jäsenet päivämäärärajattuina |
| Toimivallan raja | `company/toimivallan-rajat.yaml` | Mitä laki, yhtiöjärjestys, yhtiökokous ja osakassopimus edellyttävät hallitukselta |
| Vuosikelloasia | `annual-cycle/` | Toistuvat asiat |
| Havainto, idea, riski, esityslistaehdotus | `board-work/` | Kokousten välinen työ |
| Kokousluonnos | `meetings/` | Elää vain kokouksen ajan |

## Tilat

Jokaisella tietueella on tila, joka kertoo kuinka pitkälle se on vahvistettu:

- `provisional` — kirjattu, ei vahvistettu. Käytettävissä työskentelyssä.
- `confirmed` — puheenjohtaja tai toimitusjohtaja on tarkistanut. Riittää tasolle 1 ja 2.
- `formally_approved` — hallitus on hyväksynyt kokouksessa. Vaaditaan tasolla 3.
- `superseded` — korvattu uudemmalla. Tietue jää, uusi viittaa siihen.

Tilaa ei nosteta ilman sitä vastaavaa ihmisen tekoa.

## Kolme kirjoitustasoa

Kuvattu [`AGENTS.md`](../AGENTS.md):ssä. Lyhyesti: **taso 1** agentti saa kirjata luonnoksena · **taso 2** agentti ehdottaa, toimivaltainen henkilö hyväksyy · **taso 3** hallitus hyväksyy kokouksessa. Taso ei koskaan laske.

## Kaksi tilakenttää päätöksillä

`decision_text_status` (kokoustasolla) kertoo, onko päätösteksti kopio allekirjoitetusta asiakirjasta. `interpretation` (**päätöskohtainen lohko**: `status`, `confirmed_by`, `confirmed_at`) kertoo, onko agentin päätelmä päätöksen voimassaolosta ja yhteyksistä ihmisen vahvistama. Ne ovat eri asioita: teksti voi olla täydellinen kopio ja sen voimassaoloarvio silti vahvistamaton — ja saman kokouksen päätöksistä yksi voi olla vahvistettu ja toinen ei. Täysi kuvaus: [`03`](03-paatokset-ja-poytakirja.md).

## Johdettu tieto lasketaan, kirjoitettu tieto tarkistetaan

Päätösvaltaisuus, seuraava tunnus, poissaolijat ja allekirjoittajien vähimmäismäärä johdetaan rekisteristä (`scripts/tyotila.py`). Jos sama tieto on kirjoitettu rekisteriin käsin, validointi vertaa sen johdettuun ja ristiriita on virhe, ei näkökulmaero. Henkilöt viitataan `person_id`-tunnuksella kokoonpanorekisteriin; nimi tulostuu asiakirjaan sieltä.

## Yksi asiakirja on aina alkuperäinen

Allekirjoitettu pöytäkirja säilytyspaikassaan on virallinen. Rekisteri viittaa siihen nimellä. Ristiriidassa alkuperäinen ratkaisee ja rekisteri korjataan.
