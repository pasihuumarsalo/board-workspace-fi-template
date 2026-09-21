# Hallituksen työtilan arvio ja kehitysohje Claudelle

**Kohde:** `board-workspace-fi-template`  
**Arviointipäivä:** 21.9.2026  
**Tarkoitus:** toimia Clauden kehitystyön lähtöaineistona ennen templaten laajempaa käyttöönottoa tai jakelua.

> Tämä arvio ei ole oikeudellista neuvontaa. Osakeyhtiölakia koskevat muutokset ja tulkinnat on tarkistettava ajantasaisesta laista ja tarvittaessa yhtiöoikeuteen perehtyneeltä juristilta ennen niiden merkitsemistä oikeudellisesti vahvistetuiksi.

---

## 1. Yhteenveto

Työtila soveltuu jo nyt erittäin hyvin hallituksen avustavaksi muistiksi, valmistelijaksi ja päätösrekisteriksi. Se ei ole pelkkä pöytäkirjapohja, vaan harkittu hallinnollinen tietomalli, jossa tekoälyn rooli ja toimivalta on rajattu oikein.

Arvio nykytilasta:

| Osa-alue | Arvio |
|---|---:|
| Hallituksen avustava työtila | 8/10 |
| Päätösten ja historian muistijärjestelmä | 9/10 |
| Kokousten valmistelu | 8/10 |
| Automaattinen pöytäkirjasihteeri | 5/10 |
| Valmius yleisesti jaettavaksi templateksi | 6/10 |

Työtilaa voidaan käyttää ihmisen ohjaamana jo nyt. Sitä ei kuitenkaan tule vielä pitää itsenäisesti luotettavana pöytäkirjan muodostajana tai lainmukaisuuden varmistajana.

Suurin keskeneräisyys ei ole dokumentaation määrässä vaan siinä, että ohjelmalliset tarkistukset eivät vielä pakota noudattamaan dokumentaatiossa määriteltyjä hallinnollisia turvarajoja.

---

## 2. Säilytettävät vahvuudet

Seuraavia periaatteita ei pidä heikentää jatkokehityksessä.

### 2.1 Agentti on avustaja, ei päättäjä

`AGENTS.md` rajaa agentin tehtäväksi valmistelun, jäsentämisen, kirjaamisen ja muistuttamisen. Agentti ei:

- tee hallituksen päätöksiä;
- merkitse päätöstä hyväksytyksi ilman ihmisen vahvistusta;
- arvaa puuttuvia tietoja;
- toimi lakimiehenä;
- muuta luonnosta allekirjoitetuksi asiakirjaksi omalla päätöksellään.

Tämä on työtilan tärkein turvallisuusperiaate.

### 2.2 Rekisterikopio ja alkuperäinen asiakirja erotetaan

Allekirjoitettu pöytäkirja on auktoritatiivinen alkuperäinen. Päätösrekisteri on sitä täydentävä rakenteinen kopio. Ristiriidassa alkuperäinen ratkaisee.

### 2.3 Kopio ja tulkinta erotetaan

`decision_text_status` ja `interpretation_status` erottavat:

- alkuperäisestä asiakirjasta kopioidun päätöstekstin;
- agentin tekemän arvion päätöksen voimassaolosta, suhteista ja seurauksista.

Vahvistamatonta tekoälytulkintaa ei saa esittää faktana.

### 2.4 Kokoonpanohistoria on aikarajattu

`company/hallituksen-kokoonpano.yaml` säilyttää toimikaudet ja jäsenkohtaiset voimassaoloajat. Tämä mahdollistaa menneiden kokousten osallistumisoikeuden ja päätösvaltaisuuden jälkikäteisen arvioinnin.

### 2.5 Päätösten perusteet kirjataan

`decision_basis` on keskeinen kenttä. Sen tarkoituksena on osoittaa:

- mitä tietoa hallituksella oli;
- kuka asian valmisteli;
- mitä vaihtoehtoja tarkasteltiin;
- mihin päätös perustui.

### 2.6 Menettelymerkintöjä ei sekoiteta asiapäätöksiin

Kokouksen avaus, päätösvaltaisuuden toteaminen, esityslistan hyväksyminen ja pöytäkirjan tarkastaminen eivät saa varsinaista päätöstunnusta. Menettelykehys on silti tallennettava kokoustietueeseen ja pöytäkirjaan.

