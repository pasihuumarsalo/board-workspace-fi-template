# -*- coding: utf-8 -*-
"""Muodostaa hallituksen pöytäkirjan päätösrekisteristä Word-pohjalle.

    python templates/tee-poytakirja.py PTK-000073 [ulostulo.docx] [--valmis] [--rekisteri polku.yaml]

Muokkaa pohjaa PAIKOILLEEN kopiosta: tyylit ja Wordin automaattinen
pykälänumerointi periytyvät. Ulkoasumuutos tehdään siis Word-pohjaan, ei tähän.
Kohdat etsitään sisällön perusteella, ei kappalenumeron.

Toteuttaa governance/03:n säännöt: kokousnumero selkokielisenä juoksevana
numerona, ja monipäiväisessä kokouksessa avaus ja päättäminen kantavat päiväyksen.
Kieltäytyy, jos menettelykehys (session.opened_at/closed_at) puuttuu.
Oletus on LUONNOS; --valmis jättää bannerin pois.
"""
import copy, glob, io, os, re, shutil, sys
import yaml, docx
from docx.shared import Cm

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
JUURI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POHJA = os.path.join(JUURI, 'templates', 'poytakirjapohja.docx')


def pvm_fi(iso):
    v, k, pv = iso.split('-')
    return '%d.%d.%s' % (int(pv), int(k), v)


def juokseva_numero(ptk):
    """PTK-000073 -> '73'. Asiakirjalla numero on selkokielinen."""
    return str(int(ptk.rsplit('-', 1)[1]))


def korvaa(p, vanha, uusi):
    """Korvaa merkkijonon kappaleessa vaikka se olisi jakautunut useaan runiin."""
    runs = p.runs
    koko = ''.join(r.text for r in runs)
    if vanha not in koko:
        return False
    a = koko.index(vanha); b = a + len(vanha); pos = 0
    for r in runs:
        rt = r.text; rs, re_ = pos, pos + len(rt); pos = re_
        if re_ <= a or rs >= b:
            continue
        ls = max(a, rs) - rs; le = min(b, re_) - rs
        r.text = (rt[:ls] + uusi + rt[le:]) if rs <= a else (rt[:ls] + rt[le:])
    return True


def etsi(d, hakusana):
    for p in d.paragraphs:
        if hakusana in p.text:
            return p
    raise SystemExit('Pohjasta ei löytynyt kohtaa: %r' % hakusana)


def kloonaa(malli, teksti, lihava=False, numeroitu=True):
    """Kloonaa mallikappaleen. Numeroidut perivät listatyylin; muut saavat Normal-tyylin ja sisennyksen."""
    el = copy.deepcopy(malli._p)
    for r in el.findall(W + 'r'):
        el.remove(r)
    p = docx.text.paragraph.Paragraph(el, malli._parent)
    if not numeroitu:
        pPr = el.find(W + 'pPr')
        if pPr is not None:
            npr = pPr.find(W + 'numPr')
            if npr is not None:
                pPr.remove(npr)
        p.style = malli.part.document.styles['Normal']
        p.paragraph_format.left_indent = malli.paragraph_format.left_indent or Cm(1.27)
        p.paragraph_format.first_line_indent = Cm(0)
    p.add_run(teksti).bold = lihava
    return p


def jaa_kohdiksi(teksti):
    """Normalisoi välilyönnit ja jakaa '1. ' -luettelon omiksi kappaleikseen. Ei muuta sanamuotoa."""
    t = re.sub(r'\s+', ' ', teksti or '').strip()
    osat = re.split(r'(?=(?<![\d.])\d{1,2}\.\s+[A-ZÅÄÖ])', t)
    return [o.strip() for o in osat if o.strip()]


def hae_kokous(ptk, rekisteri=None):
    tiedostot = [rekisteri] if rekisteri else sorted(
        f for f in glob.glob(os.path.join(JUURI, 'decisions', '*.yaml'))
        if not os.path.basename(f).startswith('MALLI'))
    for f in tiedostot:
        data = yaml.safe_load(io.open(f, encoding='utf-8')) or {}
        for m in (data.get('meetings') or []):
            if m.get('minutes_number') == ptk:
                return m
    raise SystemExit('Kokousta %s ei löytynyt rekisteristä' % ptk)


