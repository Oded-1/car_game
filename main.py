import pygame
import math
from methods import scale_image, blit_rotate_center, blit_text_center

# initalize pygame 
pygame.init()



# Loading images
map1 = scale_image(pygame.image.load("public/track1.png"), 0.9)
map1_border = scale_image(pygame.image.load("public/track1_border.png"), 0.9)

# main screen -> screen size (640,640)
screen = pygame.display.set_mode((map1.get_width(), map1.get_height()))
pygame.display.set_caption("Car Game")

# Loading images
red_car = scale_image(pygame.image.load("public/car_red.png").convert_alpha(), 0.15)

# Var for game loop
running = True
clock = pygame.time.Clock()
delta_time = 0.1


# For text
font = pygame.font.Font(None, size = 30)


class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 200
        self.friction = 2

    def rotate(self, left=False, right=False, dt=1):
        speed_ratio = abs(self.vel) / self.max_vel
        effective_rotation = self.rotation_vel * (1.2 - (speed_ratio * 0.4))
        if left:
            self.angle += effective_rotation*dt
        elif right:
            self.angle -= effective_rotation*dt

    def draw(self, scrn):
        blit_rotate_center(scrn, self.img, (self.x, self.y), self.angle)

    def move_forward(self, dt=1):
        accel_factor = (1 - (self.vel / self.max_vel))**.5
        self.vel = min(self.vel + self.acceleration*accel_factor*dt, self.max_vel)
        self.move(dt=dt)

    def move_backward(self, dt=1):
        if self.vel > 0:
            self.vel = max(self.vel - self.acceleration/20 , 0)
        else:
            self.vel = max(self.vel - self.acceleration*dt, -self.max_vel/2)
        self.move(dt=dt)

    def move(self, dt=1):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel *dt
        horizontal = math.sin(radians) * self.vel *dt

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0

class PlayerCar(AbstractCar):
    IMG = red_car
    START_POS = (50, 300)

    def reduce_speed(self, dt):
        if self.vel > 0:
            self.vel = max(self.vel - self.friction, 0)
        elif self.vel < 0:
            self.vel = min(self.vel + self.friction, 0)
        self.move(dt=dt)



def draw(scrn, imgs, player_car):
    for img, pos in imgs:
        scrn.blit(img, pos)
    player_car.draw(scrn)

    pygame.display.update()

def move_player(player_car, d_t):
    keysPressed = pygame.key.get_pressed()
    moved = False

    if keysPressed[pygame.K_LEFT] or keysPressed[pygame.K_a]:
        player_car.rotate(left=True, dt=d_t)
    if keysPressed[pygame.K_RIGHT] or keysPressed[pygame.K_d]:
        player_car.rotate(right=True, dt=d_t)
    if keysPressed[pygame.K_UP] or keysPressed[pygame.K_w]:
        moved = True
        player_car.move_forward(dt=d_t)
    if keysPressed[pygame.K_DOWN] or keysPressed[pygame.K_s]:
        moved = True
        player_car.move_backward(dt=d_t)

    if not moved:
        player_car.reduce_speed(dt =d_t)

# Varibles 
FPS = 60
images = [(map1, (0,0)), (map1_border, (0,0))]
player_car = PlayerCar(225, 200)  # pixels/sec   ,    degrees/sec

while running:
     # delta time normalizes lags/speeds of computer 
    delta_time = clock.tick(FPS)/1000
    delta_time = max(0.001, min(0.1, delta_time))   

    # check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    move_player(player_car, delta_time)


    # Check for key inputs
   


    # Update car position    
    

    # Set up hitboxes
    

    # Check collision
    
    # Respond to collision

    
    # Clear previous frame
    screen.fill((22,222,32))
    
    draw(screen, images, player_car)

    # Draw walls/hitboxes ~~~~~
    
    # Draw car onto surface - screen
    

    # Render and draw text on screen
    
    # Display all new changes to screen

    
    

pygame.quit()