---

## 3. Kriittiset korjaustarpeet

### P0-1: Estä virheellisen asiakirjan tuottaminen valmiina pöytäkirjana

Nykyinen `templates/tee-poytakirja.py` voi poistaa luonnosbannerin parametrilla `--valmis`, vaikka kokouksen tiedot olisivat puutteellisia tai menettely virheellinen.

Ennen valmiin asiakirjan muodostamista on tarkistettava vähintään:

- `quorum.is_quorate == true`;
- päätösvaltaisuus on laskettu eikä vain kirjoitettu;
- kaikki päätöstunnukset ovat yksikäsitteisiä;
- kokous- ja päätösnumerointi on eheä;
- jokaisella päätöksellä on päätösteksti;
- esteellisyys on käsitelty päätöskohtaisesti;
- äänestys ja mahdolliset eriävät mielipiteet on kirjattu;
- päätöstekstin tila sallii asiakirjan muodostamisen;
- puheenjohtaja on vahvistanut sanamuodot;
- vaaditut allekirjoittajat on määritelty;
- osallistujat ja kokousroolit ovat rekisterissä;
- kutsumis- ja osallistumismahdollisuuden tiedot ovat riittävät.

Jos yksikin estävä tarkistus epäonnistuu, generaattorin on:

1. kieltäydyttävä tuottamasta valmista asiakirjaa;
2. näytettävä selkeä virheluettelo;
3. sallittava enintään selvästi merkitty luonnos.

`--valmis` ei saa tarkoittaa vain bannerin poistamista.

### P0-2: Muodosta osallistujat ja menettelytiedot rekisteristä

Word-pohjaan käsin tallennettuja osallistujanimiä ei saa käyttää lopullisen pöytäkirjan lähteenä. Generaattorin on tuotava rekisteristä:

- kokouksen puheenjohtaja;
- läsnä olleet varsinaiset jäsenet;
- jäsenen sijaan osallistunut varajäsen;
- poissa olleet jäsenet tarvittaessa;
- toimitusjohtaja;
- sihteeri;
- kutsutut asiantuntijat;
- esteellisyydet ja poistuminen käsittelyn ajaksi;
- äänestystulokset;
- eriävät mielipiteet;
- pöytäkirjan allekirjoittajat.

Osallistujat tulee viitata `person_id`-tunnuksilla, ei vain vapaamuotoisina `display_name`-merkkijonoina.

### P0-3: Tee päätösvaltaisuudesta päätöskohtainen

Kokoustason päätösvaltaisuus ei riitä, koska esteellinen jäsen ei osallistu kyseisen asian käsittelyyn ja esteellisyys voi vaikuttaa päätösvaltaisuuteen.

Jokaiselle päätökselle tarvitaan esimerkiksi:

```yaml
decision_quorum:
  entitled_count: 3
  disqualified_person_ids: []
  eligible_count: 3
  participating_person_ids: []
  participating_count: 3
  is_quorate: true
  basis: "OYL 6:3 §"
  derived: true
```

Kokoustason `quorum` voidaan säilyttää yleisenä menettelytietona, mutta se ei korvaa päätöskohtaista tarkistusta.

### P0-4: Toteuta päätös ilman kokousta omana prosessinaan

Tietomalli sallii arvon `decision_method: without_meeting`, mutta nykyinen generaattori vaatii kokouksen avaus- ja päättämisajat ja muodostaa kokousmuotoisen pöytäkirjan.

Päätös ilman kokousta tarvitsee oman rakenteen ja asiakirjapohjan:

- päätöspäivä;
- asian käsittelyyn kutsutut jäsenet;
- tieto osallistumismahdollisuuden varaamisesta;
- osallistuneet jäsenet;
- päätösehdotus;
- jäsenten kannat tai äänet;
- päätösvaltaisuus;
- esteellisyydet;
- päätösteksti;
- allekirjoitukset tai muu hyväksytty todentaminen;
- ei kokouksen avaus- tai päättämispykäliä.

