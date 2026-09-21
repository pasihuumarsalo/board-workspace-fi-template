# 03 — Päätökset, päätösrekisteri ja pöytäkirja

## Perusperiaate

Rekisteriin kirjataan **asiapäätökset** sanatarkasti, ja jokaisen päätöksen kohdalla näkyy mihin tietoon se perustui, kuka osallistui sen käsittelyyn, sitooko se yhä, ja onko tämä arvio ihmisen vahvistama.

Kaikki, mikä voidaan johtaa rekisteristä, johdetaan: päätösvaltaisuus, poissaolijat, seuraava tunnus, allekirjoittajien vähimmäismäärä. Jos sama tieto on kirjoitettu käsin, validointi vertaa sen johdettuun — ristiriita on virhe. Koneellinen skeema: `schema/paatosrekisteri.schema.json`; tarkistus: `python scripts/validoi-tyotila.py`.

## Tunnukset

Kaksi juoksevaa sarjaa, molemmat ilman aukkoja ja ilman uudelleenkäyttöä:

- **Kokous tai päätös ilman kokousta:** `PTK-000001`, `PTK-000002`, …
- **Päätös:** `DEC-000001`, `DEC-000002`, …

Etuliitteen voi vaihtaa yhtiön omaksi käyttöönotossa (`company/yhtio.yaml → id_prefix`, esim. `ABC-PTK-`). Numero-osan pituus on kuusi merkkiä.

**Seuraava vapaa tunnus lasketaan kaikista rekisteritiedostoista**, ei lueta mistään: `python scripts/validoi-tyotila.py` tulostaa sen. Käsin ylläpidetty "seuraava numero"-rivi olisi toinen totuus, joka erkanee ensimmäisestä huomaamatta. Validointi tarkistaa, ettei tunnusta ole käytetty kahdesti, ettei numeroita puutu välistä, että etuliite on yhtiön oma, että numerot kasvavat tiedostojärjestyksessä ja että jokainen `supersedes`- ja `related_constraints`-viittaus osuu olemassa olevaan tietueeseen.

**Asiakirjalle numero kirjoitetaan selkokielisenä:** *Kokous numero 73*, ei `PTK-000073` eikä vuosikohtainen `8/2026`. Vuosikohtaiset sarjat katkeavat ja menevät sekaisin — juokseva numero on ainoa, joka on yksikäsitteinen ja jatkuva. Tämä on myös asialuettelon suositus: *pöytäkirjat numeroidaan juoksevasti*.

Jos vanhoja pöytäkirjoja tuodaan ja niissä on oma numerointi, se säilytetään kentässä `legacy.original_minutes_number`. Rekisterin numero ja asiakirjan numero ovat eri asioita.

## Menettelypykälät eivät ole päätöksiä

Kokouksen avaus ja päättäminen, laillisuuden ja päätösvaltaisuuden toteaminen, esityslistan hyväksyminen ja pöytäkirjan tarkastaminen **eivät saa päätöstunnusta**, vaikka pöytäkirjassa alkaisivat sanalla "Päätettiin". Ilman tätä rajausta rekisteri täyttyy merkinnöistä, jotka eivät kerro mitään hallituksen tahdosta.

Rajatapaus: muuttaako pykälä yhtiön asemaa, velvoitteita tai valtuuksia? Puheenjohtajan valinta on päätös. Pöytäkirjantarkastajien valinta ei ole.

## Menettelykehys kirjataan kokouksen ominaisuutena

Se, ettei menettelyä kirjata päätöksenä, ei tarkoita ettei sitä kirjata. Jokainen kokoustietue kantaa:

