from pico2d import get_canvas_width, get_time, load_image

FRAME_SIZE = 100
FRAME_COUNT = 8
ANIMATION_FPS = 10
BASE_GAME_FPS = 100
SPEED_MULTIPLIER = 1.5
AUTO_RUN_DURATION = 5
AUTO_RUN_SCALE = 1.5


class AutoRun:
    def __init__(self, boy, run_speed):
        self.boy = boy
        self.speed = run_speed * BASE_GAME_FPS * SPEED_MULTIPLIER
        self.image = load_image('run_animation.png')
        self.frame = 0
        self.direction = 1
        self.started_at = None
        self.last_updated_at = None

    def start(self):
        self.started_at = get_time()
        self.last_updated_at = self.started_at
        self.frame = 0
        self.direction = self.boy.face_dir or 1

    def stop(self):
        self.started_at = None
        self.last_updated_at = None
        self.frame = 0

    def update(self):
        now = get_time()
        elapsed = max(0, now - self.last_updated_at)
        self.last_updated_at = now

        self.frame = (self.frame + elapsed * ANIMATION_FPS) % FRAME_COUNT
        half_width = FRAME_SIZE * AUTO_RUN_SCALE / 2
        left_edge = half_width
        right_edge = get_canvas_width() - half_width
        span = right_edge - left_edge

        position = self.boy.x - left_edge + self.direction * self.speed * elapsed
        reflected_position = position % (2 * span)
        if reflected_position < span:
            self.boy.x = left_edge + reflected_position
            self.direction = 1
        else:
            self.boy.x = right_edge - (reflected_position - span)
            self.direction = -1

        self.boy.face_dir = self.direction
        return now - self.started_at >= AUTO_RUN_DURATION
