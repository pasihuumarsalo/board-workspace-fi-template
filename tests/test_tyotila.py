# -*- coding: utf-8 -*-
"""Työtilan sääntötestit. Ajo:  python -m unittest discover -s tests -v

Kattaa kehitysarvion 15 skenaariota: tavallinen kokous, kokous ilman päätöksiä,
monipäiväinen kokous, yksijäseninen hallitus, varajäsen sijaisena, päätöskohtainen
esteellisyys, esteellisyyden vuoksi päätösvallaton asia, äänestys ja eriävä
mielipide, päätös ilman kokousta, puuttuva allekirjoittaja, päällekkäinen tunnus,
ristiriitainen kokoonpano, valmiin asiakirjan estäminen, päätöksen korvaaminen ja
katkennut viittaus. Lisäksi MALLI-tilikausi.yaml tarkistetaan mallikokoonpanoa
vasten, ja generaattori ajetaan väliaikaisessa työtilassa.
"""
import copy
import io
import os
import shutil
import sys
import tempfile
import unittest

JUURI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(JUURI, 'scripts'))
sys.path.insert(0, os.path.join(JUURI, 'templates'))
import tyotila as T  # noqa: E402

PJ, J2, J3, VJ = 'matti-meikalainen', 'maija-mallikas', 'kalle-kokeilija', 'varpu-varajasen'


def kokoonpano(jasenet=(PJ, J2, J3), pj=PJ, varajasenet=(VJ,), allekirjoitus='chair_plus_one', saanto=None):
    def j(pid, rooli):
        return {'person_id': pid, 'display_name': pid.replace('-', ' ').title(), 'board_role': rooli,
                'valid_from': '2026-01-01', 'valid_until': None, 'decision_right': rooli != 'deputy'}
    members = [j(p, 'chair' if p == pj else 'member') for p in jasenet] + [j(v, 'deputy') for v in varajasenet]
    return {'schema_version': 2, 'record_type': 'board_composition_register',
            'terms': [{'term_id': 'T-0001', 'valid_from': '2026-01-01', 'valid_until': None, 'status': 'confirmed', 'members': members}],
            'ceo': {'person_id': 'tiina-toimari', 'display_name': 'Tiina Toimari', 'valid_from': '2026-01-01', 'valid_until': None},
            'quorum_rule': saanto or {'type': 'more_than_half', 'source': 'OYL 6:3 §'},
            'signature_policy': {'required_signers': allekirjoitus, 'includes_absent_members': False}}


def paatos(did='DEC-000001', **k):
    d = {'id': did, 'title': 'Asia', 'decision_text': 'Päätettiin jotakin täsmällistä.', 'decision_basis': 'Esitys.',
         'conflict_of_interest': 'none', 'vote': {'unanimous': True}, 'effect_status': 'in_force',
         'interpretation': {'status': 'ai_tulkinta'}}
    d.update(k)
    return d


def kokous(ptk='PTK-000001', lasna=(PJ, J2, J3), oikeutetut=(PJ, J2, J3), pj=PJ, paatokset=None, **k):
    m = {'minutes_number': ptk, 'decision_date': '2026-05-14', 'title': 'Hallituksen kokous', 'place': 'Toimisto',
         'decision_method': 'meeting', 'roles': {'meeting_chair_person_id': pj, 'secretary_person_id': None, 'ceo_participation': 'present'},
         'participants': list(lasna), 'entitled_participants': list(oikeutetut), 'deputy_substitutions': [],
         'notice': {'sent_at': '2026-05-06', 'sent_by': pj, 'invited_person_ids': list(oikeutetut), 'participation_opportunity_confirmed': True},
         'session': {'opened_at': '2026-05-14 09:00', 'closed_at': '2026-05-14 11:00'},
         'wording_confirmed_by_chair': {'confirmed': True, 'person_id': pj, 'confirmed_at': '2026-05-15'},
         'signatures': {'required_signer_person_ids': [pj, J2] if J2 in lasna else [pj] + [p for p in lasna if p != pj][:1]},
         'decision_text_status': 'odottaa_allekirjoitusta', 'items_without_decision': [],
         'decisions': [paatos()] if paatokset is None else paatokset}
    m.update(k)
    return m


