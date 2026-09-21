# Päätösrekisteri

Yksi tiedosto per tilikausi: `2026.yaml`, `2027.yaml`. Rakenne on tiedostossa `MALLI-tilikausi.yaml` — kopioi se uuden tilikauden pohjaksi ja korvaa esimerkkisisältö. Koneellinen skeema: `schema/paatosrekisteri.schema.json`. Kentät on kuvattu `governance/03`:ssa.

## Mitä rekisteri on ja mitä ei

Rekisteri on **kopio**. Päätösteksti on poimittu allekirjoitetusta pöytäkirjasta (tai odottaa sitä), ja alkuperäinen asiakirja on nimetty jokaisen kokouksen kohdalla. Jos ne ovat ristiriidassa, alkuperäinen ratkaisee.

Rekisteri sisältää myös **tulkintoja**: sitooko päätös yhä, mihin se liittyy, mitä siitä seuraa. Ne eivät ole kopioita mistään, ja jokaisen päätöksen `interpretation`-lohko kertoo, onko ihminen vahvistanut ne (`ai_tulkinta` → `ihmisen_vahvistama`, vahvistaja ja päivä). Vahvistamatonta tulkintaa ei käytetä päätöksen perusteena.

## Numerointi

Kokoukset ja päätökset numeroidaan juoksevasti ensimmäisestä alkaen, tiedostorajoista riippumatta. Numeroa ei käytetä uudelleen eikä jätetä väliin. Päätös ilman kokousta saa numeron samasta `PTK`-sarjasta kuin kokous (OYL 6:3 §: numeroidaan kuten pöytäkirja).

**Seuraava vapaa tunnus lasketaan, ei lueta:**

```bash
python scripts/validoi-tyotila.py
```

Se käy läpi kaikki tilikausitiedostot ja tulostaa seuraavan kokous- ja päätöstunnuksen sekä virheet: päällekkäiset tunnukset, aukot, väärä etuliite, pienenevä numero, viittaus olemattomaan päätökseen tai rajoitteeseen. Tässä tiedostossa ei ole käsin ylläpidettyä "seuraava numero"-riviä — se olisi toinen totuus.

## Henkilöt

Osallistujat, sijaiset, esteelliset, äänestäneet ja allekirjoittajat kirjataan `person_id`-tunnuksina, jotka ovat `company/hallituksen-kokoonpano.yaml`:ssa. Nimi tulostuu pöytäkirjaan sieltä. Tunnus, jota ei ole kokoonpanorekisterissä, on virhe.

## Kokous ilman päätöksiä on tieto, ei puute

Kokous, jossa ei tehty päätöksiä, kirjataan silti — läsnäolijat, käsitellyt asiat, mitä jäi avoimeksi (`items_without_decision`). Puuttuva kokous näyttäisi jälkikäteen samalta kuin pitämättä jäänyt. Ei-päätösvaltainen kokous ilman päätöksiä on sallittu tietue; ei-päätösvaltainen kokous, jossa on päätöksiä, on virhe.

## Tuodut pöytäkirjat

Jos aiempia pöytäkirjoja on tuotu, jokaisen kohdalla lukee `import_metadata`: mistä, milloin, kuinka luotettavasti. Alkuperäinen asiakirjan numero säilyy `legacy.original_minutes_number`-kentässä rekisterin juoksevan numeron rinnalla. Kokoonpanohistorian aukot ovat `company/hallituksen-kokoonpano.yaml` → `known_gaps`. Tuodusta pöytäkirjasta (`decision_text_status: kopio`) ei muodosteta uutta valmista asiakirjaa — alkuperäinen on jo arkistossa.
