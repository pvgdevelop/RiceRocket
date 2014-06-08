# program template for Spaceship
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
SCREEN_SIZE = [WIDTH, HEIGHT]
LIFE_POS = [30, 30]
SCORE_POS = [WIDTH / 2 - 50, 30]
HIGH_SCORE_POS = [WIDTH - 150, 30]
TEXT_SIZE = 30
TEXT_COLOR = "White"
score = 0
high_score = 0
lives = 3
time = 0.5
started = False


#Custom globals
fwd_const = 0.1 # Constant of forward vector
missile_const = 6 # Constant of forward vector
friction_const = 0.01 # Constant used to simulate friction
angle_vel_inc = 0.06 # Angle velocity increment
vol = 3
lvl_up = 1000


class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated


# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim

# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris = random.choice(['debris1_brown.png', 'debris2_brown.png', 'debris3_brown.png',
                        'debris4_brown.png', 'debris1_blue.png', 'debris2_blue.png',
                        'debris3_blue.png', 'debris4_blue.png'])
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/%s" % debris)

# nebula images - nebula_brown.png, nebula_blue.png
nebula = random.choice(['nebula_brown.png', 'nebula_blue.s2014.png'])
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/%s" % nebula)

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
shot = random.choice(['shot1.png', 'shot2.png', 'shot3.png'])
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/%s" % shot)

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")


# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]


def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)


def sum_coord(pos1, pos2, const=1):
    '''Return new position coordinates by adding their x and y coordinates'''
    return [p1 + p2 * const for p1, p2 in zip(pos1, pos2)]


NUM_DIMENSIONS = 2
def move(position, vector):
    '''Moves the position by the given vector in 2D toroidal space.'''
    for d in range(NUM_DIMENSIONS):
        position[d] = (position[d] + vector[d]) % SCREEN_SIZE[d]


def random_num(step=0.1, start=-10, stop=10):
    '''Generate a random number with given step from start to and including stop.
    Works with floats.
    Default range [-1, 1, 0.1]
    '''
    return  random.randrange(start, stop + 1) * step


# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.fire = False

    def draw(self,canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)

    def update(self):
        self.angle += self.angle_vel
        move(self.pos, self.vel) # Update the position

        self.vel[0] *= (1 - friction_const)
        self.vel[1] *= (1 - friction_const)

        if self.thrust:
            forward = angle_to_vector(self.angle)
            self.vel = sum_coord(self.vel, forward, fwd_const) # Accelerate when thrusting

            ship_thrust_sound.set_volume(0.3)
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.rewind()

    def get_position(self):
        return self.pos

    def get_radius(self):
        return self.radius

    def shoot(self):
        global missile_group
        forward = angle_to_vector(self.angle)
        #Adding missiles to a missile_group set when shooting
        missile_group.add(Sprite(sum_coord(self.pos, forward, self.radius),
                           sum_coord(self.vel, forward, missile_const),
                           self.angle, 0, missile_image, missile_info, missile_sound))


class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()

    def draw(self, canvas):

        self.update()
        if self.animated:
            global time_inc
            current_img_center = [self.image_center[0] + self.age * self.image_size[0],
                                  self.image_center[1]]
            canvas.draw_image(self.image, current_img_center,
                              self.image_size, self.pos,
                              self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center,
                              self.image_size, self.pos,
                              self.image_size, self.angle)

    def update(self):
        self.angle += self.angle_vel
        move(self.pos, self.vel)
        self.age += 1
        return self.age >= self.lifespan

    def get_position(self):
        return self.pos

    def get_radius(self):
        return self.radius

    def collide(self, other_object, safe_distance = 0):
        '''
        Return True if other_object collides with sprite
        safe_distance represents distance between 2 objects at wich collision accurs
        '''
        return dist(self.get_position(), other_object.get_position()) <= \
        self.get_radius() + other_object.get_radius() + safe_distance


