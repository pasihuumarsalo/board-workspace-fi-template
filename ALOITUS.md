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

Tekninen valmistelu, jos Python on käytettävissä (kerro käyttäjälle, tee jos hän pyytää):

```bash
pip install -r requirements.txt
git config core.hooksPath .githooks     # sisältö- ja rakennetarkistus ennen jokaista committia
python scripts/validoi-tyotila.py       # pitää olla puhdas tyhjässä työtilassa
```

---

## 1 · Yhtiö → `company/yhtio.yaml`

Kysy: yhtiön virallinen nimi · Y-tunnus · yhtiömuoto (Oy / Oyj / muu) · kotipaikka · tilikausi (alku–loppu) · toimiala lyhyesti · onko toimitusjohtaja · onko tilintarkastaja.

Kysy myös: **missä allekirjoitetut pöytäkirjat säilytetään** (esim. "SharePoint, Hallitus-kansio" — paikan nimi, ei polkua). Rekisteri viittaa alkuperäisiin nimellä, ja lukijan on tiedettävä mistä ne löytyvät.

---

## 2 · Hallitus → `company/hallituksen-kokoonpano.yaml`

Kysy nykyinen kokoonpano: jokaisesta jäsenestä nimi, rooli (puheenjohtaja / varapuheenjohtaja / jäsen / varajäsen), toimikauden alkupäivä ja valintaperuste (esim. "varsinainen yhtiökokous 12.4.2026"). Toimitusjohtaja erikseen, myös jos hän on jäsen.

**Kysy myös aiemmat kokoonpanot**, jos pöytäkirjoja tuodaan (vaihe 4). Ilman kokoonpanohistoriaa ei voi jälkikäteen todeta, kuka oli oikeutettu osallistumaan menneisiin kokouksiin, eikä päätösvaltaisuutta voi laskea niille. Jos historia ei ole tiedossa, merkitse se avoimeksi — älä täytä nykyisellä kokoonpanolla.

Anna jokaiselle henkilölle `person_id` (`etunimi-sukunimi`, pienin kirjaimin). Se pysyy samana kaudesta toiseen, ja päätösrekisteri viittaa henkilöön vain sillä — nimet tulostuvat asiakirjoihin tästä rekisteristä.

Tarkista kokoonpano kaupparekisteriotetta vasten, jos ote on käsillä.

**Kysy myös menettelysäännöt** (`quorum_rule`, `signature_policy`):
- Onko yhtiöjärjestyksessä lakia tiukempi päätösvaltaisuusvaatimus? Oletus on OYL 6:3 §: yli puolet jäsenistä.
- **Kuka allekirjoittaa pöytäkirjan?** Oletus on lain vähimmäisvaatimus `chair_plus_one` (OYL 6:6 §: puheenjohtaja ja vähintään yksi hallituksen valitsema jäsen; yksijäsenisessä hallituksessa jäsen itse). Yhtiö voi valita kaikkien jäsenten allekirjoituksen — mutta kerro, että allekirjoitus ei tee poissa olleesta osallistujaa, ja että kaikkien tarkastus (`reviewed_by`) on eri asia kuin allekirjoitus.

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
- Jokaisen päätöksen voimassaolo (`effect_status`) on agentin **tulkinta**, ja se merkitään päätöksen omaan `interpretation`-lohkoon (`status: ai_tulkinta`). Kerro käyttäjälle, että tulkinnat vahvistetaan vähitellen, ei kerralla.
- Osallistujat kirjataan `person_id`-tunnuksina. Jos vanhasta pöytäkirjasta ei käy ilmi koollekutsua tai puheenjohtajan sanamuotovahvistusta, jätä `notice` ja `wording_confirmed_by_chair` tyhjiksi — ne tuottavat varoituksen, eivät virhettä, eikä tuodusta pöytäkirjasta muodosteta uutta valmista asiakirjaa (`decision_text_status: kopio` estää sen).
- Aja `python scripts/validoi-tyotila.py` jokaisen tilikausitiedoston jälkeen. Se kertoo aukot numeroinnissa ja ristiriidat kokoonpanon kanssa heti, ei vuosien päästä.
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

Hallituksen valvonta- ja kehitysasiat ovat pohjan `optional_catalog`-listassa (budjetti ja tavoitteet, ennuste ja maksuvalmius, strategian seuranta, riskit, vakuutukset, sisäinen valvonta, lähipiiritapahtumat, toimitusjohtajan tavoitteet ja arviointi, seuraajasuunnittelu, tietoturva ja jatkuvuus, henkilöstön avainriskit, merkittävät investoinnit ja sopimukset, työtilan käyttöoikeuksien tarkistus). **Käy ne läpi yksi kerrallaan ja kysy, otetaanko mukaan.** Mikään niistä ei ole pakollinen. Valittu asia siirretään `items`-listaan kuukauden kanssa ja merkitään `adopted: true`; muut jäävät luetteloon tulevaa varten.

