# -*- coding: utf-8 -*-
"""Tarkistaa, ettei repossa ole sisältöä, joka ei kuulu sinne: henkilötunnuksia,
salaisuuksia eikä kiellettyjä merkkijonoja — myös Word-tiedostojen tekstistä.

    python scripts/tarkista-sisalto.py [--staged] [--lista kielletyt.txt]

Kolme tarkistusta:
  1. Henkilötunnuksen muoto PPKKVV<merkki>NNNT kaikilla käytössä olevilla
     vuosisatamerkeillä (+  -  Y X W V U  A B C D E F). Jos tarkistusmerkki
     täsmää, osuma on HETU; jos vain muoto täsmää, HETU?. Molemmat estävät.
  2. Salaisuuksien tunnetut muodot (yksityiset avaimet, GitHub-/API-tokenit,
     "password: '...'" -tyyppiset rivit).
  3. Kiellettyjen merkkijonojen lista (oletus .paikallinen/kielletyt-merkkijonot.txt,
     gitignoroitu — lista itsessään sisältää nimet, joita ei saa julkaista).
     Rivin muoto:  merkkijono            -> kielletty kaikkialla
                   merkkijono ;; A, B    -> kielletty paitsi tiedostoissa A ja B

Tarkistettavat tiedostot: tekstitiedostot ja .docx (word/document.xml, ylä- ja
alatunnisteet, kommentit). Muut binaarit — pdf, xlsx, kuvat — EIVÄT tule
tarkistetuiksi, ja ne luetellaan lopussa nimeltä. Tarkistus ei väitä repoa
puhtaaksi tarkistamatta jääneiden tiedostojen osalta.

--staged tarkistaa vain git-indeksissä olevat tiedostot (commit-koukku).
Palauttaa 0 jos puhdas, 1 jos osumia.
"""
import html
import io
import os
import re
import subprocess
import sys
import zipfile

JUURI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OHITA = {'.git', '.paikallinen', '__pycache__', 'import', 'node_modules'}
TEKSTIPAATTEET = {'.md', '.yaml', '.yml', '.py', '.txt', '.json', '.gitignore', '.gitattributes', '.sh', '.csv', ''}
WORD = {'.docx'}

HETU = re.compile(r'(?<![\w/.-])(\d{2})(\d{2})(\d{2})([+\-ABCDEFYXWVU])(\d{3})([0-9ABCDEFHJKLMNPRSTUVWXY])(?![\w/-])')
TARKISTUSMERKIT = '0123456789ABCDEFHJKLMNPRSTUVWXY'
SALAISUUDET = [
    ('YKSITYINEN AVAIN', re.compile(r'-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY')),
    ('GITHUB-TOKEN', re.compile(r'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b')),
    ('API-AVAIN', re.compile(r'\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}\b|\bAKIA[0-9A-Z]{16}\b')),
    ('SALASANA/TOKEN', re.compile(r'(?i)\b(?:password|passwd|salasana|api[_-]?key|secret|token)\b\s*[:=]\s*["\'][^"\']{8,}["\']')),
]


def on_hetu(m):
    """True, jos päivä/kuukausi ovat mahdollisia ja tarkistusmerkki täsmää;
    False jos vain muoto täsmää; None jos päivä on mahdoton (ei osuma)."""
    pp, kk = int(m.group(1)), int(m.group(2))
    if not (1 <= pp <= 31 and 1 <= kk <= 12):
        return None
    luku = int(m.group(1) + m.group(2) + m.group(3) + m.group(5))
    return TARKISTUSMERKIT[luku % 31] == m.group(6)


def lue_kielletyt(polku):
    if not os.path.exists(polku):
        return None
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


def kaikki_tiedostot():
    for hak, alih, tied in os.walk(JUURI):
        alih[:] = [a for a in alih if a not in OHITA]
        for t in tied:
            yield os.path.join(hak, t)


