# Päätösrekisteri

Yksi tiedosto per tilikausi: `2026.yaml`, `2027.yaml`. Rakenne on tiedostossa `MALLI-tilikausi.yaml` — kopioi se uuden tilikauden pohjaksi ja poista esimerkkisisältö.

## Mitä rekisteri on ja mitä ei

Rekisteri on **kopio**. Päätösteksti on poimittu allekirjoitetusta pöytäkirjasta (tai odottaa sitä), ja alkuperäinen asiakirja on nimetty jokaisen kokouksen kohdalla. Jos ne ovat ristiriidassa, alkuperäinen ratkaisee.

Rekisteri sisältää myös **tulkintoja**: sitooko päätös yhä, mihin se liittyy, mitä siitä seuraa. Ne eivät ole kopioita mistään, ja ne on merkitty `ai_tulkinta`-tilaan kunnes ihminen vahvistaa ne. Vahvistamatonta tulkintaa ei käytetä päätöksen perusteena.

## Numerointi

Kokoukset ja päätökset numeroidaan juoksevasti ensimmäisestä alkaen, tiedostorajoista riippumatta. Numeroa ei käytetä uudelleen eikä jätetä väliin. Seuraava vapaa numero on aina edellinen + 1 — ei tarvitse laskea tiedostoista, vaan se luetaan tämän tiedoston lopusta.

**Seuraava kokous:** PTK-000001
**Seuraava päätös:** DEC-000001

(Päivitä nämä rivit jokaisen kirjauksen yhteydessä.)

## Kokous ilman päätöksiä on tieto, ei puute

Kokous, jossa ei tehty päätöksiä, kirjataan silti — läsnäolijat, käsitellyt asiat, mitä jäi avoimeksi. Puuttuva kokous näyttäisi jälkikäteen samalta kuin pitämättä jäänyt.

## Tuodut pöytäkirjat

Jos aiempia pöytäkirjoja on tuotu, jokaisen kohdalla lukee `import_metadata`: mistä, milloin, kuinka luotettavasti. Alkuperäinen asiakirjan numero säilyy `legacy.original_minutes_number`-kentässä rekisterin juoksevan numeron rinnalla. Kokoonpanohistorian aukot ovat `company/hallituksen-kokoonpano.yaml` → `known_gaps`.