def tyotila(kokoukset, kok=None, rajat=None):
    return {'juuri': JUURI, 'yhtio': {'id_prefix': {'minutes': 'PTK-', 'decision': 'DEC-'}}, 'kokoonpano': kok or kokoonpano(),
            'rajat': rajat or {}, 'vuosikello': {},
            'rekisterit': [('decisions/2026.yaml', {'schema_version': 2, 'record_type': 'board_decision_register',
                                                    'fiscal_year': '2026', 'meetings': list(kokoukset)})]}


def koodit(loydokset, taso=None):
    return {l.koodi for l in loydokset if taso is None or l.taso == taso}


class Saannot(unittest.TestCase):

    def test_01_tavallinen_paatosvaltainen_kokous(self):
        L = T.validoi(tyotila([kokous()]), valmis=True, skeema=False)
        self.assertEqual(T.virheet(L), [], [str(l) for l in T.virheet(L)])

    def test_02_kokous_ilman_paatoksia(self):
        m = kokous(paatokset=[], items_without_decision=['Strategiakeskustelu, ei päätöstä.'])
        L = T.validoi(tyotila([m]), skeema=False)
        self.assertEqual(T.virheet(L), [])
        # ei-päätösvaltainen kokous ilman päätöksiä on tieto, ei virhe
        m2 = kokous(lasna=(PJ,), paatokset=[])
        L2 = T.validoi(tyotila([m2]), skeema=False)
        self.assertIn('EI-PAATOSVALTAINEN', koodit(L2, T.INFO))
        self.assertNotIn('EI-PAATOSVALTAINEN', koodit(L2, T.ERROR))

    def test_03_monipaivainen_kokous(self):
        m = kokous(decision_date='2026-09-19', session={'opened_at': '2026-09-17 16:00', 'closed_at': '2026-09-19 12:00'})
        L = T.validoi(tyotila([m]), skeema=False)
        self.assertEqual(T.virheet(L), [])
        self.assertNotIn('PAIVA-ISTUNTO', koodit(L))
        m['decision_date'] = '2026-09-17'
        self.assertIn('PAIVA-ISTUNTO', koodit(T.validoi(tyotila([m]), skeema=False), T.WARNING))

    def test_04_yksijaseninen_hallitus(self):
        kok = kokoonpano(jasenet=(PJ,), varajasenet=())
        m = kokous(lasna=(PJ,), oikeutetut=(PJ,), signatures={'required_signer_person_ids': [PJ]})
        L = T.validoi(tyotila([m], kok), valmis=True, skeema=False)
        self.assertEqual(T.virheet(L), [], [str(l) for l in T.virheet(L)])
        self.assertEqual(T.vaaditut_allekirjoittajat(tyotila([m], kok), m)['min_count'], 1)

    def test_05_varajasen_sijaisena(self):
        m = kokous(lasna=(PJ, J2), deputy_substitutions=[{'deputy_person_id': VJ, 'for_person_id': J3}])
        ty = tyotila([m])
        q = T.johda_kokouksen_paatosvaltaisuus(m, T.paatosvaltaisuussaanto(ty['kokoonpano']))
        self.assertEqual((q['present_count'], q['entitled_count'], q['is_quorate']), (3, 3, True))
        self.assertEqual(T.poissaolijat(m), [])
        self.assertEqual(T.virheet(T.validoi(ty, skeema=False)), [])
        # sijaistettu ei voi olla samaan aikaan läsnä
        m2 = kokous(deputy_substitutions=[{'deputy_person_id': VJ, 'for_person_id': J3}])
        self.assertIn('SIJAINEN-JA-JASEN', koodit(T.validoi(tyotila([m2]), skeema=False), T.ERROR))

    def test_06_paatoskohtainen_esteellisyys(self):
        d = paatos(conflict_of_interest={'status': 'declared', 'disqualified_person_ids': [J2], 'left_room': True})
        m = kokous(paatokset=[d])
        ty = tyotila([m])
        q = T.johda_paatoksen_paatosvaltaisuus(m, d, T.paatosvaltaisuussaanto(ty['kokoonpano']))
        self.assertEqual(q['participating_person_ids'], [PJ, J3])
        self.assertEqual((q['eligible_count'], q['participating_count'], q['is_quorate']), (2, 2, True))
        self.assertEqual(T.virheet(T.validoi(ty, skeema=False)), [])
        # kirjoitettu decision_quorum, joka ei täsmää, on virhe
        d['decision_quorum'] = {'participating_count': 3, 'is_quorate': True}
        self.assertIn('PAATOS-QUORUM-RISTIRIITA', koodit(T.validoi(tyotila([m]), skeema=False), T.ERROR))

    def test_07_esteellisyys_vie_paatosvaltaisuuden(self):
        # 3 jäsentä, läsnä 2, joista yksi esteellinen -> osallistuu 1/3 -> ei päätösvaltainen tässä asiassa
        d = paatos(conflict_of_interest={'status': 'declared', 'disqualified_person_ids': [J2]})
        m = kokous(lasna=(PJ, J2), paatokset=[d])
        L = T.validoi(tyotila([m]), skeema=False)
        self.assertIn('PAATOS-EI-PAATOSVALTAINEN', koodit(L, T.ERROR))
        self.assertNotIn('EI-PAATOSVALTAINEN', koodit(L, T.ERROR))  # kokoustasolla 2/3 riittää

    def test_08_aanestys_ja_eriava_mielipide(self):
        d = paatos(vote={'unanimous': False, 'for': 2, 'against': 1,
                         'dissenting_opinions': [{'person_id': J3, 'text': 'Eriävä.'}]})
        L = T.validoi(tyotila([kokous(paatokset=[d])]), skeema=False)
        self.assertEqual(T.virheet(L), [])
        # tasan ilman puheenjohtajan ääntä -> varoitus; eriävä ei-osallistujalta -> virhe
        d2 = paatos(vote={'unanimous': False, 'for': 1, 'against': 1, 'abstained': 1,
                          'dissenting_opinions': [{'person_id': VJ, 'text': 'x'}]})
        L2 = T.validoi(tyotila([kokous(paatokset=[d2])]), skeema=False)
        self.assertIn('AANESTYS-TASAN', koodit(L2, T.WARNING))
        self.assertIn('ERIAVA-EI-OSALLISTUJA', koodit(L2, T.ERROR))
        d3 = paatos(vote={'unanimous': False})
        self.assertIn('AANESTYS-LUVUT', koodit(T.validoi(tyotila([kokous(paatokset=[d3])]), skeema=False), T.ERROR))

    def test_09_paatos_ilman_kokousta(self):
        vast = [{'person_id': p, 'position': 'for'} for p in (PJ, J2, J3)]
        m = kokous(decision_method='without_meeting', place=None, session=None,
                   without_meeting={'proposal_sent_at': '2026-05-10 12:00', 'response_deadline': '2026-05-14 16:00',
                                    'verification_method': 'sähköinen allekirjoitus', 'responses': vast},
                   paatokset=[paatos(proposal='Ehdotus.')])
        L = T.validoi(tyotila([m]), valmis=True, skeema=False)
        self.assertEqual(T.virheet(L), [], [str(l) for l in T.virheet(L)])
        # istuntoaika kokouksettomalle -> virhe; vastaamatta jäänyt jäsen ilman merkintää -> virhe; ehdotus puuttuu -> virhe
        m2 = copy.deepcopy(m); m2['session'] = {'opened_at': '2026-05-14 09:00', 'closed_at': '2026-05-14 10:00'}
        self.assertIn('ISTUNTO-ILMAN-KOKOUSTA', koodit(T.validoi(tyotila([m2]), skeema=False), T.ERROR))
        m3 = copy.deepcopy(m); m3['without_meeting']['responses'] = vast[:2]; m3['participants'] = [PJ, J2]
        self.assertIn('OSALLISTUMISMAHDOLLISUUS', koodit(T.validoi(tyotila([m3]), skeema=False), T.ERROR))
        m4 = copy.deepcopy(m); m4['decisions'][0]['proposal'] = None
        self.assertIn('EHDOTUS', koodit(T.validoi(tyotila([m4]), skeema=False), T.ERROR))
        # no_response on kelvollinen merkintä: tilaisuus varattiin, jäsen ei vastannut
        m5 = copy.deepcopy(m); m5['without_meeting']['responses'][2] = {'person_id': J3, 'position': 'no_response'}; m5['participants'] = [PJ, J2]
        L5 = T.validoi(tyotila([m5]), skeema=False)
        self.assertEqual(T.virheet(L5), [], [str(l) for l in T.virheet(L5)])
        self.assertIn('ILMAN-KOKOUSTA-EI-KAIKKI', koodit(L5, T.INFO))

    def test_10_puuttuva_allekirjoittaja(self):
        m = kokous(signatures={'required_signer_person_ids': [J2]})   # puheenjohtaja puuttuu
        self.assertIn('ALLEKIRJOITTAJA-VAADITTU', koodit(T.validoi(tyotila([m]), skeema=False), T.ERROR))
        m2 = kokous(signatures={'required_signer_person_ids': [PJ]})  # vain yksi, hallituksessa useita
        self.assertIn('ALLEKIRJOITTAJIA-LIIAN-VAHAN', koodit(T.validoi(tyotila([m2]), skeema=False), T.ERROR))
        m3 = kokous(signatures={})
        L3 = T.validoi(tyotila([m3]), skeema=False)
        self.assertIn('ALLEKIRJOITTAJAT-PUUTTUU', koodit(L3, T.WARNING))
        self.assertIn('ALLEKIRJOITTAJAT-PUUTTUU', koodit(T.validoi(tyotila([m3]), valmis=True, skeema=False), T.ERROR))
        # poissa ollut allekirjoittajana: varoitus, ei osallistuja
        m4 = kokous(lasna=(PJ, J2), signatures={'required_signer_person_ids': [PJ, J3]})
        self.assertIn('ALLEKIRJOITTAJA-POISSA', koodit(T.validoi(tyotila([m4]), skeema=False), T.WARNING))

    def test_11_paallekkainen_ja_aukollinen_tunnus(self):
        m1, m2 = kokous('PTK-000001'), kokous('PTK-000001', paatokset=[paatos('DEC-000001')])
        L = T.validoi(tyotila([m1, m2]), skeema=False)
        self.assertIn('TUNNUS-KAHDESTI', koodit(L, T.ERROR))
        m3 = kokous('PTK-000003', paatokset=[paatos('DEC-000003')])
        L2 = T.validoi(tyotila([m1, m3]), skeema=False)
        self.assertIn('TUNNUS-AUKKO', koodit(L2, T.ERROR))
        self.assertEqual(T.seuraavat_tunnukset(tyotila([m1, m3])), ('PTK-000004', 'DEC-000004'))

    def test_12_ristiriitainen_kokoonpano(self):
        kok = kokoonpano()
        kok['terms'].append({'term_id': 'T-0002', 'valid_from': '2025-12-01', 'valid_until': None, 'members': []})
        L = T.validoi(tyotila([kokous()], kok), skeema=False)
        self.assertTrue({'KAUSI-PAALLEKKAIN', 'KAUSI-USEA-AVOIN'} & koodit(L, T.ERROR))
        # entitled_participants poikkeaa rekisteristä -> varoitus
        m = kokous(oikeutetut=(PJ, J2), lasna=(PJ, J2))
        self.assertIn('KOKOONPANO-ERO', koodit(T.validoi(tyotila([m]), skeema=False), T.WARNING))
        # läsnäolija, jolla ei ole oikeutta -> virhe
        m2 = kokous(lasna=(PJ, J2, VJ))
        self.assertIn('OSALLISTUJA-EI-OIKEUTTA', koodit(T.validoi(tyotila([m2]), skeema=False), T.ERROR))

    def test_13_valmiin_asiakirjan_esto(self):
        m = kokous(wording_confirmed_by_chair={'confirmed': False})
        L = T.validoi(tyotila([m]), valmis=True, skeema=False)
        self.assertIn('SANAMUOTO-VAHVISTAMATTA', koodit(L, T.ERROR))
        self.assertEqual(T.virheet(T.validoi(tyotila([m]), valmis=False, skeema=False)), [])
        m2 = kokous(decision_text_status='kopio')
        self.assertIn('ALKUPERAINEN-ON-JO', koodit(T.validoi(tyotila([m2]), valmis=True, skeema=False), T.ERROR))
        m3 = kokous(notice=None)
        self.assertIn('KUTSU-PUUTTUU', koodit(T.validoi(tyotila([m3]), valmis=True, skeema=False), T.ERROR))
        self.assertIn('KUTSU-PUUTTUU', koodit(T.validoi(tyotila([m3]), valmis=False, skeema=False), T.WARNING))
        # quorum kirjoitettu käsin väärin -> virhe aina
        m4 = kokous(lasna=(PJ,), quorum={'entitled_count': 3, 'present_count': 3, 'is_quorate': True})
        self.assertIn('QUORUM-RISTIRIITA', koodit(T.validoi(tyotila([m4]), skeema=False), T.ERROR))

    def test_14_paatoksen_korvaaminen(self):
        m1 = kokous('PTK-000001', paatokset=[paatos('DEC-000001', effect_status='superseded')])
        m2 = kokous('PTK-000002', paatokset=[paatos('DEC-000002', supersedes='DEC-000001')])
        L = T.validoi(tyotila([m1, m2]), skeema=False)
        self.assertEqual(T.virheet(L), [])
        self.assertNotIn('KORVATTU-TILA', koodit(L))
        m1['decisions'][0]['effect_status'] = 'in_force'
        self.assertIn('KORVATTU-TILA', koodit(T.validoi(tyotila([m1, m2]), skeema=False), T.WARNING))
        self.assertEqual(len(T.voimassa_olevat(tyotila([m1, m2]))), 2)

    def test_15_katkennut_viittaus(self):
        m = kokous(paatokset=[paatos(supersedes='DEC-000099', related_constraints=['AUTH-404'])])
        rajat = {'constraints': [{'id': 'AUTH-001'}]}
        L = T.validoi(tyotila([m], rajat=rajat), skeema=False)
        self.assertIn('VIITTAUS-PAATOS', koodit(L, T.ERROR))
        self.assertIn('VIITTAUS-RAJOITE', koodit(L, T.ERROR))
        m2 = kokous(lasna=(PJ, 'tuntematon-henkilo', J3), oikeutetut=(PJ, 'tuntematon-henkilo', J3))
        self.assertIn('HENKILO-TUNTEMATON', koodit(T.validoi(tyotila([m2]), skeema=False), T.ERROR))

    def test_16_esteellisyys_puuttuu_on_eri_kuin_none(self):
        d = paatos(); del d['conflict_of_interest']
        self.assertIn('ESTEELLISYYS-PUUTTUU', koodit(T.validoi(tyotila([kokous(paatokset=[d])]), skeema=False), T.ERROR))
        self.assertEqual(T.normalisoi_esteellisyys('none')['status'], 'none')
        self.assertEqual(T.normalisoi_esteellisyys({'status': 'declared', 'disqualified_person_ids': [J2]})['disqualified_person_ids'], [J2])

    def test_17_yhtiojarjestyksen_tiukempi_saanto(self):
        kok = kokoonpano(saanto={'type': 'min_count', 'min_count': 3, 'source': 'Yhtiöjärjestys 7 §'})
        m = kokous(lasna=(PJ, J2))
        self.assertIn('EI-PAATOSVALTAINEN', koodit(T.validoi(tyotila([m], kok), skeema=False), T.ERROR))
        self.assertTrue(T.on_paatosvaltainen(3, 2, {'type': 'more_than_half'}))
        self.assertFalse(T.on_paatosvaltainen(4, 2, {'type': 'more_than_half'}))
        self.assertFalse(T.on_paatosvaltainen(3, 2, {'type': 'fraction', 'numerator': 2, 'denominator': 3}) is False and False)
        self.assertTrue(T.on_paatosvaltainen(3, 2, {'type': 'fraction', 'numerator': 2, 'denominator': 3}))
        self.assertFalse(T.on_paatosvaltainen(4, 2, {'type': 'fraction', 'numerator': 2, 'denominator': 3}))


