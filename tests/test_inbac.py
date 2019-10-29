import os
import unittest
import unittest.mock as mock

from PIL import Image

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

    def test_selection_box_for_aspect_ratio_returns_box_with_aspect_ratio(self):
        aspect_ratio = 16.0/9.0
        mouse_press_coord = (0.0, 0.0)
        mouse_move_coord = (15.0, 9.0)
        selection_box = (0.0, 0.0, 15.0, 9.0)
        expected_selection_box = (0.0, 0.0, 16.0, 9.0)
        returned_selection_box = Application.get_selection_box_for_aspect_ratio(selection_box, aspect_ratio, 
                                                                                mouse_press_coord, mouse_move_coord)
        self.assertEqual(expected_selection_box, returned_selection_box)

    def test_get_selected_box_returns_correct_selection_box_when_selecting_from_upper_left_to_bottom_right(self):
        mouse_press_coord = (0.0, 0.0)
        mouse_move_coord = (15.0, 9.0)
        expected_selection_box = (0.0, 0.0, 15.0, 9.0)
        returned_selection_box = Application.get_selected_box(mouse_press_coord, mouse_move_coord, None)
        self.assertEqual(expected_selection_box, returned_selection_box)
    
    def test_get_selected_box_returns_correct_selection_box_when_selecting_from_bottom_right_to_upper_left(self):
        mouse_press_coord = (15.0, 9.0)
        mouse_move_coord = (0.0, 0.0)
        expected_selection_box = (0.0, 0.0, 15.0, 9.0)
        returned_selection_box = Application.get_selected_box(mouse_press_coord, mouse_move_coord, None)
        self.assertEqual(expected_selection_box, returned_selection_box)

    def test_get_real_box(self):
        selected_box = (2, 2, 4, 4)
        expected_real_box = (4, 4, 8, 8)
        returned_real_box = Application.get_real_box(selected_box, (10, 10), (5, 5))
        self.assertEqual(expected_real_box, returned_real_box)

    @mock.patch('inbac.inbac.os.listdir')
    def test_load_images_with_wrong_filetype(self, mock_listdir):
        mock_listdir.return_value = ["test.txt", "test2"]
        returned_images = Application.load_images("/home/test/", False)
        self.assertListEqual([], returned_images)

    @mock.patch('inbac.inbac.Image.open')
    @mock.patch('inbac.inbac.os.listdir')
    def test_load_images_with_image_file(self, mock_listdir, mock_image_open):
        mock_listdir.return_value = ["test.txt", "test2.jpg"]
        directory = "/home/test/"
        returned_image = Image.new("RGB", (800, 600))
        mock_image_open.return_value = returned_image
        returned_images = Application.load_images(directory, False)
        mock_image_open.assert_called_with(os.path.join(directory, mock_listdir.return_value[1]))
        self.assertListEqual([returned_image], returned_images)

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
