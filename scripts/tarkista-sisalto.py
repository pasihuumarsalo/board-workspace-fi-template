# -*- coding: utf-8 -*-
"""Tarkistaa, ettei repossa ole merkkijonoja, jotka eivät kuulu julkiseen templateen.

    python scripts/tarkista-sisalto.py [kielletyt.txt]

Kiellettyjen merkkijonojen lista luetaan tiedostosta, oletuksena
.paikallinen/kielletyt-merkkijonot.txt. Tiedosto on gitignoroitu, koska lista
itsessään sisältää ne nimet, joita ei saa julkaista.

Rivin muoto:  merkkijono            -> kielletty kaikkialla
              merkkijono ;; A, B    -> kielletty paitsi tiedostoissa A ja B
Poikkeus on tarkoitettu esim. tekijänoikeuden haltijan nimelle, jonka PITÄÄ
olla lisenssitiedostoissa mutta ei missään muualla.

Yhtiö voi käyttää samaa työkalua omassa työtilassaan päinvastaiseen suuntaan:
tarkistaa, ettei esimerkiksi henkilötunnuksen muotoista merkkijonoa ole päätynyt
rekisteriin (kaava on mukana oletuksena).

Palauttaa 0 jos puhdas, 1 jos löytyi osumia. Sopii commit-koukkuun.
"""
import io, os, re, sys

JUURI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OHITA = {'.git', '.paikallinen', '__pycache__', 'import'}
TEKSTIPAATTEET = {'.md', '.yaml', '.yml', '.py', '.txt', '.json', '.gitignore', ''}

# Henkilötunnuksen muoto: PPKKVV[+-A]NNNT. Tarkistetaan aina, listasta riippumatta.
HETU = re.compile(r'\b\d{6}[+\-A]\d{3}[0-9A-Y]\b')


def lue_kielletyt(polku):
    if not os.path.exists(polku):
        print('Kiellettyjen listaa ei löydy: %s — tarkistetaan vain henkilötunnusmuoto.' % polku)
        return []
    rivit = []
    for r in io.open(polku, encoding='utf-8'):
        r = r.strip()
        if not r or r.startswith('#'):
            continue
        if ';;' in r:
            token, sallitut = r.split(';;', 1)
            sallitut = {os.path.normpath(x.strip()) for x in sallitut.split(',') if x.strip()}
        else:
            token, sallitut = r, set()
        rivit.append((token.strip().lower(), sallitut))
    return rivit


def tiedostot():
    for hak, alih, tied in os.walk(JUURI):
        alih[:] = [a for a in alih if a not in OHITA]
        for t in tied:
            p = os.path.join(hak, t)
            if os.path.splitext(t)[1].lower() in TEKSTIPAATTEET:
                yield p


def main():
    lista = sys.argv[1] if len(sys.argv) > 1 else os.path.join(JUURI, '.paikallinen', 'kielletyt-merkkijonot.txt')
    kielletyt = lue_kielletyt(lista)
    osumia = 0
    for p in tiedostot():
        try:
            teksti = io.open(p, encoding='utf-8').read()
        except (UnicodeDecodeError, OSError):
            continue
        suht = os.path.relpath(p, JUURI)
        for i, rivi in enumerate(teksti.split('\n'), 1):
            r = rivi.lower()
            for k, sallitut in kielletyt:
                if k in r and os.path.normpath(suht) not in sallitut:
                    print('KIELLETTY  %s:%d  "%s"' % (suht, i, k))
                    osumia += 1
            if HETU.search(rivi) and 'PPKKVV' not in rivi:
                print('HETU?      %s:%d  %s' % (suht, i, rivi.strip()[:70]))
                osumia += 1
    if osumia:
        print('\n%d osumaa. Älä committaa ennen kuin nämä on poistettu.' % osumia)
        return 1
    print('Puhdas: ei kiellettyjä merkkijonoja eikä henkilötunnusmuotoa.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
