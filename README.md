# Hallituksen työtila — template suomalaiselle osakeyhtiölle

Tämä on **hallituksen avustavan sihteerin työtila**: paikka, jossa yhden osakeyhtiön hallituksen päätökset, kokoukset, muistiinpanot ja toimivallan rajat pysyvät järjestyksessä ja löydettävinä — ja jossa tekoälyagentti auttaa kirjaamisessa ilman että se koskaan päättää mitään.

Se on tarkoitettu **listaamattomille yhtiöille**: operatiivisille yhtiöille, holding-yhtiöille, kiinteistöosakeyhtiöille ja perheyrityksille, joissa hallitus tekee oikeaa työtä mutta jossa ei ole erillistä sihteeristöä.

## Mitä tämä on — ja mitä ei

**On:**
- Päätösrekisteri, josta näkee mitä on päätetty, milloin, millä perusteella ja sitooko se yhä
- Kokoonpanorekisteri, josta näkee kuka oli hallituksen jäsen minäkin päivänä
- Toimivallan rajat yhtiöjärjestyksestä, yhtiökokouksista ja osakassopimuksesta — vain hallitusta koskevat kohdat
- Vuosikello, kokousluonnokset, havainnot ja esityslistaehdotukset
- Pöytäkirjan — ja päätöksen ilman kokousta — muodostaminen rekisteristä Word-pohjalle. Osallistujat, esteellisyydet, äänestykset ja allekirjoittajat tulevat rekisteristä, ei pohjaan käsin kirjoitetuista nimistä
- Koneellinen tarkistus: skeema, tunnusten eheys, päätösvaltaisuus jokaisessa asiassa, koollekutsu, allekirjoittajat. **Valmis asiakirja syntyy vain, kun tarkistus on puhdas**

**Ei ole:**
- **Ei määrittele, miten hallituksen pitäisi työskennellä.** Se kirjaa sen, mitä hallitus tekee.
- **Ei ole oikeudellista neuvontaa** eikä takaa osakeyhtiölain noudattamista. Ks. vastuuvapaus alla.
- **Ei korvaa allekirjoitettua pöytäkirjaa.** Rekisteri on kopio; allekirjoitettu asiakirja on aina se, joka ratkaisee.
- **Ei ole tekoälyn päätöksentekoa.** Agentti valmistelee, ehdottaa ja kirjaa. Ihminen päättää ja vahvistaa, aina.

## Miksi tällainen työtila

Keskuskauppakamarin *Asialuettelo listaamattomien yhtiöiden hallinnoinnin kehittämiseksi* (2016) sanoo sen näin:

> Pöytäkirjat numeroidaan juoksevasti ja säilytetään luotettavasti. Pöytäkirjasta ja sen liitteistä on jälkikäteen todettavissa tehdyt päätökset ja niiden perustelut. Hyvin laadittu pöytäkirja liitteineen auttaa hallitusta osoittamaan että se on toiminut huolellisuusvelvollisuuden mukaisesti.

Päätösrekisteri perusteluineen on se näyttö, jolla huolellisuusvelvollisuus osoitetaan jälkikäteen. Tämä työtila on olemassa sitä varten — ei työkalun vuoksi.

## Käyttöönotto

1. **Luo oma repo tästä templatesta** (GitHub: *Use this template*). Pidä se **yksityisenä** — hallituksen aineisto ei kuulu julkiseksi.
2. **Avaa repo tekoälyagentissa**, joka lukee `AGENTS.md`:n (esim. Claude Code, Cursor).
3. **Sano agentille: "Aloita käyttöönotto"** — tai avaa itse [`ALOITUS.md`](ALOITUS.md). Agentti kysyy yhtiön perustiedot, hallituksen kokoonpanon, aiemmat pöytäkirjat ja kokousrytmin, ja täyttää työtilan niiden perusteella.

Tarvitset: Git-tilin, tekoälyagentin ja Python 3:n. Python-riippuvuudet asennetaan `pip install -r requirements.txt` (python-docx, PyYAML, jsonschema).

## Rakenne

```
ALOITUS.md         käyttöönottokysely — tästä aloitetaan
AGENTS.md          agentin sitovat toimintarajat
governance/        miten työtila toimii: kirjaaminen, päätökset, vuosikello, rajat
company/           yhtiön perustiedot, kokoonpanorekisteri, toimivallan rajat
decisions/         päätösrekisteri tilikausittain
meetings/          kokousluonnokset (elävät vain kokouksen ajan)
annual-cycle/      vuosikello
board-work/        havainnot, ideat, riskit, esityslistaehdotukset
templates/         asiakirjapohjat (kokous, päätös ilman kokousta) ja generaattori
schema/            koneelliset skeemat YAML-tiedostoille
scripts/           validaattori, sisältötarkistus, yhteinen kirjasto
tests/             sääntötestit (python -m unittest discover -s tests)
```

Kansioiden ja YAML-kenttien nimet ovat englanniksi, sisältö suomeksi. Näin tekniset nimet pysyvät vakaina, kun sisältöä muokataan.

## Tarkistukset — kirjalliset rajat koneellisesti valvottuina

