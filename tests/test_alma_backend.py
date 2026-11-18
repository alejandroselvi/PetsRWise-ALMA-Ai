"""Offline tests. No real API key or network required."""
import unittest
from types import SimpleNamespace as NS

from alma_backend import (
    AlmaProfile, ask_alma, build_tools,
    extract_sources, instructions_for,
    possible_emergency, vector_ids_from_env,
)


class TestAlmaBackend(unittest.TestCase):
    def test_three_vector_ids(self):
        env = {'ALMA_VECTOR_STORE_IDS': 'vs_111, vs_222,vs_111, vs_333'}
        self.assertEqual(vector_ids_from_env(env), ['vs_111','vs_222','vs_333'])

    def test_fallback_single_vector_id(self):
        self.assertEqual(vector_ids_from_env({'ALMA_VECTOR_STORE_ID': 'vs_older'}), ['vs_older'])

    def test_no_placeholder(self):
        self.assertEqual(vector_ids_from_env({'ALMA_VECTOR_STORE_IDS': 'YOUR_ID, '}), [])

    def test_tools(self):
        tools = build_tools(['vs_one'], True)
        self.assertEqual(tools[0]['vector_store_ids'], ['vs_one'])
        self.assertEqual(tools[1]['type'], 'web_search')
        self.assertEqual(build_tools([], False), [])

    def test_emergency_warning(self):
        self.assertTrue(possible_emergency('Mi gato no puede orinar'))
        self.assertTrue(possible_emergency('My dog cannot breathe'))
        self.assertFalse(possible_emergency('Hola ALMA'))

    def test_system_boundaries(self):
        guidance = instructions_for(AlmaProfile())
        self.assertIn('Never state you are a veterinarian', guidance)
        self.assertIn('UNAPPROVED DRAFT MATERIAL', guidance)

    def test_sources_from_files_and_web(self):
        response = NS(output=[
            NS(type='file_search_call', results=[NS(filename='intake_es_v1.md')]),
            NS(type='web_search_call', action=NS(sources=[NS(title='Veterinary Clinic', url='https://example.org/clinic')])),
            NS(type='message', content=[]),
        ])
        results = extract_sources(response)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'intake_es_v1.md')
        self.assertEqual(results[1]['url'], 'https://example.org/clinic')

    def test_request_with_previous_response_id(self):
        class FakeResponses:
            def __init__(self): self.kwargs = None
            def create(self, **kwargs):
                self.kwargs = kwargs
                return NS(id='resp_two', output_text='Hola desde ALMA', output=[])
        fake = FakeResponses()
        result = ask_alma(NS(responses=fake), 'Hola', AlmaProfile(),
                          ['vs_first', 'vs_second'], 'resp_first', True)
        self.assertEqual(result.text, 'Hola desde ALMA')
        self.assertEqual(fake.kwargs['previous_response_id'], 'resp_first')
        self.assertEqual(fake.kwargs['tools'][0]['vector_store_ids'], ['vs_first','vs_second'])
        self.assertEqual(fake.kwargs['tools'][1]['type'], 'web_search')


if __name__ == '__main__':
    unittest.main()
