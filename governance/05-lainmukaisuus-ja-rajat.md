# 05 — Lainmukaisuus ja hyväksyntärajat

**Tämä ei ole oikeudellista neuvontaa.** Se on luettelo niistä osakeyhtiölain kohdista, joihin työtilan käytännöt nojaavat, ja normihierarkia jota agentti soveltaa. Epäselvässä tilanteessa kysytään asiantuntijalta.

## Osakeyhtiölain (624/2006) kohdat, joihin työtila nojaa

| Kohta | Mitä | Miten näkyy työtilassa |
|---|---|---|
| **1:8 §** Johdon tehtävä | Huolellisuus ja yhtiön edun edistäminen | `decision_basis`-kenttä: mihin tietoon päätös perustui |
| **6:2 §** Hallituksen yleiset tehtävät | Hallinto ja toiminnan asianmukainen järjestäminen; kirjanpidon ja varainhoidon valvonta | Vuosikellon lakisääteiset asiat |
| **6:3 §** Päätöksenteko | Päätösvaltainen kun yli puolet jäsenistä läsnä; päätös ilman kokousta mahdollinen | `quorum` lasketaan; `decision_method` |
| **6:4 §** Esteellisyys | Jäsen ei saa osallistua asiaan, jossa hänellä on olennainen etu | `conflict_of_interest` pakollinen |
| **6:5 §** Koolle kutsuminen | Puheenjohtaja kutsuu koolle; jäsen tai toimitusjohtaja voi vaatia | Työjärjestys |
| **6:6 §** Pöytäkirja | Pöytäkirja laaditaan, numeroidaan juoksevasti, allekirjoittaa pj + yksi jäsen; eriävä mielipide merkitään | Koko rekisteri; `vote` |
| **5:3 §** Varsinainen yhtiökokous | Kuuden kuukauden kuluessa tilikauden päättymisestä | Vuosikello |
| **13 luku** Varojen jakaminen | Vain laissa säädetyillä tavoilla; maksukykyisyys | Toimivallan rajat; voitonjakoesitykset |

## Normihierarkia

Kun säännöt ovat ristiriidassa, ylempi voittaa:

1. **Osakeyhtiölaki** — pakottavat säännökset
2. **Yhtiöjärjestys** — voi tiukentaa lakia, ei lieventää pakottavaa
3. **Yhtiökokouksen päätökset** — valtuutukset ja ohjeet hallitukselle
4. **Osakassopimus** — sitoo osakkaita, **ei yhtiötä eikä hallitusta suoraan**. Hallitus ottaa sen huomioon, mutta osakassopimuksen vastainen hallituksen päätös ei ole yhtiöoikeudellisesti pätemätön. Tämä ero on olennainen ja helposti unohtuva.
5. **Hallituksen omat päätökset ja työjärjestys**

Toimivallan rajat (`company/toimivallan-rajat.yaml`) kirjataan tämän hierarkian mukaan lähdetyyppi näkyvissä.

## Mikä vaatii yhtiökokouksen

Hallitus ei voi päättää: yhtiöjärjestyksen muutos, osakeanti ilman valtuutusta, varojen jako ilman yhtiökokouksen päätöstä, tilinpäätöksen vahvistaminen, hallituksen ja tilintarkastajan valinta, sulautuminen ja jakautuminen. Jos jokin näistä nousee hallituksessa, agentti merkitsee sen **esitykseksi yhtiökokoukselle**, ei päätökseksi.

## Hyväksyntätasot työtilassa

| Mitä | Kuka |
|---|---|
| Päätösteksti ja sen tila | Hallitus kokouksessa; sanamuodon vahvistaa puheenjohtaja |
| Vuosikello, työjärjestys | Hallitus |
| Kokoonpanon muutos | Vain yhtiökokouksen tai hallituksen pöytäkirjan perusteella |
| Toimivallan rajat | Puheenjohtaja tarkistaa; lähde on aina asiakirja |
| Muistiinpanot ja havainnot | Agentti saa kirjata luonnoksena |

## Mitä agentti tekee, kun laki tulee vastaan

Sanoo sen. Ei tulkitse lakia päätökseksi, ei täytä aukkoa oletuksella, ei merkitse asiaa ratkaistuksi. Kirjaa havainnon ja ohjaa kysymyksen ihmiselle.
