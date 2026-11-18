"""Podcast POCUS: allegato alla mail degli iscritti (con le schede), Reel, mai bloccante."""
import contextlib
import email
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)
import config as cfg  # noqa: E402
import newsletter_pocus as nl  # noqa: E402

ART = [{"pmid": "1", "titolo": "T", "titolo_it": "Titolo", "rivista": "Ultrasound J", "sintesi_it": "S",
        "rilevanza": "R", "limite": "L", "link": "https://pubmed.ncbi.nlm.nih.gov/1/", "data": "2026-11-01",
        "url": "https://pubmed.ncbi.nlm.nih.gov/1/", "autori": "Rossi M", "abstract": "A", "gruppo": "A"}]
WL = {"settimana": 47, "anno": 2026, "giorno": 18, "mese": "Novembre"}


def _file(d, nome, byte):
    p = os.path.join(d, nome)
    with open(p, "wb") as f:
        f.write(b"x" * byte)
    return p


class Config(unittest.TestCase):
    def test_blocco_podcast(self):
        self.assertEqual(cfg.PODCAST_TITOLO, "POCUS Weekly Digest")
        self.assertEqual(cfg.PODCAST_CORSI, "pocus")
        self.assertIn("ecografia clinica", cfg.PODCAST_INTRO)
        self.assertNotIn("due minuti", cfg.PODCAST_INTRO)       # 1-5 articoli: la durata cambia
        self.assertIn("{blocchi}", cfg.PODCAST_PROMPT)
        self.assertIn("ecografia", cfg.PODCAST_PROMPT)
        self.assertNotIn("ventilazione non invasiva e l'insufficienza", cfg.PODCAST_PROMPT)
        self.assertFalse(cfg.PODCAST_RIPIEGO_CHATTERBOX)
        self.assertIn("completo", cfg.YT_TITOLI)

    def test_podcast_py_usa_il_modulo_pocus(self):
        import podcast
        self.assertIs(podcast.nr, nl)
        testo, _, _ = podcast.chiusura_podcast(True)
        self.assertTrue(testo.endswith("Alla prossima."))

    def test_un_solo_articolo_al_singolare(self):
        import podcast
        self.assertIn("Un articolo,", podcast.intro(1))
        self.assertNotIn("Uno articoli", podcast.intro(1))
        self.assertIn("Tre articoli,", podcast.intro(3))
        self.assertEqual(podcast.limiti_parole(1)[1], round(cfg.PODCAST_PAROLE_MAX / cfg.ARTICOLI_FINALI))


class Mail(unittest.TestCase):
    def _spedita(self, allegati=None, media=None):
        with mock.patch("smtplib.SMTP_SSL") as smtp:
            ok = nl.invia_email("Oggetto", "<p>ciao</p>", ["a@example.org"], allegati=allegati, media=media)
        self.assertTrue(ok)
        return email.message_from_bytes(
            smtp.return_value.__enter__.return_value.send_message.call_args[0][0].as_bytes())

    def test_senza_podcast_come_prima(self):
        msg = self._spedita()
        self.assertEqual([p.get_content_type() for p in msg.get_payload()], ["multipart/alternative"])

    def test_schede_e_video_insieme(self):
        with tempfile.TemporaryDirectory() as d:
            png = _file(d, "digest-s47-01.png", 50)
            mp4 = _file(d, "podcast-s47-2026.mp4", 112)
            msg = self._spedita([png], mp4)
        tipi = [p.get_content_type() for p in msg.get_payload()]
        self.assertEqual(tipi, ["multipart/alternative", "image/png", "video/mp4"])
        self.assertEqual(msg.get_payload()[2].get_filename(), "podcast-s47-2026.mp4")
        self.assertEqual(len(msg.get_payload()[2].get_payload(decode=True)), 112)

    def test_file_mancante_la_mail_parte_senza(self):
        msg = self._spedita(media="/non/esiste.mp4")
        self.assertEqual([p.get_content_type() for p in msg.get_payload()], ["multipart/alternative"])

    def test_riga_nella_mail_solo_con_il_podcast(self):
        with mock.patch.object(nl, "numero_settimana", return_value=WL):
            self.assertNotIn(">Podcast<", nl.build_html(ART))
            h = nl.build_html(ART, podcast_allegato="podcast/podcast-s47-2026.mp4")
        self.assertIn(">Podcast<", h)
        self.assertIn("un articolo da ascoltare", h)
        self.assertIn("il video è in allegato", h)
        self.assertIn("podcast-s47-2026.mp4", h)


