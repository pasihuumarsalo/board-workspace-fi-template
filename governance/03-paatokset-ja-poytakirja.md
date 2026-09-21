# 03 — Päätökset, päätösrekisteri ja pöytäkirja

## Perusperiaate

Rekisteriin kirjataan **asiapäätökset** sanatarkasti, ja jokaisen päätöksen kohdalla näkyy mihin tietoon se perustui, sitooko se yhä, ja onko tämä arvio ihmisen vahvistama.

## Tunnukset

Kaksi juoksevaa sarjaa, molemmat ilman aukkoja ja ilman uudelleenkäyttöä:

- **Kokous:** `PTK-000001`, `PTK-000002`, …
- **Päätös:** `DEC-000001`, `DEC-000002`, …

Etuliitteen voi vaihtaa yhtiön omaksi käyttöönotossa (esim. `ABC-PTK-`). Numero-osan pituus on kuusi merkkiä.

**Pöytäkirjalle numero kirjoitetaan selkokielisenä:** *Kokous numero 73*, ei `PTK-000073` eikä vuosikohtainen `8/2026`. Vuosikohtaiset sarjat katkeavat ja menevät sekaisin — juokseva numero on ainoa, joka on yksikäsitteinen ja jatkuva. Tämä on myös asialuettelon suositus: *pöytäkirjat numeroidaan juoksevasti*.

Jos vanhoja pöytäkirjoja tuodaan ja niissä on oma numerointi, se säilytetään kentässä `legacy.original_minutes_number`. Rekisterin numero ja asiakirjan numero ovat eri asioita.

## Menettelypykälät eivät ole päätöksiä

Kokouksen avaus ja päättäminen, laillisuuden ja päätösvaltaisuuden toteaminen, esityslistan hyväksyminen ja pöytäkirjan tarkastaminen **eivät saa päätöstunnusta**, vaikka pöytäkirjassa alkaisivat sanalla "Päätettiin". Ilman tätä rajausta rekisteri täyttyy merkinnöistä, jotka eivät kerro mitään hallituksen tahdosta.

Rajatapaus: muuttaako pykälä yhtiön asemaa, velvoitteita tai valtuuksia? Puheenjohtajan valinta on päätös. Pöytäkirjantarkastajien valinta ei ole.

## Menettelykehys kirjataan kokouksen ominaisuutena

Se, ettei menettelyä kirjata päätöksenä, ei tarkoita ettei sitä kirjata. Jokainen kokoustietue kantaa:

| Kenttä | Mitä |
|---|---|
| `participants` | Läsnä olleet hallituksen jäsenet |
| `entitled_participants` | Toimikauden jäsenet kokouspäivänä — ne, joilla oli oikeus osallistua |
| `invited_participants` | Asiantuntijat ja esittelijät, jotka eivät ole jäseniä |
| `quorum` | Päätösvaltaisuus, laskettuna |
| `session.opened_at` / `closed_at` | Avaus ja päättäminen, päivä ja kellonaika |
| `place` | Kokouspaikka tai "etäkokous" |
| `signatures` | Allekirjoittajat, kun pöytäkirja on allekirjoitettu |

**Päätösvaltaisuus lasketaan, ei kirjoiteta.** `entitled_count` ja `present_count` johdetaan listoista ja `is_quorate` niistä. Kynnys on osakeyhtiölain 6:3 §:n mukaan yli puolet jäsenistä, ellei yhtiöjärjestys vaadi enemmän. Käsin kirjoitettu "todettiin päätösvaltaiseksi" menee läpi hiljaa silloinkin kun läsnä oli kaksi viidestä; laskettu ei.

Ilman `entitled_participants`-kenttää ei näe, puuttuiko joku kokouksesta vai eikö hän ollut silloin jäsen. Siksi kokoonpanorekisterin on oltava päivämäärärajattu.

## Päätöksen vähimmäistiedot

- Tunnus
- `title` ja `decision_text` — teksti täsmällisenä, ehdot mukaan: rahasummat, määräajat, vastuuhenkilöt. **Puuttuva ehto on rekisterin yleisin vika.**
- `decision_basis` — **mihin tietoon päätös perustui**: mikä aineisto oli käytettävissä, kuka valmisteli, mitä vaihtoehtoja punnittiin. Tämä kenttä on se, joka tekee rekisteristä näytön huolellisuusvelvollisuuden täyttämisestä (OYL 1:8 §) eikä pelkkää luetteloa.
- `conflict_of_interest` — esteellisyys (OYL 6:4 §). **Pakollinen kenttä.** Arvo `none` tarkoittaa nimenomaisesti "todettiin, ettei esteellisyyksiä ollut" — se on eri asia kuin tyhjä, joka tarkoittaa "ei kysytty".
- `vote` — yksimielinen vai äänestys; äänet ja eriävät mielipiteet
- `effect_status` — sitooko yhä: `in_force`, `executed`, `superseded`, `expired`, `undetermined`
- `decision_text_status` ja `interpretation_status`
- `implementation` — vastuuhenkilö ja määräaika, jos päätös edellyttää toimeenpanoa

## Päätös ilman kokousta

OYL 6:3 § sallii päätöksen ilman kokousta, jos kaikki jäsenet siihen suostuvat. Se kirjataan `decision_method: without_meeting`, päivätään, ja allekirjoitetaan tai muuten todennetaan. Ratkaiseva ero kokoukseen: ilman kokousta tehty päätös edellyttää **kaikkien** jäsenten osallistumismahdollisuutta, ei vain päätösvaltaisuutta.

## Pöytäkirjan muodostaminen rekisteristä

Pöytäkirja tuotetaan rekisteristä Word-pohjalle: `python templates/tee-poytakirja.py PTK-000073`. Generaattori muokkaa pohjaa paikoilleen, joten muotoilu ja Wordin automaattinen pykälänumerointi säilyvät — **ulkoasumuutos tehdään Wordiin, ei skriptiin.**

Kaksi sääntöä, jotka generaattori pakottaa: kokousnumero on juokseva numero selkokielisenä, ja **monipäiväisessä kokouksessa avaus- ja päättämispykälä kantavat päiväyksen** (*avattiin 17.9.2026 klo 16:00*), yksipäiväisessä kellonaika riittää. Ehto ratkeaa aikaleimoista.

Generaattori kieltäytyy, jos menettelykehys puuttuu.

## Tarkastus, allekirjoitus, arkisto

1. Pöytäkirjaluonnos tuotetaan rekisteristä. Tila `odottaa_allekirjoitusta`.
2. Puheenjohtaja tarkistaa sanamuodot. Sisältömuutos tehdään rekisteriin ja pöytäkirja tuotetaan uudelleen — ei Word-tiedostoon käsin.
3. Hallituksen jäsenet tarkastavat ja allekirjoittavat, myös poissa olleet, ellei työjärjestys toisin määrää. OYL 6:6 §: pöytäkirjan allekirjoittaa puheenjohtaja ja vähintään yksi hallituksen valitsema jäsen.
4. Allekirjoitettu asiakirja arkistoidaan säilytyspaikkaan. Se on virallinen.
5. Rekisterissä `decision_text_status` → `kopio`, ja asiakirja nimetään `source_documents`-kohdassa **nimellä, ei polulla** — kansiorakenne voi muuttua, nimi pysyy.

## Kun alkuperäinen ja rekisteri eroavat

Alkuperäinen ratkaisee. Rekisteri korjataan, ja korjaus näkyy — ei hiljaa.
