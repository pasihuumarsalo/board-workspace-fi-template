# 07 — Tietosuoja ja luottamuksellisuus

## Mitä tänne ei kirjata

- **Henkilötunnuksia** — ei koskaan, ei vaikka ne olisivat lähdeasiakirjassa. Nimi riittää yksilöintiin, koska hallituksen jäsenet ovat kaupparekisterissä. `scripts/tarkista-sisalto.py` tunnistaa henkilötunnuksen muodon kaikilla vuosisatamerkeillä, tarkistaa tarkistusmerkin ja lukee myös Word-tiedostot — ja estää commitin.
- **Sopimusten sisältöä** — osakassopimuksesta ja johtajasopimuksista vain hallitusta koskevat velvoitteet tiivistettynä.
- **Terveystietoja, palkkatietoja tai muuta arkaluonteista** yksityiskohtina. Päätös kirjataan sen tasolla, millä hallitus sen teki ("päätettiin toimitusjohtajan palkkiosta liitteen mukaan"), ja yksityiskohta jää alkuperäiseen asiakirjaan.
- **Ulkopuolisten henkilöiden nimiä**, ellei päätös menetä merkitystään ilman niitä. Vastapuolet, pankkien toimihenkilöt ja työntekijät kuvataan roolinsa kautta.
- **Salaisuuksia** — ei avaimia, tokeneita eikä salasanoja mihinkään tiedostoon. Sisältötarkistus tunnistaa yleisimmät muodot.

## Kenen nimet kirjataan

Hallituksen jäsenet, varajäsenet ja toimitusjohtaja nimetään. Peruste: pöytäkirjasta on voitava jälkikäteen todeta, ketkä osallistuivat päätöksentekoon, jotta päätösvaltaisuus (OYL 6:3 §) ja esteellisyys (6:4 §) ovat todennettavissa ja huolellisuusvelvollisuus (1:8 §) osoitettavissa; tieto on julkinen kaupparekisterissä. *Korjaus aiempaan:* OYL 6:6 § ei sanamuodoltaan edellytä osallistujien yksilöintiä — se koskee allekirjoituksia, eriävää mielipidettä, numerointia ja säilytystä ([`05`](05-lainmukaisuus-ja-rajat.md), kohta 2). Se on **nimen kirjaamisen peruste, ei lupa kirjata muuta** — jäsenen yhteystietoja, osoitetta tai muita henkilötietoja ei tallenneta tänne.

## Käyttöoikeusmalli

Kirjataan `company/yhtio.yaml → access_and_continuity` käyttöönotossa (ALOITUS.md, vaihe 9). `null` tarkoittaa "ei ratkaistu", ei oletusta.

1. **Repo on aina yksityinen.** Hallituksen aineisto ei kuulu julkiseksi.
2. **Kaksivaiheinen tunnistautuminen tai passkey** vaaditaan kaikilta, joilla on pääsy.
3. **Kirjoitusoikeus vain sitä tarvitseville** — yleensä yhdellä ylläpitäjällä. Jäsenille lukuoikeus riittää; se riittää myös Issueiden avaamiseen.
4. **Oikeudet tarkistetaan jokaisen kokoonpanomuutoksen yhteydessä.** Kun kokoonpanorekisteriin kirjataan jäsenen `valid_until`, samalla poistetaan hänen pääsynsä repoon.
5. **Tekoälypalvelun käyttöoikeus poistetaan samalla.** Jos jäsen on käyttänyt agenttia, joka lukee tätä repoa, myös se yhteys puretaan — pelkkä GitHub-oikeuden poisto ei riitä, jos palvelulla on oma kopio tai istunto.
6. **Arkaluonteista aineistoa ei viedä Issueihin.** Issue on nosto, ei säilö; sen sisältö näkyy kaikille lukuoikeudellisille eikä sitä voi rajata.
7. **Varmuuskopiointi ja palautustesti määritellään.** GitHub ei ole arkisto. Sovitaan, miten repo kloonataan yhtiön omaan säilytykseen ja milloin palautus viimeksi kokeiltiin.
8. **Allekirjoitettu alkuperäinen säilytetään erillisessä luotettavassa arkistossa** (`minutes_archive`), ei tässä repossa. Repo on rekisteri ja työtila; alkuperäinen on muualla.
9. **Haaran suojaus.** Yksityisissä repoissa branch protection ja rulesetit vaativat maksullisen GitHub-tason. Jos sitä ei ole, CI-tarkistus (`.github/workflows/tarkistukset.yml`) on ilmoitus, ei portti — ja paikallinen commit-koukku on ainoa este ennen pushia. Tilanne kirjataan `branch_protection`-kenttään.

