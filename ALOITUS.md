# Käyttöönotto

Tämä on keskustelu, jonka agentti käy käyttäjän kanssa, kun työtila otetaan käyttöön ensimmäisen kerran. Agentti kysyy vaihe kerrallaan, kirjoittaa vastaukset oikeisiin tiedostoihin ja näyttää lopuksi mitä syntyi ja mitä jäi avoimeksi.

**Agentille:** kysy yksi vaihe kerrallaan, älä kaikkea yhdellä listalla. Kirjoita tiedostot heti kun vaihe on vastattu, jotta keskeytynyt käyttöönotto ei hukkaa mitään. Puuttuva tieto merkitään `null`-arvoksi ja kirjataan avoimeksi — ei arvata, ei jätetä placeholderia paikoilleen.

---

## 0 · Ennen kuin kysyt mitään

Kerro käyttäjälle nämä kolme asiaa:

1. **Repon on oltava yksityinen.** Tarkista se ensin. Hallituksen aineisto ei kuulu julkiseksi.
2. **Henkilötunnuksia ei kirjata koskaan**, ei myöskään pöytäkirjoista tuotaessa. Nimi ja kaupparekisteri riittävät yksilöintiin.
3. **Sopimuksista ei kopioida sisältöä.** Yhtiöjärjestyksestä, osakassopimuksesta ja johtajasopimuksista poimitaan vain ne kohdat, jotka rajoittavat tai velvoittavat hallitusta.

Ja mitä kannattaa olla käsillä: yhtiöjärjestys, kaupparekisteriote, aiemmat hallituksen pöytäkirjat jos ne tuodaan, ja osakassopimus jos sellainen on.

---

## 1 · Yhtiö → `company/yhtio.yaml`

Kysy: yhtiön virallinen nimi · Y-tunnus · yhtiömuoto (Oy / Oyj / muu) · kotipaikka · tilikausi (alku–loppu) · toimiala lyhyesti · onko toimitusjohtaja · onko tilintarkastaja.

Kysy myös: **missä allekirjoitetut pöytäkirjat säilytetään** (esim. "SharePoint, Hallitus-kansio" — paikan nimi, ei polkua). Rekisteri viittaa alkuperäisiin nimellä, ja lukijan on tiedettävä mistä ne löytyvät.

---

## 2 · Hallitus → `company/hallituksen-kokoonpano.yaml`

Kysy nykyinen kokoonpano: jokaisesta jäsenestä nimi, rooli (puheenjohtaja / varapuheenjohtaja / jäsen / varajäsen), toimikauden alkupäivä ja valintaperuste (esim. "varsinainen yhtiökokous 12.4.2026"). Toimitusjohtaja erikseen, myös jos hän on jäsen.

**Kysy myös aiemmat kokoonpanot**, jos pöytäkirjoja tuodaan (vaihe 4). Ilman kokoonpanohistoriaa ei voi jälkikäteen todeta, kuka oli oikeutettu osallistumaan menneisiin kokouksiin, eikä päätösvaltaisuutta voi laskea niille. Jos historia ei ole tiedossa, merkitse se avoimeksi — älä täytä nykyisellä kokoonpanolla.

Tarkista kokoonpano kaupparekisteriotetta vasten, jos ote on käsillä.

---

## 3 · Toimivallan rajat → `company/toimivallan-rajat.yaml`

Käy läpi **yhtiöjärjestys** ja poimi hallitusta koskevat kohdat: jäsenmäärä, toimikausi, päätösvaltaisuus jos poikkeaa laista, edustamisoikeus, määräenemmistöä vaativat asiat, lunastus- ja suostumuslausekkeet.

Jos on **osakassopimus**, kysy onko siinä hallitusta koskevia kohtia — esimerkiksi asioita, jotka vaativat osakkaiden suostumuksen, tai nimitysoikeuksia. Kirjaa **vain velvoite ja sen lähdekohta**, ei sopimustekstiä eikä kaupallisia ehtoja.

Jos on **toimitusjohtajasopimus**, ainoa tänne kuuluva asia on se, mitä hallitus on siinä sitoutunut tekemään (esim. vuosittainen arviointi). Palkkiot eivät kuulu tänne.

Jokainen rajoite saa tunnuksen ja lähdeviitteen. Merkitse tila `provisional`, kunnes puheenjohtaja on tarkistanut listan.

---

## 4 · Historia → `decisions/`

Kysy: **tuodaanko aiemmat pöytäkirjat**, ja jos, kuinka pitkältä ajalta?

