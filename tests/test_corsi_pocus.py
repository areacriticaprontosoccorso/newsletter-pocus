"""Integrazione degli avvisi corsi in newsletter_pocus: mail, Telegram, Facebook."""
import json
import unittest
from datetime import date
from unittest.mock import patch

import config as cfg
import corsi as avvisi
import newsletter_pocus as np_


def un_corso():
    return {"titolo": "Corso base di ecografia", "inizio": date(2026, 11, 14),
            "fine": date(2026, 11, 15), "ora": "9:00–17:00", "luogo": "Torino",
            "descrizione": "Parte pratica.", "posti": "", "link": "https://esempio.it/x",
            "iscrizioni_fino": None, "immagine_file": None, "immagine_url": ""}


def un_articolo():
    return {"pmid": "1", "titolo": "POCUS study", "autori": "A B", "rivista": "J",
            "data": "2026 Oct 14", "abstract": "x" * 300, "doi": "", "gruppo": "spec",
            "url": "https://pubmed.ncbi.nlm.nih.gov/1/", "tipo": "conferma",
            "sintesi_it": "Sintesi.", "rilevanza": "Rilevante.", "limite": "Limite.",
            "pubtypes": [], "pubdate_dt": None}


class MailTest(unittest.TestCase):
    def test_avviso_in_cima_prima_degli_articoli(self):
        h = np_.build_html([un_articolo()], [un_corso()])
        self.assertIn("Corso base di ecografia", h)
        self.assertLess(h.index("Corso base di ecografia"), h.index("POCUS study"))

    def test_nessun_avviso_senza_corsi(self):
        self.assertNotIn("Corso in programma", np_.build_html([un_articolo()]))
        self.assertNotIn("Corso in programma", np_.build_html([un_articolo()], []))


class TelegramTest(unittest.TestCase):
    def invia(self, corsi):
        with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "c"}), \
                patch.object(np_, "telegram_send_message", return_value=True) as m, \
                patch.object(np_.time, "sleep"):
            ok = np_.invia_telegram([un_articolo()], corsi)
        return ok, [c.args[2] for c in m.call_args_list]

    def test_messaggio_corsi_dopo_intestazione(self):
        ok, msgs = self.invia([un_corso()])
        self.assertTrue(ok)
        self.assertEqual(len(msgs), 4)                       # header + corso + articolo + footer
        self.assertIn("Corso base di ecografia", msgs[1])

    def test_senza_corsi_come_prima(self):
        ok, msgs = self.invia([])
        self.assertTrue(ok)
        self.assertEqual(len(msgs), 3)


class FacebookTest(unittest.TestCase):
    def test_un_post_programmato_per_corso(self):
        with patch.object(cfg, "FB_PAGE_ID", "1"), patch.object(cfg, "FB_PAGE_TOKEN", "t"), \
                patch.object(np_, "_fb_post", return_value={"id": "1_2"}) as m:
            self.assertTrue(np_.pubblica_facebook_corsi([un_corso()]))
        percorso, campi = m.call_args.args[:2]
        self.assertEqual(percorso, "1/feed")
        self.assertEqual(campi["published"], "false")
        self.assertEqual(campi["link"], "https://esempio.it/x")
        self.assertIn("scheduled_publish_time", campi)
        self.assertIn("Corso base di ecografia", campi["message"])

    def test_locandina_caricata_e_allegata(self):
        c = dict(un_corso(), immagine_file="/tmp/locandina.png", immagine_url="https://x/l.png")
        chiamate = []

        def finto(percorso, campi, file_path=None):
            chiamate.append((percorso, dict(campi), file_path))
            return {"id": "FOTO1" if percorso.endswith("/photos") else "1_2"}

        with patch.object(cfg, "FB_PAGE_ID", "1"), patch.object(cfg, "FB_PAGE_TOKEN", "t"), \
                patch.object(np_, "_fb_post", side_effect=finto):
            self.assertTrue(np_.pubblica_facebook_corsi([c]))
        self.assertEqual(chiamate[0][0], "1/photos")
        self.assertEqual(chiamate[0][2], "/tmp/locandina.png")
        feed = chiamate[1][1]
        self.assertEqual(json.loads(feed["attached_media[0]"]), {"media_fbid": "FOTO1"})
        self.assertNotIn("link", feed)

    def test_locandina_non_caricata_post_solo_testo(self):
        c = dict(un_corso(), immagine_file="/tmp/locandina.png", immagine_url="https://x/l.png")

        def finto(percorso, campi, file_path=None):
            if percorso.endswith("/photos"):
                raise RuntimeError("upload fallito")
            return {"id": "1_2"}

        with patch.object(cfg, "FB_PAGE_ID", "1"), patch.object(cfg, "FB_PAGE_TOKEN", "t"), \
                patch.object(np_, "_fb_post", side_effect=finto) as m:
            self.assertTrue(np_.pubblica_facebook_corsi([c]))
        feed = m.call_args.args[1]
        self.assertNotIn("attached_media[0]", feed)
        self.assertEqual(feed["link"], "https://esempio.it/x")

    def test_senza_credenziali_o_corsi_non_pubblica(self):
        with patch.object(cfg, "FB_PAGE_ID", ""), patch.object(np_, "_fb_post") as m:
            self.assertFalse(np_.pubblica_facebook_corsi([un_corso()]))
        with patch.object(cfg, "FB_PAGE_ID", "1"), patch.object(cfg, "FB_PAGE_TOKEN", "t"), \
                patch.object(np_, "_fb_post") as m:
            self.assertFalse(np_.pubblica_facebook_corsi([]))
            m.assert_not_called()

    def test_errore_facebook_non_solleva(self):
        with patch.object(cfg, "FB_PAGE_ID", "1"), patch.object(cfg, "FB_PAGE_TOKEN", "t"), \
                patch.object(np_, "_fb_post", side_effect=RuntimeError("boom")):
            self.assertFalse(np_.pubblica_facebook_corsi([un_corso()]))

    def test_slot_nel_futuro_in_giorni_feriali(self):
        slot = np_.prossimi_slot_corsi(3)
        self.assertEqual(len(slot), 3)
        self.assertTrue(all(s.weekday() in cfg.FB_GIORNI_FERIALI for s in slot))
        self.assertTrue(all((s.hour, s.minute) == (cfg.FB_ORA_CORSI, cfg.FB_MINUTO_CORSI) for s in slot))


if __name__ == "__main__":
    unittest.main()