| Kenttä | Mitä |
|---|---|
| `roles` | Kokouksen puheenjohtaja, sihteeri ja toimitusjohtajan osallistuminen — roolit **tässä kokouksessa**, jotka voivat poiketa pysyvästä roolista (varapuheenjohtaja johtaa puhetta) |
| `participants` | Läsnä olleet päätösoikeudelliset jäsenet, `person_id`-tunnuksina |
| `deputy_substitutions` | Varajäsen jäsenen sijasta: kuka, kenen sijasta. Vain sijaisena varajäsen saa päätösoikeuden |
| `entitled_participants` | Toimikauden jäsenet kokouspäivänä — ne, joilla oli oikeus osallistua. Validointi vertaa kokoonpanorekisteriin |
| `invited_participants` | Asiantuntijat ja esittelijät, jotka eivät ole jäseniä; nimi tai pelkkä rooli, ja mihin asioihin |
| `notice` | Koollekutsu: milloin, kuka, kenelle (myös varajäsenille estyneiden sijaan), aineiston toimitus, ja **`participation_opportunity_confirmed`** — OYL 6:3 §: päätöstä ei saa tehdä, ellei kaikille jäsenille ole varattu tilaisuutta osallistua |
| `quorum` | Päätösvaltaisuus, laskettuna |
| `session.opened_at` / `closed_at` | Avaus ja päättäminen, päivä ja kellonaika. `null` päätöksessä ilman kokousta |
| `place` | Kokouspaikka tai "etäkokous" |
| `wording_confirmed_by_chair` | Puheenjohtajan vahvistus sanamuodoille — valmis asiakirja edellyttää sitä |
| `signatures` | Allekirjoituspolitiikka, vaaditut allekirjoittajat ja toteutuneet allekirjoitukset |
| `reviewed_by` | Tarkastajat. **Tarkastus ja allekirjoitus ovat eri asioita** |

Poissaolijoita ei kirjoiteta: ne johdetaan (toimikauden jäsenet − läsnä olleet − sijaistetut). Henkilöt viitataan `person_id`-tunnuksella kokoonpanorekisteriin, ja nimi tulostuu asiakirjaan sieltä — pohjaan käsin kirjoitettu nimi ei ole koskaan lähde.

**Päätösvaltaisuus lasketaan, ei kirjoiteta.** `entitled_count` ja `present_count` johdetaan listoista ja `is_quorate` niistä. Kynnys on osakeyhtiölain 6:3 §:n mukaan yli puolet valituista jäsenistä; yhtiöjärjestys voi vain tiukentaa (`company/hallituksen-kokoonpano.yaml → quorum_rule`). Käsin kirjoitettu "todettiin päätösvaltaiseksi" menee läpi hiljaa silloinkin kun läsnä oli kaksi viidestä; laskettu ei. Jos `quorum`-lohko on kirjoitettu rekisteriin, se tarkistetaan laskettua vasten.

## Päätösvaltaisuus on päätöskohtainen

Kokoustason päätösvaltaisuus ei riitä. **Esteellinen jäsen ei osallistu asian käsittelyyn (OYL 6:4 §)**, joten häntä ei lasketa osallistujaksi siinä asiassa — ja esteellisyys voi viedä päätösvaltaisuuden yhdeltä asialta, vaikka kokous muuten olisi päätösvaltainen. Esimerkki: kolmen jäsenen hallituksesta läsnä kaksi, joista yksi esteellinen → asian käsittelyyn osallistuu yksi kolmesta → asiaa ei voida päättää tässä kokouksessa.

Työtila laskee jokaiselle päätökselle: `entitled_count`, `disqualified_person_ids`, `eligible_count`, `participating_person_ids`, `participating_count`, `is_quorate`. Nimittäjänä käytetään valittuja jäseniä (OYL 6:3 §: *määrä lasketaan valituista hallituksen jäsenistä*) — tiukempi lukutapa, jonka oikeudellinen tarkistus on avoin ([`05`](05-lainmukaisuus-ja-rajat.md)). Kentän `decision_quorum` voi kirjoittaa rekisteriin näkyviin; jos se on kirjoitettu, sen on täsmättävä laskettuun.

## Päätöksen vähimmäistiedot

