# -*- coding: utf-8 -*-
"""Hallituksen työtilan yhteinen kirjasto: rekisterin lataus, johdetut tiedot ja
liiketoimintasääntöjen tarkistus.

Käyttäjät: scripts/validoi-tyotila.py (komentorivi), templates/tee-poytakirja.py
(generaattori tarkistaa kokouksen ennen asiakirjan muodostamista) ja tests/.

Periaate: kaikki, mikä voidaan johtaa rekisteristä, johdetaan täällä. Jos sama
tieto on kirjoitettu rekisteriin käsin, sen on täsmättävä johdettuun — muuten
se on virhe, ei näkökulmaero. Päätösvaltaisuus lasketaan, ei kirjoiteta.

Löydösten tasot:
  ERROR    estää valmiin pöytäkirjan muodostamisen
  WARNING  vaatii ihmisen tarkistuksen, ei estä luonnosta
  INFO     huomio tai suositus
"""
import datetime as dt
import glob
import io
import json
import os
import re

import yaml

JUURI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKEEMAT = os.path.join(JUURI, 'schema')

ERROR, WARNING, INFO = 'ERROR', 'WARNING', 'INFO'
TUNNUS = re.compile(r'^(?P<etuliite>[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-)(?P<numero>\d{6})$')

PAATOSTAVAT = ('meeting', 'without_meeting')
TEKSTITILAT = ('kopio', 'kopio_kuvasta', 'odottaa_allekirjoitusta')
TULKINTATILAT = ('ai_tulkinta', 'ihmisen_vahvistama')
VOIMASSAOLOT = ('in_force', 'executed', 'superseded', 'expired', 'undetermined')
ROOLIT = ('chair', 'vice_chair', 'member', 'deputy')
ALLEKIRJOITUSMALLIT = ('chair_plus_one', 'all_members_in_term', 'all_present_members')
KANNAT = ('for', 'against', 'abstain', 'no_response')

SKEEMATIEDOSTOT = {
    'yhtio': 'yhtio.schema.json',
    'kokoonpano': 'kokoonpano.schema.json',
    'rajat': 'toimivallan-rajat.schema.json',
    'vuosikello': 'vuosikello.schema.json',
    'rekisteri': 'paatosrekisteri.schema.json',
}


class Loydos(object):
    def __init__(self, taso, koodi, kohde, viesti):
        self.taso, self.koodi, self.kohde, self.viesti = taso, koodi, kohde or '-', viesti

    def __str__(self):
        return '%-7s %-22s %-16s %s' % (self.taso, self.koodi, self.kohde, self.viesti)

    def __repr__(self):
        return 'Loydos(%s, %s, %s)' % (self.taso, self.koodi, self.kohde)


def virheet(loydokset):
    return [l for l in loydokset if l.taso == ERROR]


# --------------------------------------------------------------------------- lataus