class Allegato(unittest.TestCase):
    def test_preferisce_il_video_e_rispetta_i_limiti(self):
        with tempfile.TemporaryDirectory() as d:
            mp4, mp3 = _file(d, "a.mp4", 2_000_000), _file(d, "a.mp3", 500_000)
            podcast = {"mp4": mp4, "mp3": mp3}
            self.assertEqual(nl.allegato_podcast(podcast), mp4)
            with mock.patch.object(cfg, "MAIL_MAX_MB", 1):            # video troppo grande: l'MP3
                self.assertEqual(nl.allegato_podcast(podcast), mp3)
            with mock.patch.object(cfg, "MAIL_TOTALE_MAX_MB", 2.2):   # schede + video oltre il totale
                self.assertEqual(nl.allegato_podcast(podcast, altri_mb=1.0), mp3)
            with mock.patch.object(cfg, "MAIL_TOTALE_MAX_MB", 1):
                self.assertIsNone(nl.allegato_podcast(podcast, altri_mb=1.0))
            self.assertIsNone(nl.allegato_podcast(None))


class Genera(unittest.TestCase):
    def test_spento_o_senza_chiave_niente_podcast(self):
        with mock.patch.object(cfg, "PODCAST_ABILITATO", False):
            self.assertIsNone(nl.genera_podcast(ART, WL))
        with mock.patch.object(cfg, "GEMINI_API_KEY", ""), mock.patch.object(nl.subprocess, "run") as run:
            self.assertIsNone(nl.genera_podcast(ART, WL))
            run.assert_not_called()

    def test_esito_ok_restituisce_i_file_e_scrive_l_archivio(self):
        with tempfile.TemporaryDirectory() as d:
            mp4 = _file(d, "p.mp4", 10)
            esito, arch = os.path.join(d, "esito.json"), os.path.join(d, "digest.json")

            def finto(*a, **k):
                with open(esito, "w") as f:
                    json.dump({"ok": True, "mp4": mp4, "mp3": os.path.join(d, "manca.mp3")}, f)

            with mock.patch.object(cfg, "PODCAST_DIR", d), mock.patch.object(cfg, "PODCAST_ESITO", esito), \
                    mock.patch.object(cfg, "PODCAST_ARCHIVIO", arch), \
                    mock.patch.object(cfg, "GEMINI_API_KEY", "k"), \
                    mock.patch.object(cfg, "PODCAST_DIPENDENZE_OK", True), \
                    mock.patch.object(nl.instagram, "genera_schede", return_value=(["s1.png"], [10])), \
                    mock.patch.object(nl.subprocess, "run", side_effect=finto):
                self.assertEqual(nl.genera_podcast(ART, WL), {"mp4": mp4})
            with open(arch, encoding="utf-8") as f:
                doc = json.load(f)
        self.assertEqual(doc["settimana"], 47)
        self.assertEqual(doc["pubblicati"][0]["pmid"], "1")
        self.assertEqual(len(doc["immagini"]), 1)

    def test_errore_non_blocca(self):
        with mock.patch.object(cfg, "GEMINI_API_KEY", "k"), mock.patch.object(cfg, "PODCAST_DIPENDENZE_OK", True), \
                mock.patch.object(nl.instagram, "genera_schede", side_effect=RuntimeError("boom")):
            self.assertIsNone(nl.genera_podcast(ART, WL))