- Tunnus
- `title` ja `decision_text` — teksti täsmällisenä, ehdot mukaan: rahasummat, määräajat, vastuuhenkilöt. **Puuttuva ehto on rekisterin yleisin vika.**
- `decision_basis` — **mihin tietoon päätös perustui**: mikä aineisto oli käytettävissä, kuka valmisteli, mitä vaihtoehtoja punnittiin. Tämä kenttä tekee rekisteristä näytön huolellisuusvelvollisuuden täyttämisestä (OYL 1:8 §) eikä pelkkää luetteloa.
- `conflict_of_interest` — esteellisyys (OYL 6:4 §). **Pakollinen kenttä.** Lyhyt muoto `none` tarkoittaa nimenomaisesti "todettiin, ettei esteellisyyksiä ollut" — eri asia kuin tyhjä, joka tarkoittaa "ei kysytty". Kun esteellisyys oli: `status: declared`, `disqualified_person_ids` (kuka), `left_room` (poistuiko käsittelyn ajaksi), `note` (miksi).
- `vote` — `unanimous: true`, tai äänet `for` / `against` / `abstained`, `chair_casting_vote` (äänten mennessä tasan puheenjohtajan ääni ratkaisee, vaaleissa arpa — OYL 6:3 §), henkilökohtaiset `votes` jos ne kirjattiin, ja `dissenting_opinions` sanatarkasti henkilöineen — OYL 6:6 §: jäsenellä ja toimitusjohtajalla on oikeus saada eriävä mielipiteensä merkityksi.
- `effect_status` — sitooko yhä: `in_force`, `executed`, `superseded`, `expired`, `undetermined`
- `interpretation` — **päätöskohtainen** lohko: `status` (`ai_tulkinta` / `ihmisen_vahvistama`), `confirmed_by`, `confirmed_at`, `note`. `effect_status` on tulkinta, ja sen vahvistus kuuluu päätökselle, ei kokoukselle.
- `implementation` — vastuuhenkilö ja määräaika, jos päätös edellyttää toimeenpanoa
- `proposal` — päätösehdotus; pakollinen päätöksessä ilman kokousta

## Päätös ilman kokousta

OYL 6:3 § sallii päätöksen tekemisen kokousta pitämättä. Lain sanamuodon mukaan edellytys on, että **kaikille jäsenille on mahdollisuuksien mukaan varattu tilaisuus osallistua asian käsittelyyn** — jos jäsen on estynyt, tilaisuus varataan varajäsenelle — ja että päätös **kirjataan, allekirjoitetaan, numeroidaan ja säilytetään kuten kokouksen pöytäkirja**.

Työtilassa se on oma tietue samassa juoksevassa `PTK`-sarjassa:

- `decision_method: without_meeting`, `session: null`, `place: null` — ei avausta eikä päättämistä
- `notice.participation_opportunity_confirmed: true` on **pakollinen**, ja jokaisesta toimikauden jäsenestä on rivi `without_meeting.responses`-listassa, myös vastaamatta jättäneestä (`no_response`)
- `without_meeting`: milloin ehdotus lähetettiin, mihin mennessä kannat pyydettiin, miten päätös todennettiin (sähköinen allekirjoitus, arkistoidut vahvistukset)
- jokaisella päätöksellä on `proposal` (mistä äänestettiin) ja `decision_text` (mitä päätettiin)
- asiakirja muodostetaan omalle pohjalleen `templates/paatospohja-ilman-kokousta.docx`, jossa ei ole avaus- eikä päättämispykäliä

**Korjaus aiempaan:** tämän dokumentin ensimmäinen versio väitti, että päätös ilman kokousta edellyttää kaikkien jäsenten suostumusta. Lain teksti puhuu osallistumismahdollisuudesta, ei yksimielisyydestä. Yhtiöjärjestys tai työjärjestys voi vaatia enemmän. Kohta on `provisional`-tilassa, kunnes yhtiöoikeuteen perehtynyt juristi on tarkistanut sen ([`05`](05-lainmukaisuus-ja-rajat.md)); validointi antaa `INFO`-huomion, jos kaikki jäsenet eivät osallistuneet.

## Pöytäkirjan muodostaminen rekisteristä

Pöytäkirja tuotetaan rekisteristä Word-pohjalle: `python templates/tee-poytakirja.py PTK-000073`. Generaattori muokkaa pohjaa paikoilleen, joten muotoilu ja Wordin automaattinen pykälänumerointi säilyvät — **ulkoasumuutos tehdään Wordiin, ei skriptiin.** Osallistujat, sijaiset, poissaolijat, toimitusjohtaja, sihteeri, kutsutut, esteellisyydet, äänestykset, eriävät mielipiteet ja allekirjoittajat tulevat rekisteristä.