Dokumentaation väite kaikkien jäsenten suostumuksen välttämättömyydestä on tarkistettava. OYL 6:3 §:n sanamuoto käsittelee osallistumismahdollisuutta sekä päätöksen kirjaamista, allekirjoittamista, numerointia ja säilyttämistä. Yksimielisyyttä ei tule merkitä yleiseksi lakisääteiseksi edellytykseksi ilman oikeudellista vahvistusta.

Ajantasainen lähde: https://www.finlex.fi/fi/lainsaadanto/2006/624

### P0-5: Korjaa allekirjoitusmallin oletus

Nykyinen oletus:

```yaml
required_signers: all_members_in_term
includes_absent_members: true
```

ei sovi yleiseksi template-oletukseksi.

Turvallisempi malli:

- oletus `chair_plus_one`, kun hallituksessa on useita jäseniä;
- yksijäsenisessä hallituksessa kyseinen jäsen;
- allekirjoittajan on oltava erotettavissa osallistujasta ja tarkastajasta;
- poissa ollutta ei merkitä kokoukseen osallistuneeksi allekirjoituksen perusteella;
- mahdollinen kaikkien jäsenten tarkastus kirjataan erilliseen `reviewed_by`-kenttään;
- yritys voi valita kaikkien allekirjoituksen omaksi käytännökseen.

---

## 4. Tietomallin korjaukset

### P1-1: Siirrä tulkinnan vahvistaminen päätöskohtaiseksi

Dokumentaatio puhuu jokaisen päätöksen `interpretation_status`-tilasta, mutta mallissa tila on kokoustasolla.

Lisää jokaiselle päätökselle:

```yaml
interpretation:
  status: ai_tulkinta
  confirmed_by: null
  confirmed_at: null
  note: null
```

Myös `effect_status` ja sen vahvistaminen ovat päätöskohtaisia.

### P1-2: Lisää kokouksen koollekutsumisen todentaminen

Lisää kokoustietueeseen vähintään:

```yaml
notice:
  sent_at: null
  sent_by: null
  channel: null
  invited_person_ids: []
  deputy_invited_for: []
  materials_sent_at: null
  participation_opportunity_confirmed: null
```

Tämä tukee sen osoittamista, että jäsenille ja tarvittaessa varajäsenille varattiin mahdollisuus osallistua asian käsittelyyn.

### P1-3: Poista manuaalinen seuraavan tunnuksen ylläpito

`decisions/README.md`:n käsin päivitettävät “Seuraava kokous” ja “Seuraava päätös” eivät saa olla auktoritatiivinen lähde.

Seuraava tunnus lasketaan kaikista rekisteritiedostoista. Validoinnin on tarkistettava:

- päällekkäiset tunnukset;
- puuttuvat numerot;
- virheellinen etuliite;
- virheellisesti pienenevä numero;
- viittaus olemattomaan päätökseen tai rajoitteeseen.

### P1-4: Lue päätöshistoria kokonaisuutena

`AGENTS.md` ei saa ohjata laskemaan voimassa olevien päätösten määrää vain uusimmasta tilikausitiedostosta.

Agentin on tarvittaessa luettava kaikki päätösrekisterit tai koneellisesti muodostettu indeksi, koska aiempien tilikausien päätökset voivat edelleen olla voimassa.

### P1-5: Määritä kokouskohtaiset roolit

Pelkkä osallistujan nimi ei riitä. Kokoustietueen tulee erottaa ainakin:

- `meeting_chair_person_id`;
- `secretary_person_id`;
- `member_participant_ids`;
- `deputy_substitutions`;
- `ceo_participation`;
- `invited_participants`.

Rooli kokouksessa ei aina ole sama kuin henkilön pysyvä rooli kokoonpanorekisterissä.

---

## 5. Validointi, testit ja tekninen toteutus

### P1-6: Lisää koneellinen skeema

Luo YAML-rakenteille JSON Schema tai vastaava koneellisesti validoitava skeema. Skeeman on tarkistettava ainakin:

- pakolliset kentät;
- enum-arvot;
- tunnusten muodot;
- päivämäärät;
- `null`-arvojen sallittavuus;
- henkilö- ja päätösviitteet;
- päätösmenetelmästä riippuvat ehdot;
- päätöstilan ja asiakirjatilan yhteensopivuus.

### P1-7: Lisää koko työtilan validaattori

