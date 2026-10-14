"""Regression suite offline: non chiama API, non invia email/social."""
import json
import unittest
from unittest.mock import patch
from urllib.parse import unquote

import newsletter_pocus as newsletter
import pocus_search


class RicercaPocusTest(unittest.TestCase):
    def test_esearch_pubmed_wide_and_edat(self):
        payload = json.dumps({"esearchresult": {
            "count": "2", "idlist": ["12345678", "23456789"]}}).encode()
        with patch.object(pocus_search, "_richiesta", return_value=payload) as mock:
            ids = pocus_search.cerca_pmid(7)
        self.assertEqual(ids, ["12345678", "23456789"])
        url = unquote(mock.call_args.args[0])
        self.assertIn("datetype=edat", url)
        self.assertIn("reldate=7", url)
        self.assertIn("POCUS[tiab]", url)

    def test_pocus_gate(self):
        self.assertFalse(pocus_search.potenzialmente_pocus(
            "Sepsis mortality in intensive care",
            "An observational analysis of sepsis outcomes and antibiotics."))
        self.assertTrue(pocus_search.potenzialmente_pocus(
            "Point-of-care ultrasound in shock",
            "Emergency physicians performed POCUS during resuscitation."))
        self.assertTrue(pocus_search.potenzialmente_pocus(
            "Ultrasonography for central venous access",
            "A pragmatic trial of ultrasound-assisted vascular access."))

    def test_efetch_preserves_publication_metadata(self):
        xml = b"""<PubmedArticleSet><PubmedArticle><MedlineCitation>
          <PMID>12345678</PMID><Article><ArticleTitle>Bedside lung ultrasound</ArticleTitle>
          <Abstract><AbstractText Label="Methods">POCUS in the ED.</AbstractText></Abstract>
          <Journal><Title>POCUS Journal</Title><JournalIssue><PubDate>
          <Year>2026</Year><Month>Oct</Month><Day>12</Day>
          </PubDate></JournalIssue></Journal>
          <PublicationTypeList><PublicationType>Randomized Controlled Trial</PublicationType></PublicationTypeList>
          </Article><MedlineJournalInfo><MedlineTA>POCUS J</MedlineTA></MedlineJournalInfo>
          </MedlineCitation><PubmedData><ArticleIdList>
          <ArticleId IdType="doi">10.1111/sample</ArticleId>
          </ArticleIdList></PubmedData></PubmedArticle></PubmedArticleSet>"""
        import xml.etree.ElementTree as ET
        result = pocus_search._estrai_articolo(
            ET.fromstring(xml).find("./PubmedArticle"), {})
        self.assertEqual(result["pmid"], "12345678")
        self.assertEqual(result["doi"], "10.1111/sample")
        self.assertIn("Methods:", result["abstract"])
        self.assertEqual(result["data"], "2026 Oct 12")


class SelezioneEditorialeTest(unittest.TestCase):
    def setUp(self):
        self.articoli = [
            {"pmid": str(10000000 + i), "titolo": f"POCUS study {i}",
             "abstract": "Lung ultrasound for acute patients in an ED. " * 12,
             "pubtypes": [], "rivista": "POCUS Journal", "data": "2026 Oct 14",
             "gruppo": "spec", "pubdate_dt": None}
            for i in range(4)
        ]

    def test_ai_required_even_when_fewer_than_five_candidates(self):
        output = json.dumps([{"pmid": self.articoli[0]["pmid"],
                              "tema": "ecografia polmonare", "perche": "POCUS"}])
        with patch.object(newsletter, "chiama_claude", return_value=output) as mock:
            scelti = newsletter.filtra_top_articoli(self.articoli)
        mock.assert_called_once()
        self.assertEqual([a["pmid"] for a in scelti], [self.articoli[0]["pmid"]])

    def test_no_unrelated_filler(self):
        output = json.dumps([{"pmid": self.articoli[1]["pmid"],
                              "tema": "ecografia vascolare", "perche": "POCUS"}])
        with patch.object(newsletter, "chiama_claude", return_value=output):
            scelti = newsletter.filtra_top_articoli(self.articoli)
        self.assertEqual(len(scelti), 1)

    def test_ai_failure_prevents_publication(self):
        with patch.object(newsletter, "chiama_claude",
                          side_effect=RuntimeError("Anthropic API unavailable")):
            scelti = newsletter.filtra_top_articoli(self.articoli)
        self.assertEqual(scelti, [])


if __name__ == '__main__':
    unittest.main()
