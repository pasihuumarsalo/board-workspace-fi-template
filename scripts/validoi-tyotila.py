# -*- coding: utf-8 -*-
"""Tarkistaa koko työtilan: skeemat, tunnukset, kokoonpano ja liiketoimintasäännöt.

    python scripts/validoi-tyotila.py [--kokous PTK-000073] [--valmis] [--hiljainen]
                                      [--sisallyta-mallit] [--juuri polku]

Palauttaa 1, jos yksikin ERROR-tason löydös on, muuten 0. Sopii commit-koukkuun
ja CI-ajoon. Sama tarkistus ajetaan generaattorissa ennen pöytäkirjan
muodostamista — --valmis lisää ehdot, jotka koskevat vain allekirjoitettavaksi
tarkoitettua asiakirjaa (sanamuodon vahvistus, allekirjoittajat, koollekutsu).

Tulostaa lopuksi seuraavat vapaat tunnukset ja voimassa olevien päätösten
määrän — ne lasketaan KAIKISTA rekisteritiedostoista, ei README:n rivistä.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tyotila as T  # noqa: E402


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    def lippu(nimi, arvo=False):
        if nimi not in argv:
            return None if arvo else False
        i = argv.index(nimi)
        if arvo:
            v = argv[i + 1]
            del argv[i:i + 2]
            return v
        del argv[i]
        return True

    if '-h' in argv or '--help' in argv:
        print(__doc__)
        return 0
    kohde = lippu('--kokous', arvo=True)
    juuri = lippu('--juuri', arvo=True) or T.JUURI
    valmis = lippu('--valmis')
    hiljainen = lippu('--hiljainen')
    mallit = lippu('--sisallyta-mallit')
    if argv:
        print('Tuntematon parametri: %s' % ' '.join(argv))
        print(__doc__)
        return 2

    ty = T.lataa_tyotila(juuri, sisallyta_mallit=bool(mallit))
    if not ty['rekisterit'] and not hiljainen:
        print('Ei rekisteritiedostoja (decisions/*.yaml) — tarkistetaan vain yhtiö- ja kokoonpanotiedot.')
    loydokset = T.validoi(ty, kohde=kohde, valmis=bool(valmis))

    for taso in (T.ERROR, T.WARNING, T.INFO):
        rivit = [l for l in loydokset if l.taso == taso]
        if hiljainen and taso != T.ERROR:
            continue
        for l in rivit:
            print(l)
    virheita = len(T.virheet(loydokset))
    varoituksia = sum(1 for l in loydokset if l.taso == T.WARNING)
    if not hiljainen or virheita:
        print('\n%d estävää virhettä, %d varoitusta.%s' % (
            virheita, varoituksia, ' Valmista pöytäkirjaa ei voi muodostaa.' if virheita and valmis else ''))
    return 1 if virheita else 0


if __name__ == '__main__':
    sys.exit(main())