---

## 8 · Pöytäkirjapohja → `templates/poytakirjapohja.docx`

Pohjia on kaksi: `poytakirjapohja.docx` (kokous) ja `paatospohja-ilman-kokousta.docx` (OYL 6:3 §:n päätös ilman kokousta). Pyydä käyttäjää avaamaan ne Wordissa ja korjaamaan **vain** nämä: yhtiön nimi ylätunnisteeseen ja allekirjoituslauseke, jos yhtiö ei käytä sähköistä allekirjoitusta.

**Osallistujien, poissaolijoiden ja allekirjoittajien nimiä ei kirjoiteta pohjaan.** Ne tulevat rekisteristä joka kerta — pohjaan käsin kirjoitettu nimi olisi väärä heti, kun joku on poissa.

Kerro mitä **ei** saa muuttaa: numeroidun listan rakennetta eikä hakasulkeisia paikkamerkkejä (`[ASIA #]`, `[Etunimi Sukunimi]`, `[Poissa]`, `[Allekirjoittaja]`, `[LÄSNÄ]`, `[JÄSENIÄ]`, `[HH:MM]`, `[DD.MM.YYYY]`, `[#]`). Generaattori `templates/tee-poytakirja.py` etsii nämä kohdat sisällön perusteella. Täysi luettelo on `templates/luo-pohja.py`:n alussa.

---

## 9 · Käyttöoikeudet, varmuuskopiot ja arkisto → `company/yhtio.yaml` → `access_and_continuity`

Kysy ja kirjaa — `null` tarkoittaa "ei ratkaistu", ei oletusta:

- **Repo on yksityinen** (tarkista, älä kysy) ja **kaksivaiheinen tunnistautuminen tai passkey vaaditaan** kaikilta.
- **Kenellä on kirjoitusoikeus** — yleensä yhdellä. Jäsenille lukuoikeus riittää.
- **Oikeudet tarkistetaan kokoonpanon muuttuessa**: eronneen jäsenen pääsy repoon *ja tekoälypalveluun* poistetaan samalla kun kokoonpanorekisteri päivitetään.
- **Tekoälypalvelu**: mikä palvelu lukee repoa, onko käsittelijäsopimus (DPA) tarkistettu, onko koulutuskäyttö suljettu pois. Työtila ei ratkaise näitä — se tekee ne näkyviksi ([`governance/07`](governance/07-tietosuoja-ja-luottamuksellisuus.md)).
- **Arkaluonteista aineistoa ei viedä Issueihin**, jos GitHub Issuet ovat käytössä.
- **Varmuuskopiointi ja palautustesti**: GitHub ei ole arkisto. Sovi, miten repo kloonataan yhtiön omaan säilytykseen ja milloin palautus on kokeiltu.
- **Haaran suojaus**: yksityisissä repoissa se vaatii maksullisen GitHub-tason. Jos sitä ei ole, CI-tarkistus on ilmoitus, ei portti — kirjaa `branch_protection` sen mukaan.
- **Allekirjoitettu alkuperäinen säilytetään erillisessä luotettavassa arkistossa** (`minutes_archive`), ei tässä repossa.

---

## 10 · Toistuvat asiat

Kerro, mitä agentti pyytää jatkossa säännöllisesti, ja kirjaa ne vuosikelloon:

- **Yhtiökokouksen pöytäkirja** joka vuosi kokouksen jälkeen → hallitusta koskevat velvoitteet `toimivallan-rajat.yaml`:iin, uusi kokoonpano `hallituksen-kokoonpano.yaml`:iin uutena toimikautena.
- **Yhtiöjärjestyksen muutos** aina kun sellainen tehdään → rajoitteiden päivitys.
- **Hallituksen itsearviointi** ennen jäsenvalintaa.
- **Allekirjoitettujen pöytäkirjojen kuittaus**: kun pöytäkirja on allekirjoitettu, `decision_text_status` vaihtuu `odottaa_allekirjoitusta` → `kopio` ja asiakirja nimetään.

---

## 11 · Lopuksi

Näytä käyttäjälle:

1. Mitä tiedostoja syntyi ja mitä niissä on
2. Mitä jäi avoimeksi (`null`-arvot, `provisional`-tilat, kokoonpanohistorian aukot)
3. `python scripts/validoi-tyotila.py`:n tulos: seuraava vapaa kokous- ja päätöstunnus, varoitukset
4. Ehdotus ensimmäiseksi committiksi

**Älä committaa ilman lupaa.** Käyttöönotto on valmis, kun käyttäjä on nähnyt yhteenvedon ja hyväksynyt sen.