def indeksin_tiedostot():
    ulos = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR'], cwd=JUURI)
    for rivi in ulos.decode('utf-8', 'replace').splitlines():
        p = os.path.join(JUURI, rivi.strip())
        if rivi.strip() and os.path.exists(p):
            yield p


def word_teksti(polku):
    """Word-tiedoston tekstisisältö rungosta, ylä-/alatunnisteista ja kommenteista.
    Runit yhdistetään kappaleen sisällä, jotta ajojen katkoma numero löytyy."""
    osat = []
    with zipfile.ZipFile(polku) as z:
        for n in z.namelist():
            if re.match(r'word/(document|header\d*|footer\d*|comments|footnotes|endnotes)\.xml$', n):
                xml = z.read(n).decode('utf-8', 'replace')
                for kappale in re.split(r'</w:p>', xml):
                    teksti = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', kappale))
                    if teksti.strip():
                        osat.append(html.unescape(teksti))
    return '\n'.join(osat)


def tarkista_teksti(teksti, suht, kielletyt):
    osumia = 0
    for i, rivi in enumerate(teksti.split('\n'), 1):
        r = rivi.lower()
        for k, sallitut in (kielletyt or []):
            if k in r and os.path.normpath(suht) not in sallitut:
                print('KIELLETTY  %s:%d  "%s"' % (suht, i, k))
                osumia += 1
        if 'ppkkvv' in r:
            continue
        for m in HETU.finditer(rivi):
            tulos = on_hetu(m)
            if tulos is None:
                continue
            print('%-10s %s:%d  %s' % ('HETU' if tulos else 'HETU?', suht, i, rivi.strip()[:70]))
            osumia += 1
        for nimi, kaava in SALAISUUDET:
            if kaava.search(rivi) and 'SALAISUUDET' not in rivi:
                print('%-10s %s:%d  %s' % (nimi, suht, i, rivi.strip()[:70]))
                osumia += 1
    return osumia


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    staged = '--staged' in argv
    lista = os.path.join(JUURI, '.paikallinen', 'kielletyt-merkkijonot.txt')
    if '--lista' in argv:
        lista = argv[argv.index('--lista') + 1]
    elif len([a for a in argv if not a.startswith('--')]) == 1:
        lista = [a for a in argv if not a.startswith('--')][0]
    kielletyt = lue_kielletyt(lista)
    if kielletyt is None:
        print('Kiellettyjen listaa ei ole (%s) — tarkistetaan henkilötunnukset ja salaisuudet.' % os.path.relpath(lista, JUURI))

    osumia, tarkistettu, ohitettu = 0, 0, []
    for p in (indeksin_tiedostot() if staged else kaikki_tiedostot()):
        suht = os.path.relpath(p, JUURI)
        paate = os.path.splitext(p)[1].lower()
        if os.path.basename(p) == 'kielletyt-merkkijonot.txt':
            continue
        try:
            if paate in WORD:
                teksti = word_teksti(p)
            elif paate in TEKSTIPAATTEET:
                teksti = io.open(p, encoding='utf-8').read()
            else:
                ohitettu.append(suht)
                continue
        except (UnicodeDecodeError, OSError, zipfile.BadZipFile) as e:
            print('EI LUETTU  %s  (%s)' % (suht, e.__class__.__name__))
            ohitettu.append(suht)
            continue
        tarkistettu += 1
        osumia += tarkista_teksti(teksti, suht, kielletyt)

    print('\nTarkistettu %d tiedostoa%s.' % (tarkistettu, ' (vain git-indeksi)' if staged else ''))
    if ohitettu:
        print('EI TARKISTETTU (%d, binaari tai tuntematon pääte): %s' % (len(ohitettu), ', '.join(sorted(ohitettu))))
    if osumia:
        print('%d osumaa. Älä committaa ennen kuin nämä on poistettu.' % osumia)
        return 1
    print('Puhdas tarkistettujen tiedostojen osalta.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
