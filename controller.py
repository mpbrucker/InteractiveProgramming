from world import World
from camera import Camera
from renderer import Renderer
from item import Item
import pygame
import threading
import sys


class Scene:
    def __init__(self, window_size=(1000, 1000)):
        """
        Initializes a new scene.  By default, puts one object in and sets up everything in the correct positions.
        """
        self.window_size = window_size
        self.world = World()
        self.world.gen_random_scene(1,3)
        self.world.add_item(Item('cube.stl', (0, .5, .5), (0, 0, 0), 1, color=(255, 255, 0)))
        self.camera = Camera(init_pos=[0, 1, -10], init_angle=[0, 0, 0], init_fov=1.57)
        self.renderer = Renderer(self.camera, window_size)
        self.running = False

    def begin_scene(self):
        """
        Begins the rendering and user input MVC process.
        """
        thread_lock = threading.Lock()
        canvas = pygame.display.set_mode(self.window_size, 0, 32)
        pygame.mouse.set_visible(False)
        # pygame.event.set_grab(True)  # Only uncomment this if you're SURE it won't break everything
        render_thread = threading.Thread(target=self.render_cycle, args=(canvas, thread_lock,))
        render_thread.start()

        input_thread = threading.Thread(target=self.handle_user_input, args=(thread_lock,))
        input_thread.start()

    def render_cycle(self, canvas, lock):
        """
        handles the continuous cycle of rendering each frame.
        """
        pygame.init()
        clock = pygame.time.Clock()
        self.running = True
        # try:
        while self.running:
            lock.acquire()  # Acquire lock, otherwise things get weird
            self.renderer.draw_scene(self.world, canvas)
            lock.release()
            clock.tick(60)  # FPS
            # print(self.camera.angle)

    def handle_user_input(self, lock):
        """
        Gets the input from the user.
        """
        event_keys = (pygame.K_w, pygame.K_s, pygame.K_d, pygame.K_a)
        keys_pressed = [0, 0, 0, 0]  # The pressed status of the keys
        on_screen = True
        is_grabbed = True
        pygame.mouse.set_pos(500, 500)  # Avoids vew jumping on focus gain

        while True:
            if self.running:
                try:  # Exception handling so that we can let go of inputs if need be

                    # Gets input from keyboard/mouse, and updates camera based on it
                    events = pygame.event.get()
                    down_keys = [event.key for event in events if event.type == pygame.KEYDOWN]
                    up_keys = [event.key for event in events if event.type == pygame.KEYUP]
                    for idx in range(4):
                        keys_pressed[idx] += int(event_keys[idx] in down_keys) - int(event_keys[idx] in up_keys)

                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    mouse_d = [mouse_x-500, 500-mouse_y]

                    if is_grabbed:
                        self.update_camera(keys_pressed, mouse_d, lock)

                    # This block handles updating of window focus
                    try:
                        focus_status = [event for event in events if event.type == pygame.ACTIVEEVENT][0]
                        if focus_status.gain == 1:
                            on_screen = True  # If focus on window is regained
                        else:
                            is_grabbed = False
                            on_screen = False
                    except IndexError:
                        pass

                    # If the screen is grabbed, update vars/move the mouse
                    if on_screen and pygame.mouse.get_pressed()[0] and not is_grabbed:
                        is_grabbed = True
                        pygame.event.set_grab(True)
                        pygame.mouse.set_visible(False)
                        pygame.mouse.set_pos(500, 500)  # Avoids vew jumping on focus gain

                    for event in events:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_q:  # If Q is pressed, let go of inputs
                                pygame.event.set_grab(False)
                                is_grabbed = False
                                pygame.mouse.set_visible(True)

                        if event.type == pygame.QUIT:
                            self.running = False
                            print("Quitting...")
                            break

                except Exception as e:
                    pygame.event.set_grab(False)
                    print(str(e))

        # On quit, gracefully exit
        pygame.quit()
        sys.exit()

    def update_camera(self, keys, mouse_d, lock):
        """
        Handles the moving of the camera based on the user input.
        """
        lock.acquire()  # Acquire lock to make sure multithreading things don't get messed up
        self.camera.rotate(mouse_d[0], -mouse_d[1], 0, sensitivity=.001)
        self.camera.move((keys[2]-keys[3], 0, keys[0]-keys[1]), speed=0.001)
        lock.release()
        pygame.mouse.set_pos(500, 500)


if __name__ == "__main__":
    new_scene = Scene()
    new_scene.begin_scene()