class Malli(unittest.TestCase):
    """decisions/MALLI-tilikausi.yaml on itse kelvollinen esimerkki."""

    def test_malli_validoituu_skeemaa_ja_saantoja_vasten(self):
        data = T.lataa_yaml(os.path.join(JUURI, 'decisions', 'MALLI-tilikausi.yaml'))
        ty = tyotila([], kok=kokoonpano())
        ty['rekisterit'] = [('decisions/MALLI-tilikausi.yaml', data)]
        ty['yhtio'] = T.lataa_yaml(os.path.join(JUURI, 'company', 'yhtio.yaml'))
        ty['kokoonpano'].update({k: v for k, v in T.lataa_yaml(os.path.join(JUURI, 'company', 'hallituksen-kokoonpano.yaml')).items()
                                 if k in ('quorum_rule', 'signature_policy', 'review_policy', 'secretary')})
        L = T.validoi(ty)
        self.assertEqual(T.virheet(L), [], [str(l) for l in T.virheet(L)])
        self.assertEqual(T.seuraavat_tunnukset(ty), ('PTK-000003', 'DEC-000004'))

    def test_pohjatiedostot_validoituvat_skeemoja_vasten(self):
        ty = T.lataa_tyotila(JUURI)
        L = T.validoi_skeemat(ty)
        self.assertEqual(T.virheet(L), [], [str(l) for l in T.virheet(L)])


