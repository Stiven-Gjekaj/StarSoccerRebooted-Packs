# Tests the checks of the zip file of a pack. The test makes each zip file.
import io, os, sys, unittest, zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import check_index


def make_zip(files):
    data = io.BytesIO()
    with zipfile.ZipFile(data, 'w') as archive:
        for name, text in files.items():
            archive.writestr(name, text)
    return data.getvalue()


ROW = {'id': 'harbour', 'version': '1.0', 'format': '1'}
PACK = 'id=harbour\nname=Harbour\nversion=1.0\nformat=1\n'


class CheckZip(unittest.TestCase):
    def faults(self, files):
        found = []
        check_index.check_zip(ROW, make_zip(files), found)
        return found

    def test_accepts_a_good_pack(self):
        self.assertEqual(self.faults({'pack.txt': PACK, 'world/Clubs.txt': 'id\n', 'crests/1.png': 'x'}), [])

    def test_accepts_a_pack_in_one_folder(self):
        self.assertEqual(self.faults({'harbour/pack.txt': PACK}), [])

    def test_refuses_a_zip_with_no_pack_txt(self):
        self.assertEqual(len(self.faults({'world/Clubs.txt': 'id\n'})), 1)

    def test_refuses_another_version(self):
        found = self.faults({'pack.txt': PACK.replace('version=1.0', 'version=2.0')})
        self.assertTrue(any('version' in f for f in found))

    def test_refuses_a_kind_that_is_not_data(self):
        found = self.faults({'pack.txt': PACK, 'run.sh': 'echo'})
        self.assertTrue(any('kind' in f for f in found))

    def test_refuses_a_name_out_of_the_pack(self):
        found = self.faults({'pack.txt': PACK, '../evil.txt': 'x'})
        self.assertTrue(any('goes out' in f for f in found))

    def test_refuses_a_file_that_is_not_a_zip(self):
        found = []
        check_index.check_zip(ROW, b'not a zip', found)
        self.assertEqual(len(found), 1)


if __name__ == '__main__':
    unittest.main()
