#from env import NLAN_DIR 
import os, yaml

# [Reference] http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = decode_dict(item)
        rv.append(item)
    return rv

def decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = decode_dict(value)
        rv[key] = value
    return rv

if __name__ == '__main__':

    import unittest
    import json
    import dictdiffer

    class TestSequenceFunctions(unittest.TestCase):

        def testDecodeDict(self):
            json_data = '{"a": 0, "b": 0, "c": {"d": null, "e": "abc"}}'
            # Unicode dict
            dict_data0 = json.loads(json_data)
            sample_value  = dict_data0['c']['e']
            # Ascii dict
            dict_data1 = json.loads(json_data, object_hook=decode_dict )
            
            dict_data2 = {"a": 0, "b": 0, "c": {"d": None, "e": "abc"}}

            self.assertIsInstance(sample_value, unicode) 
            self.assertNotIsInstance(sample_value, str)
            self.assertEqual(len(list(dictdiffer.diff(dict_data1, dict_data2))), 0)

    unittest.main(verbosity=2)
