# Muutoshistoria

## 0.2.0 — 2026-09-21: kirjalliset rajat koneellisiksi

Vastaus kehitysarvioon [`KEHITYSARVIO-CLAUDELLE.md`](KEHITYSARVIO-CLAUDELLE.md) (21.9.2026). Sen ydinhavainto oli, että työtilan turvarajat olivat dokumentaatiossa mutta eivät koodissa. Tässä versiossa jokainen raja, jonka voi tarkistaa koneellisesti, tarkistetaan.

### Kriittiset (P0)

| # | Vaatimus | Toteutus |
|---|---|---|
| P0-1 | `--valmis` ei saa olla pelkkä bannerin poisto | `templates/tee-poytakirja.py` ajaa `scripts/tyotila.py`:n koko validoinnin ennen asiakirjaa. Yksikin ERROR → kieltäytyy (paluuarvo 2), tulostaa virheluettelon, ei tuota mitään. Luonnos syntyy aina ja kantaa virhe-/varoitusmäärän bannerissa. Valmis-tila lisää ehdot: puheenjohtajan sanamuotovahvistus, allekirjoittajat, koollekutsu vahvistettu, `decision_text_status` ei saa olla jo `kopio` |
| P0-2 | Osallistujat ja menettelytiedot rekisteristä | Pohjissa ei ole nimiä. Generaattori täyttää `person_id`-viittauksista: puheenjohtaja, läsnä olleet jäsenet, sijaisena toimineet varajäsenet (kenen sijasta), poissa olleet, toimitusjohtaja, sihteeri, kutsutut, esteellisyydet ja poistuminen, äänestystulokset, eriävät mielipiteet, allekirjoittajat |
| P0-3 | Päätöskohtainen päätösvaltaisuus | `johda_paatoksen_paatosvaltaisuus()`: esteellinen ei osallistu, nimittäjänä valitut jäsenet. Kokoustason `quorum` säilyy yleistietona. Käsin kirjoitettu `decision_quorum` tarkistetaan johdettua vasten |
| P0-4 | Päätös ilman kokousta omana prosessina | `decision_method: without_meeting` + `without_meeting`-lohko (ehdotuksen lähetys, määräaika, jäsenkohtaiset kannat, todentamistapa), `session: null`, oma pohja `paatospohja-ilman-kokousta.docx` ilman avaus-/päättämispykäliä, sama juokseva PTK-sarja. Yksimielisyysvaatimus poistettu dokumentaatiosta ja merkitty `provisional`-kysymykseksi |
| P0-5 | Allekirjoitusmallin oletus | `chair_plus_one` (OYL 6:6 §:n vähimmäisvaatimus), `includes_absent_members: false`, yksijäsenisessä hallituksessa jäsen itse. `reviewed_by` erotettu allekirjoituksesta. Poissa ollut allekirjoittaja → varoitus "ei tee osallistujaa". Yhtiö voi valita `all_members_in_term` |

### Tietomalli (P1-1 … P1-5)

- `interpretation`-lohko päätöskohtaiseksi (`status`, `confirmed_by`, `confirmed_at`, `note`); `ihmisen_vahvistama` vaatii vahvistajan ja päivän.
- `notice`-lohko kokoustietueeseen (`sent_at`, `sent_by`, `channel`, `invited_person_ids`, `deputy_invited_for`, `materials_sent_at`, `participation_opportunity_confirmed`).
- `decisions/README.md`:n käsin ylläpidetyt "Seuraava kokous / päätös" -rivit poistettu. Validaattori laskee ne kaikista rekisteritiedostoista ja tarkistaa päällekkäiset tunnukset, aukot, väärän etuliitteen, pienenevän numeron ja katkenneet viittaukset.
- `AGENTS.md`: käynnistyksessä luetaan kaikki rekisteritiedostot (tai ajetaan validaattori), ei vain uusinta.
- `roles`-lohko: `meeting_chair_person_id`, `secretary_person_id`, `ceo_participation`; `deputy_substitutions`; `invited_participants` rakenteisena.
- `conflict_of_interest` hyväksyy lyhyen muodon `none` ja täyden objektin (`status`, `disqualified_person_ids`, `left_room`, `note`).
- `vote` laajennettu: `abstained`, `chair_casting_vote`, `votes[]`, `dissenting_opinions[{person_id, text}]`.
- Kokoonpanorekisteri skeema 2: `quorum_rule` (yhtiöjärjestyksen tiukennus), `signature_policy`, `review_policy`.

### Validointi, testit, riippuvuudet (P1-6 … P1-9)

