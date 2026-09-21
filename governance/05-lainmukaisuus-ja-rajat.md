# 05 — Lainmukaisuus ja hyväksyntärajat

**Tämä ei ole oikeudellista neuvontaa.** Se on luettelo niistä osakeyhtiölain kohdista, joihin työtilan käytännöt nojaavat, ja normihierarkia jota agentti soveltaa. Epäselvässä tilanteessa kysytään asiantuntijalta. Kohdat, joita yhtiöoikeuteen perehtynyt juristi ei ole tarkistanut, on merkitty `provisional`-tilaan alla — ne ovat työtilan tekijän lukutapa laista, eivät vahvistettua tulkintaa.

## Osakeyhtiölain (624/2006) kohdat, joihin työtila nojaa

| Kohta | Mitä | Miten näkyy työtilassa |
|---|---|---|
| **1:8 §** Johdon tehtävä | Huolellisuus ja yhtiön edun edistäminen | `decision_basis`-kenttä: mihin tietoon päätös perustui |
| **6:2 §** Hallituksen yleiset tehtävät | Hallinto ja toiminnan asianmukainen järjestäminen; kirjanpidon ja varainhoidon valvonta | Vuosikellon lakisääteiset asiat |
| **6:3 §** Päätöksenteko | Päätösvaltainen, kun yli puolet valituista jäsenistä on paikalla, ellei yhtiöjärjestys vaadi enemmän; enemmistön kanta, tasan puheenjohtajan ääni (vaaleissa arpa); päätöstä ei saa tehdä ellei kaikille jäsenille ole varattu tilaisuutta osallistua, estyneen sijaan varajäsenelle; päätös ilman kokousta kirjataan, allekirjoitetaan, numeroidaan ja säilytetään kuten pöytäkirja | `quorum` ja `decision_quorum` lasketaan; `quorum_rule`; `notice.participation_opportunity_confirmed`; `chair_casting_vote`; `decision_method: without_meeting` omalle pohjalleen samassa numerosarjassa |
| **6:4 §** Esteellisyys | Jäsen ei saa osallistua hänen ja yhtiön välistä sopimusta koskevan asian käsittelyyn, eikä yhtiön ja kolmannen välistä asiaa, jos hänellä on siitä odotettavissa olennaista etua joka voi olla ristiriidassa yhtiön edun kanssa | `conflict_of_interest` pakollinen; esteellinen ei osallistu → päätöskohtainen päätösvaltaisuus |
| **6:5 §** Koolle kutsuminen | Puheenjohtaja vastaa kokoontumisesta; jäsen tai toimitusjohtaja voi vaatia koolle kutsumista | Työjärjestys; `notice` |
| **6:6 §** Pöytäkirja | Pöytäkirja laaditaan; allekirjoittaa kokouksen puheenjohtaja ja, jos jäseniä on useita, vähintään yksi hallituksen valitsema jäsen; jäsenellä ja toimitusjohtajalla oikeus saada eriävä mielipide merkityksi; pöytäkirjat numeroidaan juoksevasti ja säilytetään luotettavasti | `signature_policy: chair_plus_one` oletus; `dissenting_opinions`; juokseva `PTK`-sarja; `minutes_archive` |
| **5:3 §** Varsinainen yhtiökokous | Kuuden kuukauden kuluessa tilikauden päättymisestä | Vuosikello |
| **13 luku** Varojen jakaminen | Vain laissa säädetyillä tavoilla; maksukykyisyys | Toimivallan rajat; voitonjakoesitykset |

## Oikeudellisesti tarkistettavat kohdat

Kehitysarvio 21.9.2026 nimesi seitsemän väitettä, jotka on tarkistettava ennen laajaa julkaisua. Kaikki ovat tilassa **`provisional`**. Taulukko kertoo, minkä lukutavan työtila tällä hetkellä soveltaa — ei sitä, että se olisi oikea.

