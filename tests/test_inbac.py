import os
import unittest
import unittest.mock as mock

from inbac.inbac import Application
from inbac.controller import Controller
from inbac.model import Model

from PIL import Image


class TestInbac(unittest.TestCase):

    @mock.patch('inbac.inbac.os.path.isfile')
    def test_find_available_name_returns_passed_name_if_file_does_not_exist(self, mock_path_isfile):
        directory = "/home/test/"
        filename = "test.jpg"
        mock_path_isfile.return_value = False

        returned_filename = Controller.find_available_name(
            directory, filename)
        mock_path_isfile.assert_called_with(os.path.join(directory, filename))
        self.assertEqual(filename, returned_filename)

    @mock.patch('inbac.inbac.os.path.isfile')
    def test_find_available_name_returns_name_with_number_if_file_exists(self, mock_path_isfile):
        directory = "/home/test/"
        filename = "test.jpg"
        new_filename = "test2.jpg"
        mock_path_isfile.side_effect = file_exist

        returned_filename = Controller.find_available_name(
            directory, filename)
        calls = [mock.call(os.path.join(directory, filename)),
                 mock.call(os.path.join(directory, new_filename))]
        mock_path_isfile.assert_has_calls(calls)
        self.assertEqual(new_filename, returned_filename)

    def test_selection_box_for_aspect_ratio_returns_box_with_aspect_ratio(self):
        aspect_ratio = 16.0/9.0
        mouse_press_coord = (0.0, 0.0)
        mouse_move_coord = (15.0, 9.0)
        selection_box = (0.0, 0.0, 15.0, 9.0)
        expected_selection_box = (0.0, 0.0, 16.0, 9.0)
        returned_selection_box = Controller.get_selection_box_for_aspect_ratio(selection_box, aspect_ratio,
                                                                                mouse_press_coord, mouse_move_coord)
        self.assertEqual(expected_selection_box, returned_selection_box)

    def test_get_selected_box_returns_correct_selection_box_when_selecting_from_upper_left_to_bottom_right(self):
        mouse_press_coord = (0.0, 0.0)
        mouse_move_coord = (15.0, 9.0)
        expected_selection_box = (0.0, 0.0, 15.0, 9.0)
        returned_selection_box = Controller.get_selected_box(
            mouse_press_coord, mouse_move_coord, None)
        self.assertEqual(expected_selection_box, returned_selection_box)

    def test_get_selected_box_returns_correct_selection_box_when_selecting_from_bottom_right_to_upper_left(self):
        mouse_press_coord = (15.0, 9.0)
        mouse_move_coord = (0.0, 0.0)
        expected_selection_box = (0.0, 0.0, 15.0, 9.0)
        returned_selection_box = Controller.get_selected_box(
            mouse_press_coord, mouse_move_coord, None)
        self.assertEqual(expected_selection_box, returned_selection_box)

    def test_get_real_box(self):
        selected_box = (2, 2, 4, 4)
        expected_real_box = (4, 4, 8, 8)
        returned_real_box = Controller.get_real_box(
            selected_box, (10, 10), (5, 5))
        self.assertEqual(expected_real_box, returned_real_box)

    @mock.patch('inbac.inbac.os.listdir')
    def test_load_images_with_wrong_filetype(self, mock_listdir):
        mock_listdir.return_value = ["test.txt", "test2"]
        returned_images = Controller.load_image_list("/home/test/")
        self.assertListEqual([], returned_images)

    @mock.patch('inbac.inbac.os.listdir')
    def test_load_images(self, mock_listdir):
        mock_listdir.return_value = ["test.txt", "test2.jpg"]
        directory = "/home/test/"
        returned_images = Controller.load_image_list(directory)
        self.assertListEqual(["test2.jpg"], returned_images)

    @mock.patch('inbac.controller.Image.open')
    @mock.patch('inbac.controller.Controller.display_image_on_canvas')
    @mock.patch('inbac.view.View')
    def test_load_image(self, mock_view, mock_display_image, mock_image_open):
        args = mock.Mock()
        args.input_dir = None
        image_name = "test.jpg"
        model = Model(args)
        controller = Controller(model, mock_view)
        args.input_dir = "/home/test/"
        img = Image.new("RGB", (8, 8))
        mock_image_open.return_value = img
        controller.load_image(image_name)
        mock_image_open.assert_called_with(os.path.join(args.input_dir, image_name))
        mock_display_image.assert_called_with(img)
        mock_view.set_title.assert_called_with(image_name)

    @mock.patch('inbac.controller.Controller.load_image')
    @mock.patch('inbac.view.View')
    def test_next_image(self, mock_view, mock_load_image):
        args = mock.Mock()
        args.input_dir = None
        model = Model(args)
        controller = Controller(model, mock_view)
        model.images = ["abc.png", "test.png", "ababaa.png"]
        model.current_file = 1
        controller.next_image()
        mock_load_image.assert_called_with = model.images[2]
        self.assertEqual(2, model.current_file)

    @mock.patch('inbac.view.View')
    def test_next_image_last_image(self, mock_view):
        args = mock.Mock()
        args.input_dir = None
        model = Model(args)
        controller = Controller(model, mock_view)
        model.images = ["abc.png", "test.png", "ababaa.png"]
        model.current_file = 2
        controller.next_image()
        self.assertEqual(2, model.current_file)

    @mock.patch('inbac.controller.Controller.load_image')
    @mock.patch('inbac.view.View')
    def test_previous_image(self, mock_view, mock_load_image):
        args = mock.Mock()
        args.input_dir = None
        model = Model(args)
        controller = Controller(model, mock_view)
        model.images = ["abc.png", "test.png", "ababaa.png"]
        model.current_file = 1
        controller.previous_image()
        mock_load_image.assert_called_with = model.images[2]
        self.assertEqual(0, model.current_file)

    @mock.patch('inbac.view.View')
    def test_previous_image_first_image(self, mock_view):
        args = mock.Mock()
        args.input_dir = None
        model = Model(args)
        controller = Controller(model, mock_view)
        model.images = ["abc.png", "test.png", "ababaa.png"]
        model.current_file = 0
        controller.previous_image()
        self.assertEqual(0, model.current_file)

    def test_calculate_canvas_image_dimensions(self):
        image_width = 1000
        image_height = 500
        canvas_width = 500
        canvas_height = 400
        (new_width, new_height) = Controller.calculate_canvas_image_dimensions(image_width, image_height, 
                                                                               canvas_width, canvas_height)
        self.assertEqual(image_width / 2, new_width)
        self.assertEqual(image_height / 2, new_height)

    @mock.patch('inbac.view.View')
    @mock.patch('inbac.controller.Controller.display_image_on_canvas')
    def test_rotated_image(self, mock_display_image, mock_view):
        args = mock.Mock()
        args.input_dir = None
        model = Model(args)
        controller = Controller(model, mock_view)
        image = Image.new("RGB", (8, 4))
        model.current_image = image
        controller.rotate_image()
        rotated_image = mock_display_image.call_args[0][0]
        mock_display_image.assert_called()
        self.assertEqual(rotated_image.width, 4)
        self.assertEqual(rotated_image.height, 8)
        
def file_exist(x):
    if x == "/home/test/test.jpg":
        return True
    return False


def main():
    unittest.main(module='tests.test_inbac')


if __name__ == '__main__':
    main()