| Komento | Mitä tekee |
|---|---|
| `python scripts/validoi-tyotila.py` | Skeema, tunnusten eheys (ei aukkoja, ei kahdesti), kokoonpanon aikarajat, päätösvaltaisuus kokous- **ja päätöskohtaisesti** (esteellinen ei osallistu), koollekutsu, allekirjoittajat, viittaukset. Tulostaa seuraavat vapaat tunnukset ja voimassa olevien päätösten määrän kaikista tilikausista. Paluuarvo 1, jos estävä virhe |
| `python scripts/tarkista-sisalto.py` | Henkilötunnukset (kaikki vuosisatamerkit, tarkistusmerkki), salaisuudet, kielletyt merkkijonot — tekstitiedostoista **ja Word-tiedostoista**. Luettelee tiedostot, joita ei voinut tarkistaa |
| `python templates/tee-poytakirja.py PTK-000073` | Luonnos aina; `--valmis` vain, jos validointi on puhdas — muuten kieltäytyy ja tulostaa virheluettelon. Parametri ei ohita porttia |
| `python -m unittest discover -s tests` | Sääntötestit: 15 skenaariota (yksijäseninen hallitus, varajäsen, esteellisyys, äänestys, päätös ilman kokousta, …) |

Samat tarkistukset ajetaan commit-koukussa (`git config core.hooksPath .githooks`) ja GitHub Actionsissa (`.github/workflows/tarkistukset.yml`). Löydöksillä on kolme tasoa: **ERROR** estää valmiin pöytäkirjan, **WARNING** vaatii ihmisen tarkistuksen, **INFO** on huomio.

## Periaatteet, joihin kaikki nojaa

1. **Rekisteri on kopio, allekirjoitettu pöytäkirja on alkuperäinen.** Jokainen päätösteksti kantaa tiedon siitä, onko se kopio vai odottaako se allekirjoitusta.
2. **Kopio ja tulkinta ovat eri asioita.** Se, sitooko päätös yhä, on tulkinta — ja tulkinta on merkitty vahvistamattomaksi kunnes ihminen vahvistaa sen.
3. **Menettelypykälät eivät ole päätöksiä.** Kokouksen avaus, päätösvaltaisuus ja esityslistan hyväksyminen kirjataan kokouksen ominaisuuksina, eivät päätöstunnuksina. Päätösvaltaisuus lasketaan kokoonpanosta, ei kirjoiteta — ja se lasketaan **jokaiselle asialle erikseen**, koska esteellinen jäsen ei osallistu asian käsittelyyn.
4. **Numerointi on juoksevaa ja jatkuvaa.** Kokous 73, ei 8/2026.
5. **Henkilötunnuksia ei kirjata koskaan.** Ei sopimusten sisältöä — vain hallitusta koskevat rajoitteet.
6. **Yhtiökokous on työtilan yläpuolella.** Sen pöytäkirjoja ei rekisteröidä päätöksinä; niistä poimitaan hallitusta koskevat velvoitteet.
7. **Kirjallinen raja on koneellinen raja.** Se, mitä nämä dokumentit kieltävät, tarkistetaan skripteillä: valmis asiakirja, tunnukset, päätösvaltaisuus, henkilötunnukset. Agentti ei voi ohittaa porttia parametrilla.

Täysi kuvaus: [`governance/`](governance/README.md).

## Vastuuvapaus

Tämä työtila ja sen ohjeet **eivät ole oikeudellista neuvontaa**. Ne on laadittu yleiseksi apuvälineeksi eikä niiden käyttö takaa osakeyhtiölain, yhtiöjärjestyksen tai muun sääntelyn noudattamista. Hallitus vastaa aina itse toiminnastaan ja päätöksistään. Jos et ole varma jonkin kirjauksen tai menettelyn oikeellisuudesta, kysy asiantuntijalta. **Osakeyhtiölakia koskevat kohdat, joita ei ole tarkistettu yhtiöoikeuteen perehtyneellä juristilla, on merkitty `provisional`-tilaan** [`governance/05`](governance/05-lainmukaisuus-ja-rajat.md):ssä. Tekijä ei vastaa työtilan käytöstä aiheutuvista vahingoista.

## Lisenssi

- Dokumentaatio ja pohjat (`.md`, `.yaml`, asiakirjapohjat): **CC BY 4.0** — [`LICENSE-DOCS`](LICENSE-DOCS)
- Skriptit: **BSD-3-Clause** — [`LICENSE`](LICENSE)

**Yhtiön oma työtila, joka on luotu tästä templatesta, ei tarvitse mainintaa lähteestä.** Nimeämisvelvoite koskee vain templaten itsensä levittämistä ja julkaisemista.

## Lähteet

- Osakeyhtiölaki (624/2006), erityisesti 6 luku (hallitus) ja 5 luku (yhtiökokous)
- Keskuskauppakamari: *Asialuettelo listaamattomien yhtiöiden hallinnoinnin kehittämiseksi* (2016)

## Osallistuminen

Havainnot ja ehdotukset Issueina. Muutokset pull requesteina. Älä koskaan lähetä tänne oman yhtiösi hallitusaineistoa — tämä repo on julkinen.
