"""Offline smoke tests. No API request is performed."""
import os
import unittest
from unittest.mock import Mock

from alma_backend import (
    AlmaProfile, ask_alma, build_tools, extract_sources,
    possible_emergency, vector_ids_from_env,
)
from alma_voice import DEFAULT_SPEED, speech_instructions


class AlmaBackendTests(unittest.TestCase):
    def test_single_vector_backward_compatible(self):
        self.assertEqual(vector_ids_from_env({'ALMA_VECTOR_STORE_ID': 'vs_one'}), ['vs_one'])

    def test_multiple_vector_ids(self):
        self.assertEqual(vector_ids_from_env({'ALMA_VECTOR_STORE_IDS': 'vs_one, vs_two, vs_one'}),
                         ['vs_one', 'vs_two'])

    def test_no_placeholder_ids(self):
        self.assertEqual(vector_ids_from_env({'ALMA_VECTOR_STORE_IDS': 'x, no, vs_'}), [])

    def test_tools_include_file_and_web(self):
        tools = build_tools(['vs_one', 'vs_two'], True)
        self.assertEqual(tools[0]['vector_store_ids'], ['vs_one', 'vs_two'])
        self.assertEqual(tools[1]['type'], 'web_search')

    def test_tools_allow_web_off(self):
        self.assertEqual(len(build_tools(['vs_one'], False)), 1)

    def test_evidence_extraction(self):
        response = {'output': [
            {'type': 'file_search_call', 'results': [{'filename': 'intake_es_v1.md'}]},
            {'type': 'message', 'content': [{'annotations': [
                {'type': 'url_citation', 'title': 'Demo vet website', 'url': 'https://example.com/vet'}
            ]}]}
        ]}
        sources = extract_sources(response)
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0]['title'], 'intake_es_v1.md')
        self.assertEqual(sources[1]['url'], 'https://example.com/vet')

    def test_potential_emergency_phrase(self):
        self.assertTrue(possible_emergency('Mi gato no puede orinar'))
        self.assertFalse(possible_emergency('Hola, tengo un perro'))

    def test_api_call_uses_store_and_state(self):
        response = Mock(output_text='Demo', id='resp_test', output=[])
        client = Mock()
        client.responses.create.return_value = response
        out = ask_alma(client, 'Hola ALMA', AlmaProfile(), ['vs_one'],
                       previous_response_id='resp_previous', use_web_search=True, model='test-model')
        kwargs = client.responses.create.call_args.kwargs
        self.assertEqual(kwargs['previous_response_id'], 'resp_previous')
        self.assertEqual(kwargs['model'], 'test-model')
        self.assertEqual(kwargs['tools'][0]['vector_store_ids'], ['vs_one'])
        self.assertEqual(out.text, 'Demo')

    def test_voice_locale_configuration(self):
        self.assertEqual(DEFAULT_SPEED, 1.2)
        self.assertIn('latinoamericano', speech_instructions('Español'))
        self.assertIn('United States English', speech_instructions('English'))

if __name__ == '__main__':
    unittest.main()