**Jos tuodaan:**
- Yksi tiedosto per tilikausi (`decisions/2024.yaml` jne.).
- Pöytäkirjat numeroidaan juoksevasti ensimmäisestä alkaen. Jos alkuperäisissä on oma numerointi, se kirjataan `legacy.original_minutes_number`-kenttään — rekisterin juokseva numero ja asiakirjan oma numero ovat eri asioita, ja molemmat säilytetään.
- Päätösteksti kopioidaan sanatarkasti. `decision_text_status: kopio`, tai `kopio_kuvasta` jos lähde on skannattu.
- Jokaisen päätöksen voimassaolo (`effect_status`) on agentin **tulkinta**, ja se merkitään `interpretation_status: ai_tulkinta`. Kerro käyttäjälle, että tulkinnat vahvistetaan vähitellen, ei kerralla.
- Menettelypykälistä ei tehdä päätöksiä (ks. `governance/03`).
- Henkilötunnukset ja sopimussisällöt jätetään pois ja poisto merkitään `redaction_applied`-kenttään.
- Jos jotain ei saa selville, kirjaa se `notable_findings`- tai `open_items`-osioon. Kokous ilman päätöksiä on tieto, ei puute.

**Jos ei tuoda:** rekisteri alkaa tyhjänä ja numerointi ensimmäisestä uudesta kokouksesta. Kirjaa `decisions/README.md`:hen, että aiemmat pöytäkirjat ovat olemassa säilytyspaikassa mutta eivät rekisterissä.

---

## 5 · Työjärjestys → `governance/06-tyojarjestys.md`

Kysy: **onko hallituksella kirjallinen työjärjestys?**

Jos on, tuo sen olennainen sisältö: työnjako, kokoontumistiheys, koollekutsuminen, varajäsenten rooli, aineiston toimitusaika. Jos ei ole, kerro että `governance/06` sisältää rungon, jonka hallitus voi hyväksyä sellaisenaan tai muokata — ja että kirjallinen työjärjestys on Keskuskauppakamarin asialuettelon suositus, ei lain vaatimus.

---

## 6 · Kokousrytmi

Kysy: montako kokousta vuodessa on tarkoitus pitää · pidetäänkö strategiapäivää · kokoontuuko hallitus paikan päällä, etänä vai molempia · kuka kutsuu koolle ja miten · kuinka monta päivää ennen aineisto toimitetaan.

Kirjaa vastaukset työjärjestykseen (vaihe 5) ja vuosikelloon (vaihe 7).

---

## 7 · Vuosikello → `annual-cycle/vuosikello.yaml`

Kysy: **tuodaanko olemassa oleva vuosikello, luodaanko se lakisääteisistä asioista, vai jätetäänkö myöhemmäksi?**

Lakisääteinen runko on pohjassa valmiina: tilinpäätöksen käsittely ja allekirjoitus, varsinaisen yhtiökokouksen valmistelu (OYL 5:3 §: kuuden kuukauden kuluessa tilikauden päättymisestä), hallituksen järjestäytyminen yhtiökokouksen jälkeen. Lisäksi pohjassa on kaksi suositusta asialuettelosta: **hallituksen itsearviointi ennen jäsenvalintaa** ja **yhtiökokouspöytäkirjan läpikäynti** hallitusta koskevien velvoitteiden poimimiseksi.

Muut asiat (budjetti, strategia, riskit, henkilöstö, vakuutukset) lisätään käyttäjän vastausten mukaan.

---

## 8 · Pöytäkirjapohja → `templates/poytakirjapohja.docx`

Pyydä käyttäjää avaamaan pohja Wordissa ja korjaamaan **vain** nämä: yhtiön nimi ylätunnisteeseen, kokouspaikan oletus, osallistujalohko (nimet ja roolit) ja allekirjoituslauseke, jos yhtiö ei käytä sähköistä allekirjoitusta.

Kerro mitä **ei** saa muuttaa: numeroidun listan rakennetta, `[ASIA #]`-merkintöjä eikä kellonaika- ja päiväysmerkintöjä `[HH:MM]` ja `[DD.MM.YYYY]`. Generaattori `templates/tee-poytakirja.py` etsii nämä kohdat sisällön perusteella.

---

## 9 · Toistuvat asiat

Kerro, mitä agentti pyytää jatkossa säännöllisesti, ja kirjaa ne vuosikelloon:

- **Yhtiökokouksen pöytäkirja** joka vuosi kokouksen jälkeen → hallitusta koskevat velvoitteet `toimivallan-rajat.yaml`:iin, uusi kokoonpano `hallituksen-kokoonpano.yaml`:iin uutena toimikautena.
- **Yhtiöjärjestyksen muutos** aina kun sellainen tehdään → rajoitteiden päivitys.
- **Hallituksen itsearviointi** ennen jäsenvalintaa.
- **Allekirjoitettujen pöytäkirjojen kuittaus**: kun pöytäkirja on allekirjoitettu, `decision_text_status` vaihtuu `odottaa_allekirjoitusta` → `kopio` ja asiakirja nimetään.

---

## 10 · Lopuksi

Näytä käyttäjälle:

1. Mitä tiedostoja syntyi ja mitä niissä on
2. Mitä jäi avoimeksi (`null`-arvot, `provisional`-tilat, kokoonpanohistorian aukot)
3. Seuraava vapaa kokous- ja päätöstunnus
4. Ehdotus ensimmäiseksi committiksi

**Älä committaa ilman lupaa.** Käyttöönotto on valmis, kun käyttäjä on nähnyt yhteenvedon ja hyväksynyt sen.
