# -*- coding: utf-8 -*-
"""Luo puhtaat asiakirjapohjat: poytakirjapohja.docx (kokous) ja
paatospohja-ilman-kokousta.docx (OYL 6:3 §:n päätös ilman kokousta).

    python templates/luo-pohja.py

Ajetaan kerran; sen jälkeen pohjia muokataan Wordissa (yhtiön nimi,
kokouspaikan oletus, allekirjoituslauseke). Rakennetta ei saa muuttaa:
numeroitu lista, [ASIA #]-merkinnät ja hakasulkeiset paikkamerkit ovat
generaattorin etsimiä kohtia. Osallistujat, poissaolijat ja allekirjoittajat
generaattori täyttää rekisteristä — niitä ei kirjoiteta pohjaan käsin.

Paikkamerkit:
  [Kokouspaikka] [DD.MM.YYYY] [#] [HH:MM]            kokouksen perustiedot
  [Etunimi Sukunimi] + rooli                          osallistujarivit (monistetaan)
  [Poissa]                                            poissa olleet jäsenet
  [LÄSNÄ] [JÄSENIÄ]                                   päätösvaltaisuuspykälä
  [ASIA #]                                            asiapykälät (monistetaan)
  [Allekirjoittaja] [rooli]                           allekirjoittajarivit (monistetaan)
  [LÄHETETTY] [MÄÄRÄAIKA] [TODENTAMINEN]              vain päätös ilman kokousta
"""
import os

import docx
from docx.shared import Pt

JUURI = os.path.dirname(os.path.abspath(__file__))


def uusi():
    d = docx.Document()
    for s in ('Normal', 'List Number'):
        d.styles[s].font.name = 'Calibri'
        d.styles[s].font.size = Pt(11)
    return d


def rivi(d, otsikko, arvo, rooli=None):
    p = d.add_paragraph()
    p.add_run(otsikko)
    p.add_run().add_tab(); p.add_run().add_tab()
    p.add_run(arvo)
    if rooli is not None:
        p.add_run().add_tab(); p.add_run(rooli)
    return p


def osallistujalohko(d, otsikko):
    rivi(d, otsikko, '[Etunimi Sukunimi]', 'puheenjohtaja')
    for _ in range(3):
        rivi(d, '', '[Etunimi Sukunimi]', 'jäsen')
    rivi(d, 'Poissa', '[Poissa]')


def allekirjoituslohko(d):
    d.add_paragraph()
    rivi(d, 'Vakuudeksi', 'Tämä asiakirja on allekirjoitettu sähköisesti ja sisältää erillisen '
         'allekirjoitussivun, jossa allekirjoituksen varmenne on näkyvissä.')
    rivi(d, 'Allekirjoitukset', '[Allekirjoittaja]', '[rooli]')
    rivi(d, '', '[Allekirjoittaja]', '[rooli]')


def poytakirja():
    d = uusi()
    d.sections[0].header.paragraphs[0].text = '[Yhtiön nimi]  ·  Hallituksen kokouksen pöytäkirja'
    rivi(d, 'Paikka', '[Kokouspaikka]')
    rivi(d, 'Päivä', '[DD.MM.YYYY]')
    osallistujalohko(d, 'Osallistujat')
    d.add_heading('Kokous numero [#]', level=1)
    pyk = lambda t: d.add_paragraph(t, style='List Number')
    pyk('Puheenjohtaja avasi kokouksen klo [HH:MM].')
    pyk('Todettiin, että kokous oli kutsuttu koolle yhtiöjärjestyksen mukaisesti ja että paikalla oli '
        '[LÄSNÄ] hallituksen [JÄSENIÄ] jäsenestä. Kokous todettiin lailliseksi ja päätösvaltaiseksi.')
    pyk('Hyväksyttiin kokouksen esityslista työjärjestykseksi.')
    pyk('[ASIA #]'); pyk('[ASIA #]'); pyk('[ASIA #]')
    pyk('Puheenjohtaja päätti kokouksen klo [HH:MM].')
    allekirjoituslohko(d)
    ulos = os.path.join(JUURI, 'poytakirjapohja.docx')
    d.save(ulos)
    return ulos


def paatos_ilman_kokousta():
    d = uusi()
    d.sections[0].header.paragraphs[0].text = '[Yhtiön nimi]  ·  Hallituksen päätös ilman kokousta (OYL 6:3 §)'
    rivi(d, 'Päätöspäivä', '[DD.MM.YYYY]')
    osallistujalohko(d, 'Osallistuneet')
    d.add_heading('Päätös ilman kokousta, numero [#]', level=1)
    pyk = lambda t: d.add_paragraph(t, style='List Number')
    pyk('Päätösehdotus toimitettiin hallituksen jäsenille [LÄHETETTY], ja kannat pyydettiin [MÄÄRÄAIKA] mennessä. '
        'Kaikille hallituksen jäsenille varattiin tilaisuus osallistua asian käsittelyyn.')
    pyk('Asian käsittelyyn osallistui [LÄSNÄ] hallituksen [JÄSENIÄ] jäsenestä. Päätös tehtiin päätösvaltaisena.')
    pyk('[ASIA #]'); pyk('[ASIA #]'); pyk('[ASIA #]')
    pyk('Päätös on todennettu: [TODENTAMINEN]. Päätös numeroidaan ja säilytetään kuten hallituksen '
        'kokouksen pöytäkirja (OYL 6:3 § 3 mom.).')
    allekirjoituslohko(d)
    ulos = os.path.join(JUURI, 'paatospohja-ilman-kokousta.docx')
    d.save(ulos)
    return ulos


if __name__ == '__main__':
    print('luotu:', poytakirja())
    print('luotu:', paatos_ilman_kokousta())
