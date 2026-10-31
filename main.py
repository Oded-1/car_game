import pygame
import math
from methods import scale_image, blit_rotate_center, blit_text_center, draw_skid_mark

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
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 300
        self.brake_power = 500
        self.friction = 60
        # forward_speed is the car's own notion of "how hard the engine/brakes
        # are pushing it along the direction it's facing". velocity is the
        # actual world-space velocity, which only catches up to forward_speed
        # at a finite rate (grip) -> when they diverge during a turn, the car
        # visibly slides instead of snapping onto the new heading.
        self.forward_speed = 0.0
        self.velocity = pygame.Vector2(0, 0)
        self.max_grip = 24.0
        self.min_grip = 11.0
        # handbrake: player-controlled drift, rather than the passive grip-loss above.
        self.handbrake_active = False
        self.handbrake_grip = 3.0
        self.handbrake_drag = 150
        self.handbrake_turn_boost = 1.25

    def rotate(self, left=False, right=False, dt=1):
        speed_ratio = min(abs(self.forward_speed) / self.max_vel, 1)
        # steering stays crisp at low speed and falls off sharply (not linearly)
        # as the car approaches top speed, like a real car's steering authority.
        steer_factor = 1 - (speed_ratio ** 2.2) * 0.35
        if self.handbrake_active:
            steer_factor *= self.handbrake_turn_boost
        effective_rotation = self.rotation_vel * steer_factor
        if left:
            self.angle += effective_rotation*dt
        elif right:
            self.angle -= effective_rotation*dt

    def draw(self, scrn):
        blit_rotate_center(scrn, self.img, (self.x, self.y), self.angle)

    def move_forward(self, dt=1):
        speed_ratio = max(0, self.forward_speed) / self.max_vel
        # torque-curve-like accel: strong push low/mid range, sharp taper near max speed.
        accel_factor = 1 - speed_ratio ** 3
        self.forward_speed = min(self.forward_speed + self.acceleration*accel_factor*dt, self.max_vel)
        self.move(dt=dt)

    def move_backward(self, dt=1):
        if self.forward_speed > 0:
            self.forward_speed = max(self.forward_speed - self.brake_power*dt, 0)
        else:
            reverse_max = self.max_vel / 2
            speed_ratio = max(0, -self.forward_speed) / reverse_max
            accel_factor = 1 - speed_ratio ** 3
            self.forward_speed = max(self.forward_speed - self.acceleration*0.6*accel_factor*dt, -reverse_max)
        self.move(dt=dt)

    def move(self, dt=1):
        if self.handbrake_active:
            # a locked rear wheel scrubs off speed; throttle can still fight this
            # if held at the same time, giving a classic power-slide.
            if self.forward_speed > 0:
                self.forward_speed = max(self.forward_speed - self.handbrake_drag*dt, 0)
            elif self.forward_speed < 0:
                self.forward_speed = min(self.forward_speed + self.handbrake_drag*dt, 0)

        radians = math.radians(self.angle)
        heading = pygame.Vector2(-math.sin(radians), -math.cos(radians))
        target_velocity = heading * self.forward_speed

        if self.handbrake_active:
            # grip collapses to a flat low value -> the slip angle (how far the
            # heading has pulled away from actual travel direction) can grow
            # large, and the player steers that angle directly: more steer-in
            # widens the slide, countersteer narrows it.
            grip = self.handbrake_grip
        else:
            # near-instant (glued) at low speed, sluggish (drifty) at high speed.
            speed_ratio = min(self.velocity.length() / self.max_vel, 1)
            grip = self.max_grip - (self.max_grip - self.min_grip) * speed_ratio
        self.velocity = self.velocity.lerp(target_velocity, min(grip * dt, 1))

        self.x -= self.velocity.x * dt
        self.y -= self.velocity.y * dt

    def slip_angle(self):
        if self.velocity.length() < 10:
            return 0.0
        radians = math.radians(self.angle)
        heading = pygame.Vector2(-math.sin(radians), -math.cos(radians))
        angle = abs(self.velocity.angle_to(heading))
        return min(angle, 360 - angle)

    def is_drifting(self, threshold_degrees=12):
        return self.slip_angle() > threshold_degrees

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.forward_speed = 0.0
        self.velocity = pygame.Vector2(0, 0)

class PlayerCar(AbstractCar):
    IMG = red_car
    START_POS = (50, 300)

    def reduce_speed(self, dt):
        # rolling resistance plus a speed-proportional drag term, so coasting
        # bleeds off speed faster at high speed than at a crawl (non-linear).
        drag = self.friction + abs(self.forward_speed) * 0.15
        if self.forward_speed > 0:
            self.forward_speed = max(self.forward_speed - drag*dt, 0)
        elif self.forward_speed < 0:
            self.forward_speed = min(self.forward_speed + drag*dt, 0)
        self.move(dt=dt)



def draw(scrn, imgs, player_car, skid_marks):
    for img, pos in imgs:
        scrn.blit(img, pos)

    for mark in skid_marks:
        fade = max(mark["life"] / mark["max_life"], 0)
        draw_skid_mark(scrn, mark["pos"], mark["angle"], int(mark["alpha"] * fade))

    player_car.draw(scrn)

    if player_car.handbrake_active and player_car.is_drifting():
        blit_text_center(scrn, font, "DRIFTING")

    pygame.display.update()

def update_skid_marks(skid_marks, player_car, dt):
    for mark in skid_marks:
        mark["life"] -= dt
    skid_marks[:] = [m for m in skid_marks if m["life"] > 0]

    slip = player_car.slip_angle()
    if slip > 5 and player_car.velocity.length() > 30:
        radians = math.radians(player_car.angle)
        heading = pygame.Vector2(-math.sin(radians), -math.cos(radians))
        side = pygame.Vector2(heading.y, -heading.x) * (player_car.img.get_width() * 0.28)
        rear_center = (pygame.Vector2(player_car.x, player_car.y)
                       + pygame.Vector2(player_car.img.get_width(), player_car.img.get_height()) / 2
                       - heading * (player_car.img.get_height() * 0.4))

        intensity = min(slip / 40, 1)
        # a locked handbrake slide leaves dark rubber; plain cornering at speed
        # only leaves a faint scuff.
        alpha = int((90 + 120 * intensity) if player_car.handbrake_active else 40 * intensity)

        for wheel_offset in (side, -side):
            skid_marks.append({
                "pos": rear_center + wheel_offset,
                "angle": player_car.angle,
                "life": 1.2,
                "max_life": 1.2,
                "alpha": alpha,
            })

    if len(skid_marks) > 400:
        del skid_marks[:-400]

def move_player(player_car, d_t):
    keysPressed = pygame.key.get_pressed()
    moved = False

    player_car.handbrake_active = keysPressed[pygame.K_SPACE]

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
player_car = PlayerCar(225, 210)  # pixels/sec   ,    degrees/sec
skid_marks = []

while running:
     # delta time normalizes lags/speeds of computer 
    delta_time = clock.tick(FPS)/1000
    delta_time = max(0.001, min(0.1, delta_time))   

    # check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    move_player(player_car, delta_time)
    update_skid_marks(skid_marks, player_car, delta_time)


    # Check for key inputs
   


    # Update car position    
    

    # Set up hitboxes
    

    # Check collision
    
    # Respond to collision

    
    # Clear previous frame
    screen.fill((22,222,32))
    
    draw(screen, images, player_car, skid_marks)

    # Draw walls/hitboxes ~~~~~
    
    # Draw car onto surface - screen
    

    # Render and draw text on screen
    
    # Display all new changes to screen

    
    

pygame.quit()