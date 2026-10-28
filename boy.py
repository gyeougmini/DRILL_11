from pico2d import (load_image, get_time, get_canvas_width, clamp,
                    SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT)
from transitions import Machine

ANIMATION_SPEED = 0.1    # 루프 1번에 넘길 프레임 수 (루프 약 100번/초 → 초당 약 10프레임)
RUN_SPEED = 3            # 루프 1번에 움직이는 픽셀 수
HALF_WIDTH = 25          # 화면 밖으로 안 나가게 할 때 쓰는 소년 몸의 반 너비


class Boy:
    states = ['idle', 'sleep', 'run']

    # 상태 변화: trigger(사건)가 일어나면 source 상태에서 dest 상태로 간다
    transitions = [
        {'trigger': 'time_out',   'source': 'idle',  'dest': 'sleep'},   # IDLE에서 5초 지남
        {'trigger': 'space_down', 'source': 'sleep', 'dest': 'idle'},    # SLEEP에서 space 누름
        {'trigger': 'arrow_down', 'source': ['idle', 'sleep'], 'dest': 'run'},  # IDLE/SLEEP에서 방향키 누름
        {'trigger': 'arrow_up',   'source': 'run',   'dest': 'idle',     # RUN에서 방향키를 다 뗌
         'conditions': 'no_arrow_pressed'},
    ]

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.image = load_image('animation_sheet.png')
        self.idle_start_time = get_time()
        self.left_pressed, self.right_pressed = False, False

        # transitions 상태 머신: 상태가 바뀌면 self.state 값이 바뀐다
        # ignore_invalid_triggers: 지금 상태에서 쓸 수 없는 trigger는 에러 없이 무시
        self.machine = Machine(model=self, states=Boy.states, transitions=Boy.transitions,
                               initial='idle', ignore_invalid_triggers=True)

    # 방향키가 하나도 안 눌려 있으면 True (RUN → IDLE 조건)
    def no_arrow_pressed(self):
        return not self.left_pressed and not self.right_pressed

    # IDLE 상태에 들어올 때 (transitions가 이름을 보고 자동으로 호출)
    def on_enter_idle(self):
        self.idle_start_time = get_time()

    # IDLE 상태에서 매 프레임 하는 일
    def idle_do(self):
        self.frame = (self.frame + ANIMATION_SPEED) % 8
        if get_time() - self.idle_start_time >= 5:
            self.time_out()

    # IDLE 상태 그리기: 시트의 y=300(오른쪽 보기), y=200(왼쪽 보기) 줄이 IDLE 애니메이션
    def idle_draw(self):
        if self.face_dir == 1:
            self.image.clip_draw(int(self.frame) * 100, 300, 100, 100, self.x, self.y)
        else:
            self.image.clip_draw(int(self.frame) * 100, 200, 100, 100, self.x, self.y)

    # SLEEP 상태에서 매 프레임 하는 일
    def sleep_do(self):
        self.frame = (self.frame + ANIMATION_SPEED) % 8

    # SLEEP 상태 그리기: IDLE 그림을 90도 눕혀서 그린다
    def sleep_draw(self):
        if self.face_dir == 1:
            self.image.clip_composite_draw(int(self.frame) * 100, 300, 100, 100,
                                           3.141592 / 2, '', self.x - 25, self.y - 25, 100, 100)
        else:
            self.image.clip_composite_draw(int(self.frame) * 100, 200, 100, 100,
                                           -3.141592 / 2, '', self.x + 25, self.y - 25, 100, 100)

    # RUN 상태에서 매 프레임 하는 일: 눌린 방향키로 방향을 정해서 움직인다 (오른쪽 1, 왼쪽 -1)
    def run_do(self):
        dir = int(self.right_pressed) - int(self.left_pressed)
        if dir != 0:
            self.face_dir = dir
        self.frame = (self.frame + ANIMATION_SPEED) % 8
        self.x += dir * RUN_SPEED
        self.x = clamp(HALF_WIDTH, self.x, get_canvas_width() - HALF_WIDTH)

    # RUN 상태 그리기: 시트의 y=100(오른쪽으로 달리기), y=0(왼쪽으로 달리기) 줄
    def run_draw(self):
        if self.face_dir == 1:
            self.image.clip_draw(int(self.frame) * 100, 100, 100, 100, self.x, self.y)
        else:
            self.image.clip_draw(int(self.frame) * 100, 0, 100, 100, self.x, self.y)

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_SPACE:
                self.space_down()
            elif event.key in (SDLK_LEFT, SDLK_RIGHT):
                if event.key == SDLK_LEFT:
                    self.left_pressed = True
                else:
                    self.right_pressed = True
                self.arrow_down()
        elif event.type == SDL_KEYUP:
            if event.key in (SDLK_LEFT, SDLK_RIGHT):
                if event.key == SDLK_LEFT:
                    self.left_pressed = False
                else:
                    self.right_pressed = False
                self.arrow_up()

    def update(self):
        if self.state == 'idle':
            self.idle_do()
        elif self.state == 'sleep':
            self.sleep_do()
        elif self.state == 'run':
            self.run_do()

    def draw(self):
        if self.state == 'idle':
            self.idle_draw()
        elif self.state == 'sleep':
            self.sleep_draw()
        elif self.state == 'run':
            self.run_draw()