- `schema/*.schema.json` — JSON Schema 2020-12 kaikille YAML-tiedostoille.
- `scripts/validoi-tyotila.py` — koko työtilan validaattori, tasot ERROR / WARNING / INFO, paluuarvo 1 estävästä virheestä.
- `tests/test_tyotila.py` — 24 testiä: kehitysarvion 15 skenaariota, MALLI-tiedoston kelpoisuus, generaattori väliaikaisessa työtilassa (luonnos, valmis, kieltäytyminen, päätös ilman kokousta), sisältötarkistus.
- `requirements.txt` — python-docx, PyYAML, jsonschema.

### Tietosuoja ja tietoturva (P1-10 … P1-12)

- Henkilötunnuksen tunnistus kattaa vuosisatamerkit `+ - Y X W V U A B C D E F` ja laskee tarkistusmerkin (HETU vs. HETU?; molemmat estävät). Salaisuuksien tunnetut muodot. **Word-tiedostot tarkistetaan** (runko, ylä-/alatunnisteet, kommentit). Tarkistamatta jääneet binaarit luetellaan nimeltä; tarkistus ei väitä niitä puhtaiksi.
- `.githooks/pre-commit` (sisältö + rakenne) ja `.github/workflows/tarkistukset.yml` (sisältö + rakenne + testit). Haaran suojauksen maksullisuus dokumentoitu.
- Käyttöoikeus-, varmuuskopiointi- ja arkistointimalli: `company/yhtio.yaml → access_and_continuity`, `governance/07`, `ALOITUS.md` vaihe 9.

### Vuosikello (luku 7)

- `optional_catalog` (VK-OPT-01 … 13): agentti tarjoaa yhtiökohtaisesti valittaviksi, ei pakollisia.

### Oikeudellisesti tarkistettavat väitteet (luku 8)

Kaikki seitsemän kohtaa on lueteltu `governance/05`:n taulukossa **Oikeudellisesti tarkistettavat kohdat** tilassa `provisional`. Kaksi virheellistä väitettä korjattiin heti: (1) päätös ilman kokousta ei lain sanamuodon mukaan edellytä kaikkien jäsenten suostumusta vaan osallistumismahdollisuuden varaamista — yhtiöjärjestys tai työjärjestys voi vaatia enemmän; (2) OYL 6:6 § ei edellytä kaikkien osallistujien yksilöintiä vaan allekirjoitukset, juoksevan numeroinnin ja eriävän mielipiteen merkitsemisen — osallistujien nimeäminen perustuu päätösvaltaisuuden ja esteellisyyden todentamiseen. Juristin tarkistus on tekemättä; Finlexin säädösteksti ei ole koneellisesti luettavissa, joten viittaukset on tarkistettava käsin.

### Hyväksymiskriteerit (luku 9)

- [x] päätös ilman kokousta toimii rakenteessa ja asiakirjatuotannossa
- [x] päätöskohtainen esteellisyys ja päätösvaltaisuus lasketaan
- [x] osallistujat ja roolit tulevat rekisteristä
- [x] äänestykset ja eriävät mielipiteet tulevat pöytäkirjaan
- [x] `--valmis` edellyttää hyväksyttyä validointia
- [x] allekirjoitusmalli ei sekoita osallistumista ja tarkastamista
- [x] tunnukset lasketaan ja validoidaan koneellisesti
- [x] kaikki päätösrekisterit huomioidaan voimassaolokyselyissä
- [x] YAML-rakenteilla on skeema
- [x] keskeiset prosessit on testattu automaattisesti
- [x] riippuvuudet on dokumentoitu
- [x] henkilötunnustarkistus kattaa nykyiset muodot ja Word-tiedostot
- [x] käyttöoikeus-, varmuuskopiointi- ja arkistointiohje on dokumentoitu
- [ ] **oikeudelliset väitteet on tarkistettu** — vaatii juristin; kohdat `provisional`

### Rajaukset

- Skripti ei kirjoita rekisteriin koskaan, ei myöskään johdettuja arvoja. Ihminen kirjaa, kone tarkistaa.
- Word-tarkistus ei näe kuvina upotettua tekstiä eikä xlsx-/pdf-tiedostoja.
- `hetu`-tunnistus ei ole aukoton: väärin muotoiltu tai välilyönnein katkottu tunnus jää huomaamatta.

## 0.1.0 — 2026-09-21

Ensimmäinen runko: governance-dokumentit, rekisterimallit, vuosikello, kokousluonnos, Issue-pohjat, pöytäkirjageneraattori, sisältötarkistus, lisenssit (CC BY 4.0 dokumentaatio, BSD-3-Clause skriptit).
