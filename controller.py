from camera import *
from item import *
import pygame
import threading
import sys


class Scene:
    def __init__(self, ):
        """
        Initializes a new scene.  By default, puts one object in and sets up everything in the correct positions.
        """
        self.world = World()
        self.camera = Camera(init_pos=[0, 0, 0], init_angle=[0, 0, 0], init_fov=.5*3.14)
        self.renderer = Renderer(self.camera)
        self.running = True

    def begin_scene(self, window_size=(1000, 1000)):
        """
        Begins the rendering and user input MVC process.
        """
        thread_lock = threading.Lock()
        canvas = pygame.display.set_mode(window_size, 0, 32)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)  # Only uncomment this if you're SURE it won't break everything
        render_thread = threading.Thread(target=self.render_cycle, args=(canvas,thread_lock,))
        render_thread.start()

        input_thread = threading.Thread(target=self.get_user_input, args=(thread_lock,))
        input_thread.start()

    def render_cycle(self, canvas, lock):
        """
        handles the continuous cycle of rendering each frame.
        """
        pygame.init()
        clock = pygame.time.Clock()
        while self.running:
            lock.acquire()
            self.renderer.draw_scene(self.world, self.camera, canvas)
            lock.release()
            clock.tick(10)  # FPS

    def get_user_input(self, lock):
        """
        Gets the input from the user.
        """

        event_keys = (pygame.K_w, pygame.K_s, pygame.K_d, pygame.K_a)
        keys_pressed = [0, 0, 0, 0]  # The pressed status of the keys
        mouse_x, mouse_y = pygame.mouse.get_pos()
        on_screen = True
        is_grabbed = True


        while self.running:
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    print("Quitting...")

            # Jesus take the wheel, hope this doesn't break everything

            down_keys = [event.key for event in events if event.type == pygame.KEYDOWN]
            up_keys = [event.key for event in events if event.type == pygame.KEYUP]
            for idx in range(4):
                keys_pressed[idx] += int(event_keys[idx] in down_keys) - int(event_keys[idx] in up_keys)
            self.camera.move((keys_pressed[2]-keys_pressed[3], 0, keys_pressed[0]-keys_pressed[1]), speed=0.0001)

            # This block avoids massive leaps in the camera position when regaining focus
            try:
                focus_status = [event for event in events if event.type == pygame.ACTIVEEVENT][0]
                if focus_status.gain == 1:
                    on_screen = True
                else:
                    is_grabbed = False
                    on_screen = False
            except IndexError:
                pass

            if on_screen and pygame.mouse.get_pressed()[0] and not is_grabbed:
                is_grabbed = True
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)

            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.event.set_grab(False)
                        is_grabbed = False
                        pygame.mouse.set_visible(True)

            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_d = [mouse_x-500, 500-mouse_y]
            if is_grabbed:
                lock.acquire()
                self.camera.rotate(mouse_d[0], -mouse_d[1], 0, sensitivity=.01)
                lock.release()
                pygame.mouse.set_pos(500, 500)


            # print(self.camera)

        # On quit, gracefully exit
        pygame.quit()
        sys.exit()

    def update_camera(self):
        """
        Handles the moving of the camera based on the user input.
        """


if __name__ == "__main__":
    new_scene = Scene()
    new_scene.begin_scene((1000, 1000))
