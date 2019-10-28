import unittest
import unittest.mock as mock
import os
from inbac.inbac import Application

class TestInbac(unittest.TestCase):

    @mock.patch('inbac.inbac.os.path.isfile')
    def test_find_available_name_returns_passed_name_if_file_does_not_exist(self, mock_path_isfile):
        directory = "/home/test/"
        filename = "test.jpg"
        mock_path_isfile.return_value = False

        returned_filename = Application.find_available_name(directory, filename)
        mock_path_isfile.assert_called_with(os.path.join(directory, filename))
        self.assertEqual(filename, returned_filename)

    @mock.patch('inbac.inbac.os.path.isfile')
    def test_find_available_name_returns_name_with_number_if_file_exists(self, mock_path_isfile):
        directory = "/home/test/"
        filename = "test.jpg"
        new_filename = "test2.jpg"
        mock_path_isfile.side_effect = file_exist

        returned_filename = Application.find_available_name(directory, filename)
        calls = [mock.call(os.path.join(directory, filename)), mock.call(os.path.join(directory, new_filename))]
        mock_path_isfile.assert_has_calls(calls)
        self.assertEqual(new_filename, returned_filename)

def file_exist(x):
    if x == "/home/test/test.jpg":
        return True
    elif x == "/home/test/test2.jpg":
        return False
    return False
        
def main():
    unittest.main(module='tests.test_inbac')

if __name__ == '__main__':
    main()