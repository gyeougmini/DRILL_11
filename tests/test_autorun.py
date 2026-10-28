import unittest
from types import SimpleNamespace
from unittest.mock import patch

import autorun
import boy


class FakeImage:
    def __init__(self):
        self.draw_calls = []

    def clip_composite_draw(self, *args):
        self.draw_calls.append(args)


class AutoRunTests(unittest.TestCase):
    def setUp(self):
        self.now = [0.0]
        self.image = FakeImage()
        self.patches = [
            patch.object(boy, 'load_image', return_value=self.image),
            patch.object(autorun, 'load_image', return_value=self.image),
            patch.object(boy, 'get_time', side_effect=lambda: self.now[0]),
            patch.object(autorun, 'get_time', side_effect=lambda: self.now[0]),
            patch.object(boy, 'get_canvas_width', return_value=800),
            patch.object(autorun, 'get_canvas_width', return_value=800),
        ]
        for active_patch in self.patches:
            active_patch.start()
        self.addCleanup(self.stop_patches)
        self.boy = boy.Boy()

    def stop_patches(self):
        for active_patch in reversed(self.patches):
            active_patch.stop()

    def send_key(self, event_type, key):
        self.boy.handle_event(SimpleNamespace(type=event_type, key=key))

    def test_a_starts_autorun_only_from_idle(self):
        self.send_key(boy.SDL_KEYDOWN, boy.SDLK_a)
        self.assertEqual(self.boy.state, 'autorun')
        self.assertEqual(self.boy.auto_run.speed, 450)

        self.boy.auto_run_timeout()
        self.boy.space_down()
        self.assertEqual(self.boy.state, 'idle')
        self.boy.time_out()
        self.assertEqual(self.boy.state, 'sleep')

        self.send_key(boy.SDL_KEYDOWN, boy.SDLK_a)
        self.assertEqual(self.boy.state, 'sleep')

        self.boy.space_down()
        self.boy.arrow_down()
        self.send_key(boy.SDL_KEYDOWN, boy.SDLK_a)
        self.assertEqual(self.boy.state, 'run')


if __name__ == '__main__':
    unittest.main()
