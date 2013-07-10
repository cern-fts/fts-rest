from fts3rest.controllers.schema import _schema
import unittest
import jsonschema



class TestJsonSchema(unittest.TestCase):
    def setUp(self):
        self.data = {"files": [
                        {
                          "sources": ["srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/dteam/test.rand"],
                          "destinations": ["gsiftp://lxbra1910.cern.ch/lxbra1910.cern.ch:/tmp/file.aalvarez.copy"],
                          "metadata": {"issuer": "aalvarez"},
                          "filesize": 1048576,
                          "checksum": "adler32:36603040"
                        }
                      ],
                      "params": {
                        "verify_checksum": True,
                        "reuse": False,
                        "spacetoken": None,
                        "bring_online": None,
                        "copy_pin_lifetime": -1,
                        "job_metadata": {"activity": "test"},
                        "source_spacetoken": None,
                        "overwrite": True,
                        "gridftp": None
                      }
                    }
        self.schema = _schema()


    def test_validation(self):
        jsonschema.validate(self.data, self.schema)


    def test_missing_files(self):
        del self.data['files']
        self.assertRaises(jsonschema.ValidationError, jsonschema.validate, self.data, self.schema)


    def test_missing_params(self):
        del self.data['params']
        jsonschema.validate(self.data, self.schema)
        
        
    def test_bad_reuse(self):
        self.data['params']['reuse'] = 'A string'
        self.assertRaises(jsonschema.ValidationError, jsonschema.validate, self.data, self.schema)


    def test_files_not_array(self):
        self.data['files'] = self.data['files'][0]
        self.assertRaises(jsonschema.ValidationError, jsonschema.validate, self.data, self.schema)


    def test_source_not_array(self):
        self.data['files'][0]['sources'] = 'srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/dteam/test.rand'
        self.assertRaises(jsonschema.ValidationError, jsonschema.validate, self.data, self.schema)

