from camera import *
from item import *
import pygame
import threading


class Scene:
    def __init__(self, ):
        """
        Initializes a new scene.  By default, puts one object in and sets up everything in the correct positions.
        """
        self.world = World()
        self.camera = Camera(init_pos=[0, 0, 0], init_angle=[0, 0, 0], init_fov=.25)
        self.renderer = Renderer()

    def begin_scene(self, window_size=(1000, 1000)):
        """
        Begins the rendering and user input MVC process.
        """
        canvas = pygame.display.set_mode(window_size, 0, 32)
        pygame.mouse.set_visible(False)
        # pygame.event.set_grab(True)  # Only uncomment this if you're SURE it won't break everything
        render_thread = threading.Thread(target=self.render_cycle, args=(canvas,))
        render_thread.start()

        input_thread = threading.Thread(target=self.get_user_input)
        input_thread.start()

    def render_cycle(self, canvas):
        """
        handles the continuous cycle of rendering each frame.
        """
        pygame.init()
        clock = pygame.time.Clock()
        while True:
            self.renderer.draw_scene(self.world, self.camera, canvas)
            clock.tick(30) # 30 FPS

    def get_user_input(self):
        """
        Gets the input from the user.
        """
        event_keys = (pygame.K_w, pygame.K_s, pygame.K_d, pygame.K_a)
        keys_pressed = [0, 0, 0, 0]  # The pressed status of the keys
        mouse_x, mouse_y = pygame.mouse.get_pos()
        last_x, last_y = pygame.mouse.get_pos()
        while True:
            events = pygame.event.get()
            down_keys = [event.key for event in events if event.type == pygame.KEYDOWN]
            up_keys = [event.key for event in events if event.type == pygame.KEYUP]
            for idx in range(4):
                keys_pressed[idx] += int(event_keys[idx] in down_keys) - int(event_keys[idx] in up_keys)
            self.camera.move(keys_pressed[2]-keys_pressed[3], keys_pressed[0]-keys_pressed[1], speed=0.001)
            x, y = pygame.mouse.get_pos()

            # This block avoids massive leaps in the camera position when regaining focus
            try:
                focus_status = [event for event in events if event.type == pygame.ACTIVEEVENT][0]
                if focus_status.gain == 1:
                    last_x, last_y = pygame.mouse.get_pos()
            except IndexError:
                pass

            # mouse_x, mouse_y = pygame.mouse.get_pos()
            # mouse_d = [mouse_x-last_x, last_y-mouse_y]
            # self.camera.rotate(mouse_d[0], mouse_d[1], 0)
            # last_x = mouse_x
            # last_y = mouse_y

            print(self.camera)


    def update_camera(self):
        """
        Handles the moving of the camera based on the user input.
        """


if __name__ == "__main__":
    new_scene = Scene()
    new_scene.begin_scene((1000, 1000))