Säännöt, jotka generaattori pakottaa: kokousnumero on juokseva numero selkokielisenä; **monipäiväisessä kokouksessa avaus- ja päättämispykälä kantavat päiväyksen** (*avattiin 17.9.2026 klo 16:00*), yksipäiväisessä kellonaika riittää — ehto ratkeaa aikaleimoista; päätös ilman kokousta menee omalle pohjalleen.

**Validointi on portti, ei parametri.** Ennen asiakirjaa ajetaan sama tarkistus kuin `scripts/validoi-tyotila.py`:ssä.

- **Luonnos** syntyy aina. Sen banneri kertoo estävien virheiden ja varoitusten määrän, ja konsoli luettelee ne.
- **`--valmis`** edellyttää, ettei yhtään `ERROR`-tason löydöstä ole. Se tarkoittaa vähintään: päätösvaltaisuus kokouksessa ja jokaisessa asiassa laskettuna, tunnukset eheät, jokaisella päätöksellä teksti, esteellisyys kirjattu jokaiselle päätökselle, äänestys ja eriävät mielipiteet kelvollisia, puheenjohtaja vahvistanut sanamuodot (`wording_confirmed_by_chair`), allekirjoittajat nimetty politiikan mukaan, koollekutsu ja osallistumismahdollisuus kirjattu, `decision_text_status` on `odottaa_allekirjoitusta` (jos alkuperäinen on jo arkistossa, uutta valmista asiakirjaa ei muodosteta sen rinnalle).
- Jos yksikin estävä tarkistus epäonnistuu, generaattori **kieltäytyy**, tulostaa virheluettelon eikä tuota mitään. Korjaus tehdään rekisteriin, ei asiakirjaan käsin. Agentti ei kierrä porttia: ei muokkaa rekisteriä vain läpäistäkseen tarkistuksen eikä täytä `wording_confirmed_by_chair`- tai `participation_opportunity_confirmed`-kenttiä ilman ihmisen antamaa tietoa.

## Tarkastus, allekirjoitus, arkisto

1. Pöytäkirjaluonnos tuotetaan rekisteristä. Tila `odottaa_allekirjoitusta`.
2. **Puheenjohtaja tarkistaa sanamuodot** → `wording_confirmed_by_chair`. Sisältömuutos tehdään rekisteriin ja pöytäkirja tuotetaan uudelleen — ei Word-tiedostoon käsin.
3. **Tarkastus**: `review_policy` (oletus kaikki toimikauden jäsenet) → `reviewed_by`. Tarkastanut henkilö ei ole allekirjoittaja eikä osallistuja sillä perusteella.
4. **Allekirjoitus**: `signature_policy`. Oletus on lain vähimmäisvaatimus `chair_plus_one` — OYL 6:6 §: kokouksen puheenjohtaja ja, jos hallituksessa on useita jäseniä, vähintään yksi hallituksen siihen valitsema jäsen; yksijäsenisessä hallituksessa jäsen itse. Valittu jäsen kirjataan `signatures.required_signer_person_ids`-listaan. Yhtiö voi valita kaikkien jäsenten allekirjoituksen (`all_members_in_term`) omaksi käytännökseen; silloinkin **poissa olleen allekirjoitus ei tee hänestä osallistujaa**, ja validointi varoittaa siitä.
5. Allekirjoitettu asiakirja arkistoidaan säilytyspaikkaan (`company/yhtio.yaml → minutes_archive`). Se on virallinen.
6. Rekisterissä `decision_text_status` → `kopio`, ja asiakirja nimetään `source_documents`-kohdassa **nimellä, ei polulla** — kansiorakenne voi muuttua, nimi pysyy. Tämän jälkeen valmista asiakirjaa ei muodosteta uudelleen.

## Kun alkuperäinen ja rekisteri eroavat

Alkuperäinen ratkaisee. Rekisteri korjataan, ja korjaus näkyy — ei hiljaa.