def draw(canvas):
    global time, score, high_score, lives, started, rock_group, lvl_up
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw ship and sprites
    my_ship.draw(canvas)
    process_sprite_group(rock_group, canvas)
    process_sprite_group(missile_group, canvas)
    process_sprite_group(explosion_group, canvas)

    # update ship
    my_ship.update()

    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(),
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2],
                          splash_info.get_size())

    # Check for collision between ship and rocks
    if group_collide(rock_group, my_ship):
        lives -= 1
        if lives == 0:
            started = False
            rock_group = set([])
            soundtrack.rewind()
            if score > high_score:
                high_score = score

    # Check for collisions between missiles and rocks
    hits = group_group_collide(missile_group, rock_group)
    score += 50 * hits
    if score == lvl_up:
        lives += 1
        lvl_up += 1000

    canvas.draw_text("Lives", LIFE_POS, TEXT_SIZE, TEXT_COLOR)
    canvas.draw_text("SCORE", SCORE_POS, TEXT_SIZE, TEXT_COLOR)
    canvas.draw_text(str(score), sum_coord(SCORE_POS, [0, 30]), TEXT_SIZE, TEXT_COLOR)
    canvas.draw_text("High score:", HIGH_SCORE_POS, TEXT_SIZE, TEXT_COLOR)
    canvas.draw_text(str(high_score), sum_coord(HIGH_SCORE_POS, [0, 30]), TEXT_SIZE, TEXT_COLOR)
    for i in range(lives):
        canvas.draw_image(ship_image, [45, 45], [90, 90], sum_coord(LIFE_POS, [15 + 30 * i, 30]), [30, 30], -1.55)


def process_sprite_group(sprites_group, canvas):
    '''
    Helper function to draw set of sprites (rocks and missiles)
    and remove sprite if it's age exceeds its lifespan
    '''
    temp_sprites = set(sprites_group)
    for a_sprite in temp_sprites:
        a_sprite.update()
        if a_sprite.update(): # True if age is age >= lifespan
            sprites_group.remove(a_sprite)
        a_sprite.draw(canvas)


def group_collide(group, other_object):
    '''Return True if group of sprites collide with other object and removes sprite from the group'''
    global explosion_group
    temp_group = set(group)
    for item in temp_group:
        if item.collide(other_object):
            expl = random.choice(['explosion_orange.png', 'explosion_blue.png', 'explosion_blue2.png', 'explosion_alpha.png'])
            explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/%s" % expl)

            explosion = (Sprite(item.pos, item.vel, item.angle, item.angle_vel,
                        explosion_image, explosion_info, explosion_sound))
            explosion_group.add(explosion)
            group.remove(item)
            return True
    return False


def group_group_collide(group1, group2):
    copy_group1 = set(group1)
    hits = 0
    for item in copy_group1:
        if group_collide(group2, item):
            group1.discard(item)
            hits += 1
    return hits


# timer handler that spawns a rock
def rock_spawner():
    global rock_group
    #Increases velocity of the spawning rocks every 500 points
    add_vel_step = score // 500 * 0.01
    rock_pos = [random_num(1,0,WIDTH), random_num(1,0,HEIGHT)]
    rock_vel = [random_num(0.03 + add_vel_step),
                random_num(0.03 + add_vel_step)]

    asteroid = random.choice(['asteroid_blue.png', 'asteroid_brown.png', 'asteroid_blend.png'])
    if started and len(rock_group) < 12:
        asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/%s" % asteroid)

        a_rock = Sprite(rock_pos,rock_vel, 0, random_num(0.0004),
                        asteroid_image, asteroid_info)
        #If a_rock tries to spawn to close to the ship it is ignored
        if not a_rock.collide(my_ship, 50):
            rock_group.add(a_rock)


def keydown(key):
    if key == simplegui.KEY_MAP["up"]:
        my_ship.thrust = True
        my_ship.image_center[0] += my_ship.image_size[0]
    elif key == simplegui.KEY_MAP["right"]:
        my_ship.angle_vel += angle_vel_inc
    elif key == simplegui.KEY_MAP["left"]:
        my_ship.angle_vel -= angle_vel_inc
    elif key == simplegui.KEY_MAP["space"]:
        my_ship.shoot()


def keyup(key):
    if key == simplegui.KEY_MAP["up"]:
        my_ship.thrust = False
        my_ship.image_center[0] -= my_ship.image_size[0]
    elif key == simplegui.KEY_MAP["right"]:
        my_ship.angle_vel -= angle_vel_inc
    elif key == simplegui.KEY_MAP["left"]:
        my_ship.angle_vel += angle_vel_inc


def restart():
    '''Resets the lives and score'''
    global lives, score
    soundtrack.set_volume(0.3)
    soundtrack.play()
    lives = 3
    score = 0
    my_ship.pos = [WIDTH / 2, HEIGHT / 2]
    my_ship.vel = [0, 0]


# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started, score
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        restart()


# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
rock_group = set([])
missile_group = set([])
explosion_group = set([])

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()