def main():
    argv = sys.argv[1:]
    valmis = '--valmis' in argv
    rekisteri = None
    if '--rekisteri' in argv:
        i = argv.index('--rekisteri'); rekisteri = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    argv = [a for a in argv if not a.startswith('--')]
    if not argv:
        raise SystemExit(__doc__)
    ptk = argv[0]
    ulos = argv[1] if len(argv) > 1 else (('' if valmis else 'LUONNOS-') + ptk + '.docx')

    m = hae_kokous(ptk, rekisteri)
    q = m.get('quorum') or {}
    istunto = m.get('session') or {}
    if not istunto.get('opened_at') or not istunto.get('closed_at'):
        raise SystemExit('Kokoukselta puuttuu session.opened_at/closed_at — täytä menettelykehys (governance/03).')

    ap, ak = str(istunto['opened_at']).split(' ')
    lp, lk = str(istunto['closed_at']).split(' ')
    monipaivainen = ap != lp
    alku = ('%s klo %s' % (pvm_fi(ap), ak)) if monipaivainen else ('klo %s' % ak)
    loppu = ('%s klo %s' % (pvm_fi(lp), lk)) if monipaivainen else ('klo %s' % lk)
    paiva = ('%s – %s' % (pvm_fi(ap), pvm_fi(lp))) if monipaivainen else pvm_fi(ap)

    shutil.copy(POHJA, ulos)
    d = docx.Document(ulos)

    pp = etsi(d, 'Paikka')
    korvaa(pp, '[Kokouspaikka]', m.get('place') or '')
    korvaa(etsi(d, '[DD.MM.YYYY]'), '[DD.MM.YYYY]', paiva)
    korvaa(etsi(d, 'Kokous numero'), '[#]', juokseva_numero(ptk))
    korvaa(etsi(d, 'avasi kokouksen'), 'klo [HH:MM]', alku)
    korvaa(etsi(d, 'päätti kokouksen'), 'klo [HH:MM]', loppu)
    if q.get('present_count') is not None:
        korvaa(etsi(d, 'paikalla oli'), '[#]', str(q['present_count']))

    asiat = [p for p in d.paragraphs if p.text.strip() == '[ASIA #]']
    if not asiat:
        raise SystemExit('Pohjasta ei löytynyt [ASIA #] -kohtia')
    malli = asiat[0]
    ankkuri = malli._p

    def lisaa(teksti, lihava=False, numeroitu=True):
        nonlocal ankkuri
        p = kloonaa(malli, teksti, lihava=lihava, numeroitu=numeroitu)
        ankkuri.addnext(p._p); ankkuri = p._p

    for dec in (m.get('decisions') or []):
        lisaa(dec['title'], lihava=True)
        for osa in jaa_kohdiksi(dec.get('decision_text')):
            lisaa(osa, numeroitu=False)
        lisaa('Päätöstunnus: ' + dec['id'], numeroitu=False)

    ilman = m.get('items_without_decision') or []
    if ilman:
        lisaa('Käsitellyt asiat, joista ei tehty päätöstä', lihava=True)
        for osa in ilman:
            lisaa(re.sub(r'\s+', ' ', osa).strip(), numeroitu=False)

    for a in asiat:
        a._p.getparent().remove(a._p)

    if not valmis:
        b = kloonaa(malli, '', numeroitu=False)
        pp._p.addprevious(b._p)
        b.add_run('LUONNOS — ei allekirjoitettavaksi. Muodostettu päätösrekisteristä (%s). '
                  'Tarkistus ja allekirjoitus vahvistavat sanamuodot.' % ptk).bold = True
        b.paragraph_format.left_indent = Cm(0)

    d.save(ulos)
    print('%s: %s' % ('Pöytäkirja' if valmis else 'Luonnos', ulos))
    print('  kokous %s, %d päätöstä, %s' % (ptk, len(m.get('decisions') or []),
                                             'monipäiväinen' if monipaivainen else 'yksipäiväinen'))


if __name__ == '__main__':
    main()