Luo yksi komento, esimerkiksi:

```bash
python scripts/validoi-tyotila.py
```

Sen tulee tarkistaa rakenteen lisäksi liiketoimintasäännöt ja palauttaa ei-nolla-arvo, jos estävä virhe löytyy.

Tulokset ryhmitellään:

- **ERROR:** estää valmiin pöytäkirjan;
- **WARNING:** vaatii ihmisen tarkistuksen;
- **INFO:** huomio tai suositus.

### P1-8: Lisää automaattiset testit

Testaa vähintään:

1. tavallinen päätösvaltainen kokous;
2. kokous ilman päätöksiä;
3. monipäiväinen kokous;
4. yksijäseninen hallitus;
5. varajäsen varsinaisen jäsenen sijalla;
6. päätöskohtainen esteellisyys;
7. esteellisyyden vuoksi päätösvallaton asia;
8. äänestys ja eriävä mielipide;
9. päätös ilman kokousta;
10. puuttuva allekirjoittaja;
11. päällekkäinen päätöstunnus;
12. ristiriitainen kokoonpanohistoria;
13. valmiin asiakirjan muodostamisen estäminen;
14. vanhan päätöksen korvaaminen;
15. katkennut tai virheellinen viittaus.

### P1-9: Ilmoita Python-riippuvuudet

README mainitsee `python-docx`-kirjaston, mutta generaattori käyttää myös `PyYAML`ia.

Lisää esimerkiksi `requirements.txt`:

```text
python-docx
PyYAML
```

Versiot voidaan lukita myöhemmin, mutta kaikki välttämättömät riippuvuudet on ilmoitettava.

---

## 6. Tietosuoja ja tietoturva

### P1-10: Laajenna henkilötunnusten tunnistus

Nykyinen tarkistus tunnistaa vain välimerkit `+`, `-` ja `A`. Päivitä tunnistus kattamaan Suomessa käytössä olevat vuosisatamerkit ja tarkista mahdollisuuksien mukaan myös tarkistusmerkki.

Tarkistuksen pitää kattaa myös:

- Word-tiedostojen tekstisisältö;
- mahdolliset tekstipohjaiset liitteet;
- YAML-kommentit;
- commitissa lisätyt tiedostot.

Tarkistus ei saa väittää repoa puhtaaksi, jos binaaritiedostoja ei ole tarkistettu. Sen tulee ilmoittaa erikseen, mitkä tiedostot jäivät tarkastuksen ulkopuolelle.

### P1-11: Automatisoi tarkistukset

Sisältö- ja rakennetarkistukset pitää voida ajaa:

- paikallisesti ennen committia;
- CI-ajossa pull requestille;
- ennen pöytäkirjan muodostamista.

Jos GitHubin nykyinen palvelutaso ei mahdollista vaadittua branch protectionia tai rulesettejä, tämä on dokumentoitava käyttöönotossa.

### P1-12: Täsmennä käyttöoikeusmalli

Yhtiökohtaisen työtilan ohjeeseen lisätään:

- repo on aina yksityinen;
- 2FA tai passkey vaaditaan;
- kirjoitusoikeus vain sitä tarvitseville;
- oikeudet tarkistetaan jäsenmuutoksen yhteydessä;
- entisen jäsenen oikeus poistetaan hallitusti;
- tekoälypalvelun käyttöoikeus poistetaan samalla;
- arkaluonteista aineistoa ei viedä Issueihin;
- varmuuskopiointi ja palautustesti määritellään;
- allekirjoitettu alkuperäinen säilytetään erillisessä luotettavassa arkistossa.

---

## 7. Vuosikellon laajentaminen

Lakisääteinen runko säilytetään. Käyttöönotossa agentin tulee lisäksi kysyä, halutaanko vuosikelloon seuraavat hallituksen valvonta- ja kehitysasiat:

- budjetti ja tavoitteet;
- ennuste, kassavirta ja maksuvalmius;
- strategian seuranta;
- riskit ja mahdollisuudet;
- vakuutukset;
- sisäinen valvonta;
- lähipiiritapahtumat;
- toimitusjohtajan tavoitteet ja arviointi;
- seuraajasuunnittelu;
- tietoturva ja jatkuvuus;
- henkilöstön avainriskit;
- merkittävät investoinnit ja sopimukset;
- hallituksen itsearviointi.