def lataa_yaml(polku):
    with io.open(polku, encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def lataa_tyotila(juuri=JUURI, sisallyta_mallit=False, rekisteri=None):
    """Lataa koko työtilan. rekisteri = yksi decisions-tiedosto muiden sijaan."""
    t = {'juuri': juuri, 'yhtio': {}, 'kokoonpano': {}, 'rajat': {}, 'vuosikello': {}, 'rekisterit': []}
    for avain, polku in (('yhtio', 'company/yhtio.yaml'),
                         ('kokoonpano', 'company/hallituksen-kokoonpano.yaml'),
                         ('rajat', 'company/toimivallan-rajat.yaml'),
                         ('vuosikello', 'annual-cycle/vuosikello.yaml')):
        p = os.path.join(juuri, polku)
        if os.path.exists(p):
            t[avain] = lataa_yaml(p)
    if rekisteri:
        tiedostot = [rekisteri]
    else:
        tiedostot = [f for f in sorted(glob.glob(os.path.join(juuri, 'decisions', '*.yaml')))
                     if sisallyta_mallit or not os.path.basename(f).startswith('MALLI')]
    for f in tiedostot:
        t['rekisterit'].append((os.path.relpath(f, juuri) if os.path.isabs(f) else f, lataa_yaml(f)))
    return t


def kokoukset(tyotila):
    for polku, data in tyotila['rekisterit']:
        for m in (data.get('meetings') or []):
            yield polku, m


def hae_kokous(tyotila, ptk):
    for _, m in kokoukset(tyotila):
        if m.get('minutes_number') == ptk:
            return m
    return None


# --------------------------------------------------------------------------- apurit

def pvm(x):
    if x is None:
        return None
    if isinstance(x, dt.datetime):
        return x.date()
    if isinstance(x, dt.date):
        return x
    try:
        return dt.date.fromisoformat(str(x).strip()[:10])
    except ValueError:
        return None


def aikaleima(x):
    """'YYYY-MM-DD HH:MM' -> datetime, muuten None. Pelkkä päivä ei ole aikaleima."""
    if isinstance(x, dt.datetime):
        return x
    if x is None or isinstance(x, dt.date):
        return None
    s = str(x).strip()
    for muoto in ('%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S'):
        try:
            return dt.datetime.strptime(s, muoto)
        except ValueError:
            pass
    return None


def pvm_fi(paiva):
    p = pvm(paiva)
    return '%d.%d.%d' % (p.day, p.month, p.year) if p else ''


def tunnus_osat(t):
    m = TUNNUS.match(str(t or '').strip())
    return (m.group('etuliite'), int(m.group('numero'))) if m else (None, None)


def json_kelpoinen(x):
    """YAML-päivät merkkijonoiksi, jotta JSON Schema voi tarkistaa muodon."""
    if isinstance(x, dict):
        return {str(k): json_kelpoinen(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [json_kelpoinen(v) for v in x]
    if isinstance(x, dt.datetime):
        return x.strftime('%Y-%m-%d %H:%M')
    if isinstance(x, dt.date):
        return x.isoformat()
    return x


# --------------------------------------------------------------------------- kokoonpano

def henkilot(kokoonpano):
    """person_id -> tietue. Myöhempi toimikausi voittaa; toimitusjohtaja mukana."""
    h = {}
    for t in (kokoonpano.get('terms') or []):
        for j in (t.get('members') or []):
            if j.get('person_id'):
                h[j['person_id']] = j
    tj = kokoonpano.get('ceo') or {}
    if tj.get('person_id') and tj['person_id'] not in h:
        h[tj['person_id']] = dict(tj, board_role=None, executive_role='ceo')
    return h


def nimi(kokoonpano, pid):
    return (henkilot(kokoonpano).get(pid) or {}).get('display_name') or str(pid)


def _voimassa(paiva, alku, loppu):
    a, l = pvm(alku), pvm(loppu)
    return a is not None and a <= paiva and (l is None or paiva <= l)


def toimikausi_paivana(kokoonpano, paiva):
    paiva = pvm(paiva)
    if paiva is None:
        return None
    for t in (kokoonpano.get('terms') or []):
        if _voimassa(paiva, t.get('valid_from'), t.get('valid_until')):
            return t
    return None


def jasenet_paivana(kokoonpano, paiva):
    """Päätösoikeudelliset jäsenet (ei varajäseniä) annettuna päivänä.
    None = kokoonpano ei tiedossa (eri asia kuin tyhjä lista)."""
    paiva = pvm(paiva)
    t = toimikausi_paivana(kokoonpano, paiva)
    if t is None:
        return None
    out = []
    for j in (t.get('members') or []):
        if j.get('board_role') == 'deputy' or j.get('decision_right') is False:
            continue
        alku = j.get('valid_from') or t.get('valid_from')
        loppu = j.get('valid_until') or t.get('valid_until')
        if _voimassa(paiva, alku, loppu) and j.get('person_id'):
            out.append(j['person_id'])
    return out


def rooli_paivana(kokoonpano, pid, paiva):
    t = toimikausi_paivana(kokoonpano, paiva)
    for j in ((t or {}).get('members') or []):
        if j.get('person_id') == pid:
            return j.get('board_role')
    return None


def puheenjohtaja_paivana(kokoonpano, paiva):
    t = toimikausi_paivana(kokoonpano, paiva)
    for j in ((t or {}).get('members') or []):
        if j.get('board_role') == 'chair' and _voimassa(pvm(paiva), j.get('valid_from') or t.get('valid_from'),
                                                      j.get('valid_until') or t.get('valid_until')):
            return j.get('person_id')
    return None


def toimitusjohtaja_paivana(kokoonpano, paiva):
    tj = kokoonpano.get('ceo') or {}
    if tj.get('person_id') and _voimassa(pvm(paiva), tj.get('valid_from'), tj.get('valid_until')):
        return tj['person_id']
    return None


# --------------------------------------------------------------------------- päätösvaltaisuus

def paatosvaltaisuussaanto(kokoonpano):
    s = kokoonpano.get('quorum_rule') or {}
    return {'type': s.get('type') or 'more_than_half',
            'numerator': s.get('numerator'), 'denominator': s.get('denominator'),
            'min_count': s.get('min_count'),
            'source': s.get('source') or 'OYL 6:3 § — yli puolet jäsenistä'}


def on_paatosvaltainen(entitled, participating, saanto):
    """Lain vähimmäisvaatimus (yli puolet valituista jäsenistä) pätee aina;
    yhtiöjärjestys voi vain tiukentaa (fraction / min_count)."""
    if entitled <= 0:
        return False
    ok = participating * 2 > entitled
    if saanto.get('type') == 'fraction' and saanto.get('numerator') and saanto.get('denominator'):
        ok = ok and participating * saanto['denominator'] >= entitled * saanto['numerator']
    elif saanto.get('type') == 'min_count' and saanto.get('min_count'):
        ok = ok and participating >= saanto['min_count']
    return ok


def lasnaolijat(m):
    """Päätösoikeudelliset läsnäolijat: läsnä olleet jäsenet + sijaisina toimineet varajäsenet."""
    s = list(m.get('participants') or [])
    for d in (m.get('deputy_substitutions') or []):
        if d.get('deputy_person_id') and d['deputy_person_id'] not in s:
            s.append(d['deputy_person_id'])
    return s


def poissaolijat(m):
    las = set(lasnaolijat(m))
    sijaistetut = {d.get('for_person_id') for d in (m.get('deputy_substitutions') or [])}
    return [p for p in (m.get('entitled_participants') or []) if p not in las and p not in sijaistetut]


def sijaistetut(m):
    return [d.get('for_person_id') for d in (m.get('deputy_substitutions') or []) if d.get('for_person_id')]


def johda_kokouksen_paatosvaltaisuus(m, saanto):
    ent, las = list(m.get('entitled_participants') or []), lasnaolijat(m)
    return {'basis': saanto['source'], 'entitled_count': len(ent), 'present_count': len(las),
            'is_quorate': on_paatosvaltainen(len(ent), len(las), saanto), 'derived': True}


def normalisoi_esteellisyys(v):
    """Hyväksyy sekä lyhyen muodon `none` että täyden objektin. None = ei kirjattu."""
    if v is None:
        return None
    if isinstance(v, str):
        if v.strip().lower() == 'none':
            return {'status': 'none', 'disqualified_person_ids': [], 'note': None, 'left_room': None}
        return {'status': 'declared', 'disqualified_person_ids': [], 'note': v, 'left_room': None}
    d = dict(v)
    d.setdefault('disqualified_person_ids', [])
    d['disqualified_person_ids'] = list(d['disqualified_person_ids'] or [])
    d.setdefault('status', 'declared' if d['disqualified_person_ids'] else 'none')
    d.setdefault('note', None)
    d.setdefault('left_room', None)
    return d


def johda_paatoksen_paatosvaltaisuus(m, dec, saanto):
    """Esteellinen jäsen ei osallistu asian käsittelyyn (OYL 6:4 §), joten häntä ei
    lasketa osallistujaksi. Nimittäjänä pidetään valittuja jäseniä (OYL 6:3 §:
    'määrä lasketaan valituista hallituksen jäsenistä') — tiukempi lukutapa,
    oikeudellinen tarkistus avoin (governance/05)."""
    ent, las = list(m.get('entitled_participants') or []), lasnaolijat(m)
    est = normalisoi_esteellisyys(dec.get('conflict_of_interest')) or {}
    dis = est.get('disqualified_person_ids') or []
    osall = [p for p in las if p not in dis]
    return {'basis': saanto['source'] + '; esteellinen ei osallistu (OYL 6:4 §)',
            'entitled_count': len(ent), 'disqualified_person_ids': list(dis),
            'eligible_count': len([p for p in ent if p not in dis]),
            'participating_person_ids': osall, 'participating_count': len(osall),
            'is_quorate': on_paatosvaltainen(len(ent), len(osall), saanto), 'derived': True}


# --------------------------------------------------------------------------- tunnukset ja koosteet

def etuliitteet(tyotila):
    p = (tyotila.get('yhtio') or {}).get('id_prefix') or {}
    return p.get('minutes') or 'PTK-', p.get('decision') or 'DEC-'


def seuraavat_tunnukset(tyotila):
    """Lasketaan KAIKISTA rekisteritiedostoista — README:n käsin ylläpidetty rivi ei ole lähde."""
    ptk_e, dec_e = etuliitteet(tyotila)
    ptk = [n for _, m in kokoukset(tyotila) for _, n in [tunnus_osat(m.get('minutes_number'))] if n]
    dec = [n for _, m in kokoukset(tyotila) for d in (m.get('decisions') or [])
           for _, n in [tunnus_osat(d.get('id'))] if n]
    return '%s%06d' % (ptk_e, (max(ptk) + 1) if ptk else 1), '%s%06d' % (dec_e, (max(dec) + 1) if dec else 1)


def voimassa_olevat(tyotila):
    """Kaikista tilikausista, ei vain uusimmasta. Palauttaa (kokous, päätös, vahvistettu?)."""
    out = []
    for _, m in kokoukset(tyotila):
        for d in (m.get('decisions') or []):
            if d.get('effect_status') == 'in_force':
                tulk = d.get('interpretation') or {}
                out.append((m, d, tulk.get('status') == 'ihmisen_vahvistama'))
    return out


def allekirjoitusmalli(tyotila, m):
    pol = (tyotila.get('kokoonpano') or {}).get('signature_policy') or {}
    return ((m.get('signatures') or {}).get('policy')) or pol.get('required_signers') or 'chair_plus_one'


def vaaditut_allekirjoittajat(tyotila, m):
    """Mitä allekirjoituspolitiikka edellyttää. chair_plus_one: puheenjohtaja + vähintään
    yksi hallituksen valitsema jäsen (OYL 6:6 §); yksijäsenisessä hallituksessa jäsen itse."""
    malli = allekirjoitusmalli(tyotila, m)
    ent = list(m.get('entitled_participants') or [])
    pj = (m.get('roles') or {}).get('meeting_chair_person_id')
    if malli == 'all_members_in_term':
        return {'policy': malli, 'must_include': list(ent), 'min_count': len(ent)}
    if malli == 'all_present_members':
        las = lasnaolijat(m)
        return {'policy': malli, 'must_include': las, 'min_count': len(las)}
    if len(ent) <= 1:
        return {'policy': malli, 'must_include': ent, 'min_count': 1}
    return {'policy': malli, 'must_include': [pj] if pj else [], 'min_count': 2}


# --------------------------------------------------------------------------- validointi

def validoi_skeemat(tyotila):
    L = []
    try:
        import jsonschema
    except ImportError:
        return [Loydos(WARNING, 'SKEEMA-EI-KIRJASTOA', None,
                       'jsonschema-kirjasto puuttuu (pip install -r requirements.txt) — skeematarkistus ohitettiin')]
    kohteet = [(k, tyotila.get(k)) for k in ('yhtio', 'kokoonpano', 'rajat', 'vuosikello') if tyotila.get(k)]
    kohteet += [('rekisteri', data, polku) for polku, data in tyotila['rekisterit']]
    for kohde in kohteet:
        avain, data = kohde[0], kohde[1]
        nimi_ = kohde[2] if len(kohde) > 2 else avain
        polku = os.path.join(SKEEMAT, SKEEMATIEDOSTOT[avain])
        if not os.path.exists(polku):
            L.append(Loydos(WARNING, 'SKEEMA-PUUTTUU', nimi_, 'skeematiedostoa ei löydy: %s' % polku))
            continue
        with io.open(polku, encoding='utf-8') as f:
            skeema = json.load(f)
        v = jsonschema.Draft202012Validator(skeema, format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER)
        for e in sorted(v.iter_errors(json_kelpoinen(data)), key=lambda e: list(e.absolute_path)):
            paikka = '/'.join(str(p) for p in e.absolute_path) or '(juuri)'
            L.append(Loydos(ERROR, 'SKEEMA', nimi_, '%s: %s' % (paikka, e.message[:160])))
    return L


def validoi_kokoonpano(tyotila):
    L = []
    k = tyotila.get('kokoonpano') or {}
    termit = k.get('terms') or []
    avoimia = 0
    edellinen_loppu = None
    for t in sorted(termit, key=lambda t: str(pvm(t.get('valid_from')) or '')):
        tid = t.get('term_id') or '?'
        alku, loppu = pvm(t.get('valid_from')), pvm(t.get('valid_until'))
        if alku is None:
            L.append(Loydos(ERROR, 'KAUSI-ALKU', tid, 'toimikaudelta puuttuu valid_from'))
            continue
        if loppu is None:
            avoimia += 1
        elif loppu < alku:
            L.append(Loydos(ERROR, 'KAUSI-JARJESTYS', tid, 'valid_until on ennen valid_from'))
        if edellinen_loppu is not None and alku <= edellinen_loppu:
            L.append(Loydos(ERROR, 'KAUSI-PAALLEKKAIN', tid, 'toimikausi alkaa ennen edellisen päättymistä (%s)' % edellinen_loppu))
        if edellinen_loppu is None and loppu is None and len(termit) > 1 and t is not termit[-1]:
            pass
        edellinen_loppu = loppu if loppu else dt.date.max
        nahdyt, pj = set(), 0
        for j in (t.get('members') or []):
            pid = j.get('person_id')
            if not pid:
                L.append(Loydos(ERROR, 'JASEN-TUNNUS', tid, 'jäseneltä puuttuu person_id'))
                continue
            if pid in nahdyt:
                L.append(Loydos(ERROR, 'JASEN-KAHDESTI', tid, 'person_id %s kahdesti samalla toimikaudella' % pid))
            nahdyt.add(pid)
            if j.get('board_role') not in ROOLIT:
                L.append(Loydos(ERROR, 'JASEN-ROOLI', tid, '%s: tuntematon board_role %r' % (pid, j.get('board_role'))))
            if j.get('board_role') == 'chair':
                pj += 1
            ja, jl = pvm(j.get('valid_from')), pvm(j.get('valid_until'))
            if ja and ja < alku:
                L.append(Loydos(ERROR, 'JASEN-AIKA', tid, '%s alkaa ennen toimikautta' % pid))
            if jl and loppu and jl > loppu:
                L.append(Loydos(ERROR, 'JASEN-AIKA', tid, '%s päättyy toimikauden jälkeen' % pid))
            if ja and jl and jl < ja:
                L.append(Loydos(ERROR, 'JASEN-AIKA', tid, '%s: valid_until ennen valid_from' % pid))
        if pj == 0 and t.get('members'):
            L.append(Loydos(WARNING, 'KAUSI-EI-PJ', tid, 'toimikaudella ei ole puheenjohtajaa (board_role: chair)'))
    if avoimia > 1:
        L.append(Loydos(ERROR, 'KAUSI-USEA-AVOIN', None, '%d toimikautta ilman valid_until-päivää — vain nykyinen saa olla avoin' % avoimia))
    pol = k.get('signature_policy') or {}
    if pol and pol.get('required_signers') not in ALLEKIRJOITUSMALLIT:
        L.append(Loydos(ERROR, 'ALLEKIRJOITUSMALLI', None, 'tuntematon signature_policy.required_signers %r' % pol.get('required_signers')))
    if (k.get('quorum_rule') or {}).get('type') not in (None, 'more_than_half', 'fraction', 'min_count'):
        L.append(Loydos(ERROR, 'PAATOSVALTAISUUSSAANTO', None, 'tuntematon quorum_rule.type'))
    return L


def validoi_tunnukset(tyotila):
    L = []
    ptk_e, dec_e = etuliitteet(tyotila)
    ptk_nahdyt, dec_nahdyt = {}, {}
    ed_ptk, ed_dec, ed_pvm = None, None, None
    for polku, m in kokoukset(tyotila):
        ptk = m.get('minutes_number')
        e, n = tunnus_osat(ptk)
        if n is None:
            L.append(Loydos(ERROR, 'TUNNUS-MUOTO', str(ptk), 'kokoustunnus ei ole muotoa %sNNNNNN' % ptk_e))
        else:
            if e != ptk_e:
                L.append(Loydos(WARNING, 'TUNNUS-ETULIITE', ptk, 'etuliite %s poikkeaa yhtiön asetuksesta %s' % (e, ptk_e)))
            if ptk in ptk_nahdyt:
                L.append(Loydos(ERROR, 'TUNNUS-KAHDESTI', ptk, 'kokoustunnus käytetty kahdesti (%s ja %s)' % (ptk_nahdyt[ptk], polku)))
            ptk_nahdyt[ptk] = polku
            if ed_ptk is not None and n <= ed_ptk:
                L.append(Loydos(ERROR, 'TUNNUS-JARJESTYS', ptk, 'kokousnumero ei kasva edellisestä (%d)' % ed_ptk))
            elif ed_ptk is not None and n != ed_ptk + 1:
                L.append(Loydos(ERROR, 'TUNNUS-AUKKO', ptk, 'numerointi hyppää %d -> %d; väliin jäävä numero puuttuu' % (ed_ptk, n)))
            ed_ptk = n
        p = pvm(m.get('decision_date'))
        if p and ed_pvm and p < ed_pvm:
            L.append(Loydos(WARNING, 'PAIVA-JARJESTYS', ptk, 'decision_date %s on aiempi kuin edellisen kokouksen %s' % (p, ed_pvm)))
        ed_pvm = p or ed_pvm
        for d in (m.get('decisions') or []):
            did = d.get('id')
            e, n = tunnus_osat(did)
            if n is None:
                L.append(Loydos(ERROR, 'TUNNUS-MUOTO', str(did), 'päätöstunnus ei ole muotoa %sNNNNNN' % dec_e))
                continue
            if e != dec_e:
                L.append(Loydos(WARNING, 'TUNNUS-ETULIITE', did, 'etuliite %s poikkeaa yhtiön asetuksesta %s' % (e, dec_e)))
            if did in dec_nahdyt:
                L.append(Loydos(ERROR, 'TUNNUS-KAHDESTI', did, 'päätöstunnus käytetty kahdesti (%s ja %s)' % (dec_nahdyt[did], ptk)))
            dec_nahdyt[did] = ptk
            if ed_dec is not None and n <= ed_dec:
                L.append(Loydos(ERROR, 'TUNNUS-JARJESTYS', did, 'päätösnumero ei kasva edellisestä (%d)' % ed_dec))
            elif ed_dec is not None and n != ed_dec + 1:
                L.append(Loydos(ERROR, 'TUNNUS-AUKKO', did, 'numerointi hyppää %d -> %d' % (ed_dec, n)))
            ed_dec = n
    return L


def _paatokset(tyotila):
    return {d.get('id'): (m, d) for _, m in kokoukset(tyotila) for d in (m.get('decisions') or [])}


def _rajoitteet(tyotila):
    r = tyotila.get('rajat') or {}
    return {x.get('id') for x in (r.get('constraints') or []) + (r.get('authorizations') or []) if x.get('id')}


def validoi_kokous(tyotila, m, valmis=False, paatokset=None, rajoitteet=None):
    L = []
    k = tyotila.get('kokoonpano') or {}
    hlot = henkilot(k)
    saanto = paatosvaltaisuussaanto(k)
    ptk = m.get('minutes_number') or '?'
    paatokset = paatokset if paatokset is not None else _paatokset(tyotila)
    rajoitteet = rajoitteet if rajoitteet is not None else _rajoitteet(tyotila)
    tapa = m.get('decision_method')
    if tapa not in PAATOSTAVAT:
        L.append(Loydos(ERROR, 'PAATOSTAPA', ptk, 'decision_method oltava meeting tai without_meeting'))
    paiva = pvm(m.get('decision_date'))
    if paiva is None:
        L.append(Loydos(ERROR, 'PAIVA', ptk, 'decision_date puuttuu tai ei ole päivä'))
    if m.get('decision_text_status') not in TEKSTITILAT:
        L.append(Loydos(ERROR, 'TEKSTITILA', ptk, 'decision_text_status oltava %s' % '/'.join(TEKSTITILAT)))

    # Henkilöt ja roolit
    ent = list(m.get('entitled_participants') or [])
    las = lasnaolijat(m)
    roolit = m.get('roles') or {}
    pj = roolit.get('meeting_chair_person_id')
    if not pj:
        L.append(Loydos(ERROR, 'PJ-PUUTTUU', ptk, 'roles.meeting_chair_person_id puuttuu — kokouksen puheenjohtaja on kirjattava'))
    elif pj not in las:
        L.append(Loydos(ERROR, 'PJ-EI-LASNA', ptk, 'kokouksen puheenjohtaja %s ei ole läsnäolijoissa' % pj))
    for pid in set(ent) | set(las) | set(sijaistetut(m)) | ({pj} if pj else set()):
        if pid not in hlot:
            L.append(Loydos(ERROR, 'HENKILO-TUNTEMATON', ptk, 'person_id %r ei ole kokoonpanorekisterissä' % pid))
    for pid in (m.get('participants') or []):
        if pid not in ent:
            L.append(Loydos(ERROR, 'OSALLISTUJA-EI-OIKEUTTA', ptk, '%s on läsnäolijoissa mutta ei toimikauden jäsenissä (entitled_participants)' % pid))
    for d in (m.get('deputy_substitutions') or []):
        vj, puolesta = d.get('deputy_person_id'), d.get('for_person_id')
        if not vj or not puolesta:
            L.append(Loydos(ERROR, 'SIJAINEN-PUUTTEELLINEN', ptk, 'deputy_substitutions vaatii deputy_person_id ja for_person_id'))
            continue
        if puolesta not in ent:
            L.append(Loydos(ERROR, 'SIJAINEN-KOHDE', ptk, 'varajäsen %s sijaistaa %s, joka ei ole toimikauden jäsen' % (vj, puolesta)))
        if puolesta in (m.get('participants') or []):
            L.append(Loydos(ERROR, 'SIJAINEN-JA-JASEN', ptk, '%s on sekä läsnä että sijaistettu' % puolesta))
        if (hlot.get(vj) or {}).get('board_role') not in (None, 'deputy'):
            L.append(Loydos(WARNING, 'SIJAINEN-EI-VARAJASEN', ptk, '%s toimii sijaisena mutta ei ole varajäsen kokoonpanorekisterissä' % vj))
    if paiva:
        johdetut = jasenet_paivana(k, paiva)
        if johdetut is None:
            L.append(Loydos(INFO, 'KOKOONPANO-AUKKO', ptk, 'kokoonpanorekisterissä ei ole toimikautta päivälle %s — entitled_participants ei ole tarkistettavissa' % paiva))
        elif set(johdetut) != set(ent):
            L.append(Loydos(WARNING, 'KOKOONPANO-ERO', ptk, 'entitled_participants %s ≠ kokoonpanorekisterin jäsenet %s päivänä %s'
                            % (sorted(ent), sorted(johdetut), paiva)))
    if not ent:
        L.append(Loydos(ERROR, 'OIKEUTETUT-PUUTTUU', ptk, 'entitled_participants on tyhjä — päätösvaltaisuutta ei voi laskea'))

    # Kokoustason päätösvaltaisuus
    joh = johda_kokouksen_paatosvaltaisuus(m, saanto)
    q = m.get('quorum')
    if q is None:
        L.append(Loydos(WARNING, 'QUORUM-PUUTTUU', ptk, 'quorum-lohko puuttuu; johdettu: %d/%d, päätösvaltainen=%s'
                        % (joh['present_count'], joh['entitled_count'], joh['is_quorate'])))
    else:
        for kentta in ('entitled_count', 'present_count', 'is_quorate'):
            if q.get(kentta) is not None and q.get(kentta) != joh[kentta]:
                L.append(Loydos(ERROR, 'QUORUM-RISTIRIITA', ptk, 'quorum.%s on %r, johdettu %r — päätösvaltaisuus lasketaan, ei kirjoiteta'
                                % (kentta, q.get(kentta), joh[kentta])))
    if not joh['is_quorate'] and ent:
        taso = ERROR if (m.get('decisions') or []) else INFO
        L.append(Loydos(taso, 'EI-PAATOSVALTAINEN', ptk, 'läsnä %d / %d — ei päätösvaltainen (%s)' % (joh['present_count'], joh['entitled_count'], saanto['source'])))

    # Koollekutsuminen
    kutsu = m.get('notice')
    if not kutsu:
        L.append(Loydos(ERROR if valmis else WARNING, 'KUTSU-PUUTTUU', ptk, 'notice-lohko puuttuu — osallistumismahdollisuuden varaamista (OYL 6:3 §) ei ole kirjattu'))
    else:
        if kutsu.get('participation_opportunity_confirmed') is not True:
            L.append(Loydos(ERROR if valmis else WARNING, 'OSALLISTUMISMAHDOLLISUUS', ptk,
                            'notice.participation_opportunity_confirmed ei ole true'))
        kutsutut = set(kutsu.get('invited_person_ids') or [])
        if kutsutut and not set(ent) <= kutsutut:
            L.append(Loydos(WARNING, 'KUTSU-VAJAA', ptk, 'kaikki toimikauden jäsenet eivät ole notice.invited_person_ids-listalla: %s' % sorted(set(ent) - kutsutut)))

    # Päätöstapa
    istunto = m.get('session')
    if tapa == 'meeting':
        a = aikaleima((istunto or {}).get('opened_at'))
        l = aikaleima((istunto or {}).get('closed_at'))
        if not a or not l:
            L.append(Loydos(ERROR, 'ISTUNTO-PUUTTUU', ptk, 'session.opened_at/closed_at puuttuu tai ei ole muotoa "YYYY-MM-DD HH:MM"'))
        else:
            if l < a:
                L.append(Loydos(ERROR, 'ISTUNTO-JARJESTYS', ptk, 'closed_at on ennen opened_at'))
            if paiva and l.date() != paiva:
                L.append(Loydos(WARNING, 'PAIVA-ISTUNTO', ptk, 'decision_date %s ≠ päättämispäivä %s' % (paiva, l.date())))
        if not m.get('place'):
            L.append(Loydos(WARNING, 'PAIKKA', ptk, 'place puuttuu (kokouspaikka tai "etäkokous")'))
        if m.get('without_meeting'):
            L.append(Loydos(WARNING, 'ILMAN-KOKOUSTA-LOHKO', ptk, 'without_meeting-lohko on täytetty vaikka decision_method on meeting'))
    elif tapa == 'without_meeting':
        if istunto and (istunto.get('opened_at') or istunto.get('closed_at')):
            L.append(Loydos(ERROR, 'ISTUNTO-ILMAN-KOKOUSTA', ptk, 'päätöksellä ilman kokousta ei ole avaus-/päättämisaikaa — session on oltava null'))
        ik = m.get('without_meeting')
        if not ik:
            L.append(Loydos(ERROR, 'ILMAN-KOKOUSTA-PUUTTUU', ptk, 'without_meeting-lohko puuttuu (proposal_sent_at, response_deadline, responses, verification_method)'))
        else:
            vastaukset = ik.get('responses') or []
            vastanneet = {v.get('person_id') for v in vastaukset}
            for v in vastaukset:
                if v.get('person_id') not in ent:
                    L.append(Loydos(ERROR, 'VASTAUS-EI-JASEN', ptk, 'vastaaja %s ei ole toimikauden jäsen' % v.get('person_id')))
                if v.get('position') not in KANNAT:
                    L.append(Loydos(ERROR, 'VASTAUS-KANTA', ptk, '%s: position oltava %s' % (v.get('person_id'), '/'.join(KANNAT))))
            puuttuu = sorted(set(ent) - vastanneet)
            if puuttuu:
                L.append(Loydos(ERROR, 'OSALLISTUMISMAHDOLLISUUS', ptk,
                                'jäseniltä %s ei ole kirjattu vastausta eikä no_response-merkintää — jokaiselle jäsenelle on varattava tilaisuus (OYL 6:3 §)' % puuttuu))
            osallistuneet = {v.get('person_id') for v in vastaukset if v.get('position') in ('for', 'against', 'abstain')}
            if osallistuneet != set(m.get('participants') or []):
                L.append(Loydos(ERROR, 'OSALLISTUJAT-VASTAUKSET', ptk, 'participants %s ≠ vastauksen antaneet %s'
                                % (sorted(m.get('participants') or []), sorted(osallistuneet))))
            for kentta in ('proposal_sent_at', 'response_deadline', 'verification_method'):
                if not ik.get(kentta):
                    L.append(Loydos(ERROR if valmis else WARNING, 'ILMAN-KOKOUSTA-KENTTA', ptk, 'without_meeting.%s puuttuu' % kentta))
            if not (kutsu or {}).get('participation_opportunity_confirmed'):
                L.append(Loydos(ERROR, 'OSALLISTUMISMAHDOLLISUUS', ptk, 'päätös ilman kokousta edellyttää notice.participation_opportunity_confirmed: true'))
            if len(osallistuneet) < len(ent):
                L.append(Loydos(INFO, 'ILMAN-KOKOUSTA-EI-KAIKKI', ptk,
                                'kaikki jäsenet eivät osallistuneet; laki ei vaadi yksimielisyyttä mutta yhtiöjärjestys tai työjärjestys voi — tarkista (governance/03, provisional)'))

    # Päätökset
    for d in (m.get('decisions') or []):
        L += validoi_paatos(tyotila, m, d, saanto, valmis, paatokset, rajoitteet)

    # Allekirjoitus ja tarkastus
    vaad = vaaditut_allekirjoittajat(tyotila, m)
    allek = m.get('signatures') or {}
    nimetyt = list(allek.get('required_signer_person_ids') or [])
    if not nimetyt:
        L.append(Loydos(ERROR if valmis else WARNING, 'ALLEKIRJOITTAJAT-PUUTTUU', ptk,
                        'signatures.required_signer_person_ids puuttuu (malli %s: vähintään %d, mukana %s)' % (vaad['policy'], vaad['min_count'], vaad['must_include'])))
    else:
        for pid in vaad['must_include']:
            if pid not in nimetyt:
                L.append(Loydos(ERROR, 'ALLEKIRJOITTAJA-VAADITTU', ptk, '%s on allekirjoitusmallin %s mukaan pakollinen allekirjoittaja' % (pid, vaad['policy'])))
        if len(nimetyt) < vaad['min_count']:
            L.append(Loydos(ERROR, 'ALLEKIRJOITTAJIA-LIIAN-VAHAN', ptk, '%d allekirjoittajaa, malli %s vaatii %d' % (len(nimetyt), vaad['policy'], vaad['min_count'])))
        for pid in nimetyt:
            if pid not in hlot:
                L.append(Loydos(ERROR, 'HENKILO-TUNTEMATON', ptk, 'allekirjoittaja %r ei ole kokoonpanorekisterissä' % pid))
            elif pid not in las and vaad['policy'] != 'all_members_in_term':
                L.append(Loydos(WARNING, 'ALLEKIRJOITTAJA-POISSA', ptk, 'allekirjoittaja %s ei ollut läsnä — allekirjoitus ei tee hänestä osallistujaa' % pid))
    for s in (allek.get('signed') or []):
        if s.get('person_id') not in nimetyt:
            L.append(Loydos(WARNING, 'ALLEKIRJOITUS-YLIMAARAINEN', ptk, '%s on allekirjoittanut mutta ei ole vaadituissa allekirjoittajissa' % s.get('person_id')))
    for r in (m.get('reviewed_by') or []):
        if r.get('person_id') not in hlot:
            L.append(Loydos(WARNING, 'TARKASTAJA-TUNTEMATON', ptk, 'tarkastaja %r ei ole kokoonpanorekisterissä' % r.get('person_id')))

    if m.get('decision_text_status') == 'kopio':
        lahteet = {x.get('minutes_number') for x in ((tyotila_lahteet(tyotila, m)) or [])}
        if ptk not in lahteet:
            L.append(Loydos(WARNING, 'LAHDE-PUUTTUU', ptk, 'decision_text_status on kopio mutta source_documents ei nimeä alkuperäistä asiakirjaa'))

    if valmis:
        L += validoi_valmius(tyotila, m)
    return L


def tyotila_lahteet(tyotila, m):
    for _, data in tyotila['rekisterit']:
        if m in (data.get('meetings') or []):
            return ((data.get('source_documents') or {}).get('documents') or [])
    return []


def validoi_paatos(tyotila, m, d, saanto, valmis, paatokset, rajoitteet):
    L = []
    hlot = henkilot(tyotila.get('kokoonpano') or {})
    did = d.get('id') or '?'
    las = lasnaolijat(m)
    if not (d.get('title') or '').strip():
        L.append(Loydos(ERROR, 'OTSIKKO', did, 'title puuttuu'))
    if not (d.get('decision_text') or '').strip():
        L.append(Loydos(ERROR, 'PAATOSTEKSTI', did, 'decision_text puuttuu — päätös ilman tekstiä ei ole päätös'))
    if not (d.get('decision_basis') or '').strip():
        L.append(Loydos(WARNING, 'PERUSTE', did, 'decision_basis puuttuu — mihin tietoon päätös perustui (OYL 1:8 §)'))
    if m.get('decision_method') == 'without_meeting' and not (d.get('proposal') or '').strip():
        L.append(Loydos(ERROR, 'EHDOTUS', did, 'päätös ilman kokousta edellyttää kirjatun päätösehdotuksen (proposal)'))

    est = normalisoi_esteellisyys(d.get('conflict_of_interest'))
    if est is None:
        L.append(Loydos(ERROR, 'ESTEELLISYYS-PUUTTUU', did, 'conflict_of_interest puuttuu — none tarkoittaa "todettiin, ettei ollut"; tyhjä tarkoittaa "ei kysytty"'))
        est = {'status': 'none', 'disqualified_person_ids': []}
    if est.get('status') not in ('none', 'declared'):
        L.append(Loydos(ERROR, 'ESTEELLISYYS-TILA', did, 'conflict_of_interest.status oltava none tai declared'))
    if est.get('status') == 'declared' and not est.get('disqualified_person_ids'):
        L.append(Loydos(WARNING, 'ESTEELLINEN-NIMEAMATTA', did, 'esteellisyys ilmoitettu mutta disqualified_person_ids on tyhjä — kuka ei osallistunut?'))
    for pid in est.get('disqualified_person_ids') or []:
        if pid not in hlot:
            L.append(Loydos(ERROR, 'HENKILO-TUNTEMATON', did, 'esteellinen %r ei ole kokoonpanorekisterissä' % pid))
        elif pid not in las and pid not in (m.get('entitled_participants') or []):
            L.append(Loydos(WARNING, 'ESTEELLINEN-EI-JASEN', did, 'esteelliseksi merkitty %s ei ollut kokouksessa eikä toimikauden jäsen' % pid))

    joh = johda_paatoksen_paatosvaltaisuus(m, d, saanto)
    dq = d.get('decision_quorum')
    if dq:
        for kentta in ('entitled_count', 'eligible_count', 'participating_count', 'is_quorate'):
            if dq.get(kentta) is not None and dq.get(kentta) != joh[kentta]:
                L.append(Loydos(ERROR, 'PAATOS-QUORUM-RISTIRIITA', did, 'decision_quorum.%s on %r, johdettu %r' % (kentta, dq.get(kentta), joh[kentta])))
        if dq.get('participating_person_ids') is not None and set(dq['participating_person_ids']) != set(joh['participating_person_ids']):
            L.append(Loydos(ERROR, 'PAATOS-QUORUM-RISTIRIITA', did, 'decision_quorum.participating_person_ids ≠ johdettu %s' % joh['participating_person_ids']))
    if not joh['is_quorate'] and (m.get('entitled_participants') or []):
        L.append(Loydos(ERROR, 'PAATOS-EI-PAATOSVALTAINEN', did, 'asian käsittelyyn osallistui %d / %d (esteellisiä %d) — ei päätösvaltainen tässä asiassa'
                        % (joh['participating_count'], joh['entitled_count'], len(joh['disqualified_person_ids']))))

    aani = d.get('vote')
    if aani is None:
        L.append(Loydos(WARNING, 'AANESTYS-PUUTTUU', did, 'vote puuttuu — yksimielinenkin kirjataan (unanimous: true)'))
    else:
        osall = set(joh['participating_person_ids'])
        if aani.get('unanimous') is False:
            puolesta, vastaan, tyhjaa = aani.get('for'), aani.get('against'), aani.get('abstained') or 0
            if not isinstance(puolesta, int) or not isinstance(vastaan, int):
                L.append(Loydos(ERROR, 'AANESTYS-LUVUT', did, 'äänestyksessä for ja against on annettava lukuina'))
            else:
                if puolesta + vastaan + tyhjaa != len(osall):
                    L.append(Loydos(WARNING, 'AANESTYS-SUMMA', did, 'äänet %d+%d+%d ≠ osallistujat %d' % (puolesta, vastaan, tyhjaa, len(osall))))
                if puolesta == vastaan and not aani.get('chair_casting_vote'):
                    L.append(Loydos(WARNING, 'AANESTYS-TASAN', did, 'äänet tasan eikä chair_casting_vote ole true — puheenjohtajan ääni ratkaisee (OYL 6:3 §), vaaleissa arpa'))
                if vastaan > 0 and not (aani.get('dissenting_opinions') or []):
                    L.append(Loydos(INFO, 'ERIAVA-EI-KIRJATTU', did, 'vastaan-ääniä %d mutta eriävää mielipidettä ei kirjattu — jäsenellä on oikeus saada se merkityksi (OYL 6:6 §)' % vastaan))
        elif aani.get('unanimous') is not True:
            L.append(Loydos(ERROR, 'AANESTYS-TILA', did, 'vote.unanimous oltava true tai false'))
        for v in (aani.get('votes') or []):
            if v.get('person_id') not in osall:
                L.append(Loydos(ERROR, 'AANI-EI-OSALLISTUJA', did, 'ääni kirjattu henkilölle %s, joka ei osallistunut asian käsittelyyn' % v.get('person_id')))
        for e in (aani.get('dissenting_opinions') or []):
            pid = e.get('person_id') if isinstance(e, dict) else None
            if pid is None:
                L.append(Loydos(ERROR, 'ERIAVA-HENKILO', did, 'eriävä mielipide ilman person_id-kenttää'))
            elif pid not in osall and pid != toimitusjohtaja_paivana(tyotila.get('kokoonpano') or {}, m.get('decision_date')):
                L.append(Loydos(ERROR, 'ERIAVA-EI-OSALLISTUJA', did, 'eriävä mielipide henkilöltä %s, joka ei osallistunut käsittelyyn' % pid))
            if isinstance(e, dict) and not (e.get('text') or '').strip():
                L.append(Loydos(ERROR, 'ERIAVA-TEKSTI', did, 'eriävän mielipiteen teksti puuttuu'))

    if d.get('effect_status') not in VOIMASSAOLOT:
        L.append(Loydos(ERROR, 'VOIMASSAOLO', did, 'effect_status oltava %s' % '/'.join(VOIMASSAOLOT)))
    tulk = d.get('interpretation')
    if tulk is None:
        L.append(Loydos(WARNING, 'TULKINTA-PUUTTUU', did, 'interpretation-lohko puuttuu — effect_status on tulkinta ja sen vahvistus kirjataan päätöskohtaisesti'))
    else:
        if tulk.get('status') not in TULKINTATILAT:
            L.append(Loydos(ERROR, 'TULKINTA-TILA', did, 'interpretation.status oltava %s' % '/'.join(TULKINTATILAT)))
        if tulk.get('status') == 'ihmisen_vahvistama' and not (tulk.get('confirmed_by') and tulk.get('confirmed_at')):
            L.append(Loydos(ERROR, 'TULKINTA-VAHVISTAJA', did, 'ihmisen_vahvistama edellyttää confirmed_by ja confirmed_at'))
    if d.get('supersedes'):
        kohde = paatokset.get(d['supersedes'])
        if not kohde:
            L.append(Loydos(ERROR, 'VIITTAUS-PAATOS', did, 'supersedes viittaa olemattomaan päätökseen %s' % d['supersedes']))
        elif kohde[1].get('effect_status') != 'superseded':
            L.append(Loydos(WARNING, 'KORVATTU-TILA', did, '%s on korvattu tällä päätöksellä mutta sen effect_status on %r' % (d['supersedes'], kohde[1].get('effect_status'))))
    for a in (d.get('related_constraints') or []):
        if rajoitteet and a not in rajoitteet:
            L.append(Loydos(ERROR, 'VIITTAUS-RAJOITE', did, 'related_constraints viittaa olemattomaan rajoitteeseen %s' % a))
    toim = d.get('implementation') or {}
    if toim.get('status') not in (None, 'pending', 'done', 'overdue'):
        L.append(Loydos(ERROR, 'TOIMEENPANO-TILA', did, 'implementation.status oltava pending/done/overdue'))
    return L


def validoi_valmius(tyotila, m):
    """Ehdot, jotka koskevat vain valmiin (allekirjoitettavan) asiakirjan muodostamista."""
    L = []
    ptk = m.get('minutes_number') or '?'
    v = m.get('wording_confirmed_by_chair') or {}
    if v.get('confirmed') is not True:
        L.append(Loydos(ERROR, 'SANAMUOTO-VAHVISTAMATTA', ptk, 'puheenjohtaja ei ole vahvistanut sanamuotoja (wording_confirmed_by_chair.confirmed)'))
    elif not v.get('person_id'):
        L.append(Loydos(ERROR, 'SANAMUOTO-VAHVISTAJA', ptk, 'wording_confirmed_by_chair.person_id puuttuu'))
    elif v.get('person_id') != (m.get('roles') or {}).get('meeting_chair_person_id'):
        L.append(Loydos(WARNING, 'SANAMUOTO-EI-PJ', ptk, 'sanamuodon vahvisti %s, kokouksen puheenjohtaja oli %s' % (v.get('person_id'), (m.get('roles') or {}).get('meeting_chair_person_id'))))
    tila = m.get('decision_text_status')
    if tila in ('kopio', 'kopio_kuvasta'):
        L.append(Loydos(ERROR, 'ALKUPERAINEN-ON-JO', ptk, 'decision_text_status on %s — allekirjoitettu alkuperäinen on jo arkistossa; uutta valmista asiakirjaa ei muodosteta sen rinnalle' % tila))
    return L


def validoi(tyotila, kohde=None, valmis=False, skeema=True):
    L = []
    if skeema:
        L += validoi_skeemat(tyotila)
    L += validoi_kokoonpano(tyotila)
    L += validoi_tunnukset(tyotila)
    paatokset, rajoitteet = _paatokset(tyotila), _rajoitteet(tyotila)
    loytyi = False
    for _, m in kokoukset(tyotila):
        if kohde and m.get('minutes_number') != kohde:
            continue
        loytyi = True
        L += validoi_kokous(tyotila, m, valmis=valmis, paatokset=paatokset, rajoitteet=rajoitteet)
    if kohde and not loytyi:
        L.append(Loydos(ERROR, 'KOKOUS-PUUTTUU', kohde, 'kokousta ei löydy rekisteristä'))
    seur_ptk, seur_dec = seuraavat_tunnukset(tyotila)
    voim = voimassa_olevat(tyotila)
    L.append(Loydos(INFO, 'SEURAAVAT-TUNNUKSET', None, 'seuraava kokous %s, seuraava päätös %s (laskettu %d rekisteritiedostosta)'
                    % (seur_ptk, seur_dec, len(tyotila['rekisterit']))))
    L.append(Loydos(INFO, 'VOIMASSA', None, '%d voimassa olevaa päätöstä, joista %d ihmisen vahvistamaa' % (len(voim), sum(1 for x in voim if x[2]))))
    return L
