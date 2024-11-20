import unittest
import os
from new_app import app

MUSICXML_FOLDER = "./test_musicxml_folder"

class backend_tests(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()
        os.makedirs(MUSICXML_FOLDER, exist_ok=True)
        with open(os.path.join(MUSICXML_FOLDER, "test.musicxml"), w) as f:
            # This is 1 measure with 1 note at middle C in 4/4 time
            f.write("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                    <!DOCTYPE score-partwise PUBLIC
                        "-//Recordare//DTD MusicXML 4.0 Partwise//EN"
                        "http://www.musicxml.org/dtds/partwise.dtd">
                    <score-partwise version="4.0">
                        <part-list>
                            <score-part id="P1">
                                <part-name>Music</part-name>
                            </score-part>
                        </part-list>
                        <part id="P1">
                            <measure number="1">
                                <attributes>
                                    <divisions>1</divisions>
                                    <key>
                                        <fifths>0</fifths>
                                    </key>
                                    <time>
                                        <beats>4</beats>
                                        <beat-type>4</beat-type>
                                    </time>
                                    <clef>
                                        <sign>G</sign>
                                        <line>2</line>
                                    </clef>
                                </attributes>
                                <note>
                                    <pitch>
                                        <step>C</step>
                                        <octave>4</octave>
                                    </pitch>
                                    <duration>4</duration>
                                    <type>whole</type>
                                </note>
                            </measure>
                        </part>
                    </score-partwise>""")

    def tearDown(self):
        if os.path.exists(MUSICXML_FOLDER):
            for file in os.listdir(MUSICXML_FOLDER):
                os.remove(os.path.join(MUSICXML_FOLDER, file))
            os.rmdir(MUSICXML_FOLDER)
    
    def test_get_scores(self):
        response = self.client.get('/scores')
        self.assertEqual(response.status_code, 200)
    
    def test_get_score(self):
        headers = {"session-token": "test-session-token"}
        response = self.client.get('/scores/test.musicxml', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/xml")
    
    def test_synthesize_audio(self):
        headers = {"session-token": "test-session-token"}
        response = self.client.get('/scores/test.musicxml/120', headers=headers)
        self.assertEqual(response.status_code, 200)
    
    def test_synchronization(self):
        headers = {"session-token": "test-session-token"}
        response = self.client.post('/synchronization', headers=headers)
        self.assertEqual(response.status_code, 200)