Näitä ei aseteta automaattisesti pakollisiksi. Agentti tarjoaa ne yhtiökohtaisesti valittaviksi.

---

## 8. Oikeudellisesti tarkistettavat väitteet

Tarkista vähintään seuraavat kohdat ennen laajaa julkaisua:

1. Päätös ilman kokousta ja väitetty yksimielisyysvaatimus.
2. Väite siitä, että OYL 6:6 § nimenomaisesti edellyttäisi kaikkien osallistujien yksilöintiä.
3. Poissa olleiden jäsenten allekirjoittamista koskeva suositus.
4. Hallituksen ja yhtiökokouksen toimivallan poikkeukset erityistilanteissa.
5. Varojenjakoa, sulautumista ja jakautumista koskevien yleislausumien tarkkuus.
6. Tietosuojan käsittelyperusteiden kuvaus eri tietoryhmille.
7. Säilytysaikojen erottelu virallisten pöytäkirjojen, luonnosten ja kokousten välisen työaineiston välillä.

Oikeudellisesti epävarma kohta merkitään `provisional`-tilaan, kunnes se on tarkistettu.

---

## 9. Hyväksymiskriteerit seuraavalle versiolle

Seuraava versio voidaan katsoa valmiiksi hallituksen avustavan sihteerin templateksi, kun:

- [ ] päätös ilman kokousta toimii rakenteessa ja asiakirjatuotannossa;
- [ ] päätöskohtainen esteellisyys ja päätösvaltaisuus lasketaan;
- [ ] osallistujat ja roolit tulevat rekisteristä;
- [ ] äänestykset ja eriävät mielipiteet tulevat pöytäkirjaan;
- [ ] `--valmis` edellyttää hyväksyttyä validointia;
- [ ] allekirjoitusmalli ei sekoita osallistumista ja tarkastamista;
- [ ] tunnukset lasketaan ja validoidaan koneellisesti;
- [ ] kaikki päätösrekisterit huomioidaan voimassaolokyselyissä;
- [ ] YAML-rakenteilla on skeema;
- [ ] keskeiset prosessit on testattu automaattisesti;
- [ ] riippuvuudet on dokumentoitu;
- [ ] henkilötunnustarkistus kattaa nykyiset muodot ja Word-tiedostot;
- [ ] käyttöoikeus-, varmuuskopiointi- ja arkistointiohje on dokumentoitu;
- [ ] oikeudelliset väitteet on tarkistettu.

---

## 10. Ohje Claudelle ennen toteutusta

1. Muodosta ensin kokonaiskuva kaikista yllä mainituista riippuvuuksista.
2. Vertaa muutoksia `AGENTS.md`:n, governance-dokumenttien, YAML-mallien, Word-pohjan ja Python-skriptien välillä.
3. Älä muuta vain yhtä kerrosta: dokumentaatio, tietomalli, validointi, generaattori ja testit on pidettävä keskenään yhdenmukaisina.
4. Erottele oikeudellinen tarkistus teknisestä toteutuksesta.
5. Esitä toteutussuunnitelma ja tiedostokohtaiset muutokset ennen rakentamista.
6. Pyydä hyväksyntä ennen muutosten toteuttamista.
7. Toteuta muutokset pieninä, testattavina kokonaisuuksina.
8. Varmista lopuksi, ettei agentti voi ohittaa hyväksyntärajoja pelkällä komentoriviparametrilla.
9. Raportoi tehdyt muutokset, testitulokset ja jäljelle jääneet avoimet kysymykset.

## Lopputulos

Työtilan ydinajatus ja tietomalli ovat vahvoja ja ammattimaisia. Se on jo käyttökelpoinen ihmisen ohjaamana hallituksen muistina ja valmisteluapulaisena.

Seuraavan kehitysvaiheen tavoite ei ole ensisijaisesti lisätä sisältöä, vaan muuttaa nykyiset kirjalliset turvarajat koneellisesti valvotuiksi säännöiksi. Kun tämä tehdään, työtila voi toimia erittäin vahvana suomalaisen listaamattoman osakeyhtiön hallituksen avustavana sihteerinä.