class Corsa(unittest.TestCase):
    """main(): podcast allegato agli iscritti; SOLO_PODCAST solo a te; senza podcast la mail parte."""

    def _corsa(self, media, solo=False, avvisi="io@example.org", mail_ok=True):
        art = dict(ART[0])
        with contextlib.ExitStack() as st:
            d = st.enter_context(tempfile.TemporaryDirectory())
            p = lambda *a, **k: st.enter_context(mock.patch.object(*a, **k))  # noqa: E731
            for nome, valore in (("SOLO_PODCAST", solo), ("DRY_RUN", False), ("SOLO_INSTAGRAM", False),
                                 ("SOLO_FACEBOOK", False), ("SOLO_PODCAST_A", avvisi),
                                 ("GMAIL_USER", "casella@example.org")):
                p(cfg, nome, valore)
            p(cfg, "valida_config")
            p(nl, "numero_settimana", return_value=WL)
            iscritti = p(nl, "carica_destinatari", return_value=["iscritto@example.org"])
            p(nl, "raccogli_candidati", return_value=[art])
            p(nl, "filtra_top_articoli", return_value=[art])
            p(nl, "sintetizza_articoli", side_effect=lambda x: x)
            p(nl, "salva_archivio")
            p(nl, "genera_immagini", return_value=[])
            p(nl.avvisi, "carica_corsi", return_value=[])
            p(nl, "genera_podcast", return_value={"mp4": "p.mp4"} if media else None)
            p(nl, "allegato_podcast", return_value=media)
            mail = p(nl, "invia_email", side_effect=[mail_ok, True])
            tg = p(nl, "invia_telegram", return_value=True)
            fb = p(nl, "pubblica_facebook")
            p(nl, "pubblica_facebook_corsi")
            ig = p(nl, "pubblica_instagram")
            vecchia = os.getcwd()
            os.chdir(d)
            try:
                ok = nl.main()
            finally:
                os.chdir(vecchia)
        return ok, iscritti, mail, tg, ig, fb

    def test_iscritti_ricevono_il_podcast(self):
        ok, iscritti, mail, tg, ig, fb = self._corsa("podcast/p.mp4")
        self.assertTrue(ok)
        self.assertEqual(mail.call_count, 1)
        self.assertEqual(mail.call_args[0][2], ["iscritto@example.org"])
        self.assertEqual(mail.call_args[1]["media"], "podcast/p.mp4")
        self.assertIn(">Podcast<", mail.call_args[0][1])
        tg.assert_called_once()
        ig.assert_called_once()

    def test_se_la_mail_col_podcast_fallisce_riparte_senza(self):
        ok, _, mail, _, _, _ = self._corsa("podcast/p.mp4", mail_ok=False)
        self.assertTrue(ok)
        self.assertEqual(mail.call_count, 2)
        self.assertNotIn("media", mail.call_args_list[1][1])
        self.assertNotIn(">Podcast<", mail.call_args_list[1][0][1])

    def test_solo_podcast_mail_solo_a_te_niente_altro(self):
        ok, iscritti, mail, tg, ig, fb = self._corsa("podcast/p.mp4", solo=True)
        self.assertTrue(ok)
        iscritti.assert_not_called()
        tg.assert_not_called()
        ig.assert_not_called()
        fb.assert_not_called()
        oggetto, _, destinatari = mail.call_args[0]
        self.assertTrue(oggetto.startswith("[Prova podcast]"))
        self.assertEqual(destinatari, ["io@example.org"])

    def test_solo_podcast_senza_avvisi_email_va_alla_casella(self):
        _, _, mail, _, _, _ = self._corsa("podcast/p.mp4", solo=True, avvisi="")
        self.assertEqual(mail.call_args[0][2], ["casella@example.org"])

    def test_solo_podcast_fallito_nessuna_mail(self):
        ok, _, mail, tg, _, _ = self._corsa(None, solo=True)
        self.assertFalse(ok)
        mail.assert_not_called()
        tg.assert_not_called()


class ReelPodcast(unittest.TestCase):
    def test_senza_podcast_niente_reel(self):
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(cfg, "PODCAST_ESITO", os.path.join(d, "manca.json")), \
                mock.patch.object(nl.instagram, "pubblica_reel_podcast") as reel:
            self.assertIsNone(nl.pubblica_reel_podcast(WL))
            reel.assert_not_called()

    def test_podcast_riuscito_reel_con_estratto_e_saluti(self):
        with tempfile.TemporaryDirectory() as d:
            mp4, esito = _file(d, "p.mp4", 10), os.path.join(d, "esito.json")
            with open(esito, "w") as f:
                json.dump({"ok": True, "mp4": mp4, "sezioni": [[0, 10], [10, 60]], "saluti": [100, 108]}, f)
            with mock.patch.object(cfg, "PODCAST_ESITO", esito), \
                    mock.patch.object(nl.instagram, "pubblica_reel_podcast", return_value="123") as reel:
                self.assertEqual(nl.pubblica_reel_podcast(WL), "123")
        args, kw = reel.call_args
        self.assertEqual(args[0], mp4)
        self.assertTrue(args[2].startswith("POCUS Weekly Digest — il podcast della settimana 47/2026"))
        self.assertEqual(kw["saluti"], [100, 108])


if __name__ == "__main__":
    unittest.main()