class Generaattori(unittest.TestCase):
    """Generaattori väliaikaisessa työtilassa: osallistujat rekisteristä, kieltäytyy valmiista virheillä."""

    def setUp(self):
        import yaml
        self.tmp = tempfile.mkdtemp(prefix='tyotila-')
        for kansio in ('company', 'decisions', 'templates'):
            os.makedirs(os.path.join(self.tmp, kansio))
        for f in ('poytakirjapohja.docx', 'paatospohja-ilman-kokousta.docx'):
            shutil.copy(os.path.join(JUURI, 'templates', f), os.path.join(self.tmp, 'templates', f))
        self.kok = kokoonpano()
        d = paatos(conflict_of_interest={'status': 'declared', 'disqualified_person_ids': [J3], 'left_room': True},
                   vote={'unanimous': False, 'for': 1, 'against': 1, 'chair_casting_vote': True,
                         'dissenting_opinions': [{'person_id': J2, 'text': 'Eri mieltä hinnasta.'}]})
        m = kokous(lasna=(PJ, J2, J3), paatokset=[d, paatos('DEC-000002')], items_without_decision=['Siirrettiin asia X.'],
                   invited_participants=[{'display_name': None, 'role': 'tilintarkastaja', 'items': '4 §'}])
        vast = [{'person_id': p, 'position': 'for'} for p in (PJ, J2, J3)]
        m2 = kokous('PTK-000002', decision_method='without_meeting', place=None, session=None, decision_date='2026-06-02',
                    without_meeting={'proposal_sent_at': '2026-05-29 14:00', 'response_deadline': '2026-06-02 16:00',
                                     'verification_method': 'sähköinen allekirjoitus', 'responses': vast},
                    paatokset=[paatos('DEC-000003', proposal='Avataan tili.')])
        m3 = kokous('PTK-000003', decision_date='2026-06-10', wording_confirmed_by_chair={'confirmed': False},
                    paatokset=[paatos('DEC-000004')])
        with io.open(os.path.join(self.tmp, 'company', 'hallituksen-kokoonpano.yaml'), 'w', encoding='utf-8') as f:
            yaml.safe_dump(self.kok, f, allow_unicode=True)
        with io.open(os.path.join(self.tmp, 'company', 'yhtio.yaml'), 'w', encoding='utf-8') as f:
            yaml.safe_dump({'schema_version': 1, 'record_type': 'company', 'id_prefix': {'minutes': 'PTK-', 'decision': 'DEC-'}}, f)
        with io.open(os.path.join(self.tmp, 'decisions', '2026.yaml'), 'w', encoding='utf-8') as f:
            yaml.safe_dump({'schema_version': 2, 'record_type': 'board_decision_register', 'fiscal_year': '2026',
                            'meetings': [m, m2, m3]}, f, allow_unicode=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _teksti(self, polku):
        import docx
        d = docx.Document(polku)
        return '\n'.join(p.text for p in d.paragraphs)

    def test_luonnos_ja_valmis_kokouksesta(self):
        import importlib
        G = importlib.import_module('tee-poytakirja')
        G.POHJAT = {'meeting': os.path.join(self.tmp, 'templates', 'poytakirjapohja.docx'),
                    'without_meeting': os.path.join(self.tmp, 'templates', 'paatospohja-ilman-kokousta.docx')}
        ulos, L = G.muodosta('PTK-000001', os.path.join(self.tmp, 'ptk1.docx'), valmis=True, juuri=self.tmp, tulosta=lambda *a: None)
        t = self._teksti(ulos)
        self.assertNotIn('LUONNOS', t)
        self.assertNotIn('[Etunimi Sukunimi]', t)
        self.assertNotIn('[Allekirjoittaja]', t)
        self.assertIn('Matti Meikalainen\tpuheenjohtaja', t)
        self.assertIn('Maija Mallikas\tjäsen', t)
        self.assertIn('Tiina Toimari\ttoimitusjohtaja', t)
        self.assertIn('tilintarkastaja (4 §)', t)
        self.assertIn('paikalla oli 3 hallituksen 3 jäsenestä', t)
        self.assertIn('Esteellisyys: Kalle Kokeilija ilmoitti esteellisyydestään', t)
        self.assertIn('Äänestys: puolesta 1, vastaan 1.', t)
        self.assertIn('Eriävä mielipide (Maija Mallikas)', t)
        self.assertIn('Kokous numero 1', t)
        self.assertIn('Käsitellyt asiat, joista ei tehty päätöstä', t)
        self.assertNotIn('[Poissa]', t)
        # allekirjoittajat rekisteristä
        self.assertIn('Allekirjoitukset\t\tMatti Meikalainen\tpuheenjohtaja', t)

    def test_paatos_ilman_kokousta_omalle_pohjalle(self):
        import importlib
        G = importlib.import_module('tee-poytakirja')
        G.POHJAT = {'meeting': os.path.join(self.tmp, 'templates', 'poytakirjapohja.docx'),
                    'without_meeting': os.path.join(self.tmp, 'templates', 'paatospohja-ilman-kokousta.docx')}
        ulos, L = G.muodosta('PTK-000002', os.path.join(self.tmp, 'ptk2.docx'), valmis=True, juuri=self.tmp, tulosta=lambda *a: None)
        t = self._teksti(ulos)
        self.assertIn('Päätös ilman kokousta, numero 2', t)
        self.assertNotIn('avasi kokouksen', t)
        self.assertIn('29.5.2026 klo 14:00', t)
        self.assertIn('Päätösehdotus: Avataan tili.', t)
        self.assertIn('sähköinen allekirjoitus', t)

    def test_valmis_kieltaytyy_virheilla_mutta_luonnos_syntyy(self):
        import importlib
        G = importlib.import_module('tee-poytakirja')
        G.POHJAT = {'meeting': os.path.join(self.tmp, 'templates', 'poytakirjapohja.docx'),
                    'without_meeting': os.path.join(self.tmp, 'templates', 'paatospohja-ilman-kokousta.docx')}
        ulos = os.path.join(self.tmp, 'ptk3.docx')
        with self.assertRaises(G.Kieltaytyi):
            G.muodosta('PTK-000003', ulos, valmis=True, juuri=self.tmp, tulosta=lambda *a: None)
        self.assertFalse(os.path.exists(ulos))
        polku, L = G.muodosta('PTK-000003', ulos, valmis=False, juuri=self.tmp, tulosta=lambda *a: None)
        t = self._teksti(polku)
        self.assertIn('LUONNOS', t)
        self.assertIn('estävää virhettä', t)


class Sisaltotarkistus(unittest.TestCase):

    def test_hetu_tunnistus_kattaa_uudet_vuosisatamerkit(self):
        import importlib
        S = importlib.import_module('tarkista-sisalto')
        # Esimerkit kokoonpannaan ajon aikana, jotta repon tekstissä ei ole hetun näköistä merkkijonoa.
        def hetu(pp, merkki, nnn, tarkistus=None):
            t = tarkistus if tarkistus is not None else S.TARKISTUSMERKIT[int(pp + nnn) % 31]
            return pp + merkki + nnn + t
        oikea_vanha = hetu('131052', '-', '308')
        oikea_uusi = hetu('010594', 'Y', '902')
        vaara_tarkistus = hetu('010594', 'Y', '902', tarkistus='A' if oikea_uusi[-1] != 'A' else 'B')
        mahdoton_paiva = hetu('320190', '-', '123')
        for teksti, odotettu in ((oikea_vanha, True), (oikea_uusi, True), (vaara_tarkistus, False),
                                 (mahdoton_paiva, None), ('2026-05-14 09:00', 'ei osumaa'), ('PTK-000073', 'ei osumaa'),
                                 ('puh. 040 123 4567', 'ei osumaa')):
            m = S.HETU.search(teksti)
            if odotettu == 'ei osumaa':
                self.assertIsNone(m, teksti)
            else:
                self.assertIsNotNone(m, teksti)
                self.assertEqual(S.on_hetu(m), odotettu, teksti)
        self.assertEqual(S.tarkista_teksti('hetu ' + oikea_vanha, 'x.md', []), 1)
        self.assertEqual(S.tarkista_teksti('hetu ' + vaara_tarkistus, 'x.md', []), 1)   # HETU? estää myös
        self.assertEqual(S.tarkista_teksti('muoto PPKKVV-NNNT', 'x.md', []), 0)
        self.assertEqual(S.tarkista_teksti('kokous 14.5.2026 klo 09:00, PTK-000073', 'x.md', []), 0)

    def test_salaisuudet_ja_word(self):
        import importlib
        S = importlib.import_module('tarkista-sisalto')
        salasanarivi = 'pass' + 'word: ' + "'" + 'hunter2' * 2 + "'"
        avainrivi = '-----BEGIN RSA ' + 'PRIVATE ' + 'KEY-----'
        self.assertEqual(S.tarkista_teksti(salasanarivi, 'x.yaml', []), 1)
        self.assertEqual(S.tarkista_teksti(avainrivi, 'x.txt', []), 1)
        self.assertEqual(S.tarkista_teksti('token: null', 'x.yaml', []), 0)
        teksti = S.word_teksti(os.path.join(JUURI, 'templates', 'poytakirjapohja.docx'))
        self.assertIn('Kokous numero', teksti)
        self.assertIn('Hallituksen kokouksen pöytäkirja', teksti)   # ylätunniste tarkistetaan

if __name__ == '__main__':
    unittest.main()