Organisaatiotasolla varmista, ettei tiimijäsenyys avaa muita repoja (`default_repository_permission: none`).

## Tekoälyn käsittely

Kaikki mitä agentti lukee tässä repossa kulkee tekoälypalvelun rajapintaan. Ennen käyttöönotettoa yhtiön on syytä tietää ja kirjata (`access_and_continuity.ai_service`):

- Millä sopimuksella palvelu käsittelee tietoa (käsittelijäsopimus / DPA)
- Missä tieto käsitellään ja säilytetään
- Käytetäänkö sitä mallien koulutukseen — kaupallisissa ehdoissa yleensä ei, kuluttajaehdoissa mahdollisesti

Tämä työtila ei ratkaise näitä kysymyksiä. Se vain tekee ne näkyviksi. Vastaus riippuu valitusta palvelusta ja tilaustasosta, ja se kannattaa tarkistaa palveluntarjoajalta eikä olettaa.

## Rekisteri on henkilötietojen käsittelyä

Päätösrekisteri sisältää hallituksen jäsenten nimet ja heihin liittyviä päätöksiä (valinta, palkkiot, esteellisyys). Se on tietosuoja-asetuksen tarkoittamaa henkilötietojen käsittelyä, ja se kuuluu yhtiön käsittelytoimien selosteeseen. Alla oleva jaottelu on **lähtökohta yhtiön omalle arviolle, ei arvio** (`provisional`, [`05`](05-lainmukaisuus-ja-rajat.md) kohta 6):

| Tietoryhmä | Esimerkki | Tyypillinen peruste | Säilytys |
|---|---|---|---|
| Hallituksen jäsenten ja toimitusjohtajan nimet, roolit, toimikaudet | kokoonpanorekisteri, osallistujat | Lakisääteinen velvoite (OYL 6 luku) ja oikeutettu etu (hallinnon järjestäminen) | Pysyvästi pöytäkirjan osana |
| Jäseniin liittyvät päätökset | valinta, palkkio, esteellisyys, eriävä mielipide | Lakisääteinen velvoite | Pysyvästi pöytäkirjan osana |
| Kutsuttujen asiantuntijoiden nimet | tilintarkastaja, esittelijä | Oikeutettu etu; pelkkä rooli riittää usein | Pysyvästi, jos pöytäkirjassa |
| Kokousten välinen työaineisto | havainnot, ideat, Issuet, kokousluonnos | Oikeutettu etu | Poistetaan tai arkistoidaan, kun asia on käsitelty ja rekisteri päivitetty |
| Pöytäkirjaluonnokset | `LUONNOS-*.docx` | — | Poistetaan, kun allekirjoitettu alkuperäinen on arkistossa; luonnos ei ole asiakirja |

Säilytysaikojen erottelu virallisen pöytäkirjan, luonnoksen ja työaineiston välillä on tarkistettava kohta ([`05`](05-lainmukaisuus-ja-rajat.md), kohta 7).

**Tämä dokumentti ei väitä työtilan olevan tietosuojasäännösten mukainen.** Se kertoo, mitä yhtiön on itse ratkaistava.