| # | Kohta | Työtilan nykyinen lukutapa | Tila |
|---|---|---|---|
| 1 | Päätös ilman kokousta ja yksimielisyys | Laki edellyttää osallistumismahdollisuuden varaamista kaikille, ei yksimielisyyttä. Aiempi väite yksimielisyysvaatimuksesta poistettu. Yhtiöjärjestys tai työjärjestys voi vaatia enemmän → `INFO`-huomio, jos kaikki eivät osallistuneet | `provisional` |
| 2 | Edellyttääkö OYL 6:6 § kaikkien osallistujien yksilöintiä | Ei sanamuodon mukaan — pykälä koskee allekirjoituksia, eriävää mielipidettä, numerointia ja säilytystä. Osallistujat nimetään, koska päätösvaltaisuus ja esteellisyys on voitava todentaa jälkikäteen (1:8 §, 6:3 §, 6:4 §) ja koska se on asialuettelon suositus. Aiempi väite korjattu `AGENTS.md`:ssä ja `07`:ssä | `provisional` |
| 3 | Poissa olleiden allekirjoitus | Ei lain vaatimus. Oletus `chair_plus_one`; kaikkien allekirjoitus on yhtiön valinta, eikä se tee poissa olleesta osallistujaa | `provisional` |
| 4 | Hallituksen ja yhtiökokouksen toimivallan poikkeukset | Alla oleva luettelo on yleissääntö; poikkeukset (esim. yhtiökokouksen valtuutukset, yhtiöjärjestyksen määräykset, konsernitilanteet) kirjataan `toimivallan-rajat.yaml`:iin tapauskohtaisesti | `provisional` |
| 5 | Varojenjaon, sulautumisen ja jakautumisen yleislausumat | Työtila viittaa 13 lukuun ja 16–17 lukuihin vain toimivallan tasolla, ei menettelyinä | `provisional` |
| 6 | Tietosuojan käsittelyperusteet tietoryhmittäin | `07`:n taulukko on lähtökohta, ei arvio | `provisional` |
| 7 | Säilytysajat: pöytäkirja, luonnos, työaineisto | `07`: pöytäkirja pysyvästi; luonnos poistetaan kun rekisteri on päivitetty; työaineisto käsittelyn jälkeen — yhtiö vahvistaa | `provisional` |
| 8 | Esteellisen jäsenen vaikutus päätösvaltaisuuden nimittäjään | Nimittäjä = valitut jäsenet (tiukempi lukutapa). Jos lukutapa on väärä, laskenta on liian tiukka, ei liian väljä | `provisional` |

Kun kohta on tarkistettu, tila vaihdetaan `confirmed`-tilaan ja tarkistaja sekä päivä kirjataan tähän taulukkoon. Finlexin säädösteksti (https://www.finlex.fi/fi/lainsaadanto/2006/624) ei ole koneellisesti luettavissa, joten pykäläviittaukset on tarkistettava käsin ajantasaisesta laista.

## Normihierarkia

Kun säännöt ovat ristiriidassa, ylempi voittaa:

1. **Osakeyhtiölaki** — pakottavat säännökset
2. **Yhtiöjärjestys** — voi tiukentaa lakia, ei lieventää pakottavaa
3. **Yhtiökokouksen päätökset** — valtuutukset ja ohjeet hallitukselle
4. **Osakassopimus** — sitoo osakkaita, **ei yhtiötä eikä hallitusta suoraan**. Hallitus ottaa sen huomioon, mutta osakassopimuksen vastainen hallituksen päätös ei ole yhtiöoikeudellisesti pätemätön. Tämä ero on olennainen ja helposti unohtuva.
5. **Hallituksen omat päätökset ja työjärjestys**

Toimivallan rajat (`company/toimivallan-rajat.yaml`) kirjataan tämän hierarkian mukaan lähdetyyppi näkyvissä. Päätösvaltaisuuden ja allekirjoituksen säännöt (`company/hallituksen-kokoonpano.yaml → quorum_rule`, `signature_policy`) noudattavat samaa: laki on vähimmäistaso, yhtiöjärjestys voi tiukentaa, ja validointi soveltaa molempia.

## Mikä vaatii yhtiökokouksen

Hallitus ei yleissäännön mukaan voi päättää: yhtiöjärjestyksen muutos, osakeanti ilman valtuutusta, varojen jako ilman yhtiökokouksen päätöstä, tilinpäätöksen vahvistaminen, hallituksen ja tilintarkastajan valinta, sulautuminen ja jakautuminen. Jos jokin näistä nousee hallituksessa, agentti merkitsee sen **esitykseksi yhtiökokoukselle**, ei päätökseksi. Poikkeukset ovat tarkistettavien kohtien 4–5 alla.

## Hyväksyntätasot työtilassa

| Mitä | Kuka |
|---|---|
| Päätösteksti ja sen tila | Hallitus kokouksessa; sanamuodon vahvistaa puheenjohtaja (`wording_confirmed_by_chair`) |
| Valmis, allekirjoitettava asiakirja | Syntyy vain puhtaan validoinnin läpi — ei parametrilla, ei agentin päätöksellä |
| Vuosikello, työjärjestys | Hallitus |
| Kokoonpanon muutos | Vain yhtiökokouksen tai hallituksen pöytäkirjan perusteella |
| Toimivallan rajat | Puheenjohtaja tarkistaa; lähde on aina asiakirja |
| Tulkinnan vahvistus (`interpretation.status`) | Ihminen, päätöskohtaisesti, nimi ja päivä |
| Muistiinpanot ja havainnot | Agentti saa kirjata luonnoksena |

## Mitä agentti tekee, kun laki tulee vastaan

Sanoo sen. Ei tulkitse lakia päätökseksi, ei täytä aukkoa oletuksella, ei merkitse asiaa ratkaistuksi. Kirjaa havainnon ja ohjaa kysymyksen ihmiselle.
