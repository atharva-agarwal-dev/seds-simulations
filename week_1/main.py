#start of program

#import lib(s)
import pygame
import numpy as np
import random

#config
WIDTH = 800
HEIGHT = 800

BOWL_CENTER = np.array([WIDTH / 2, HEIGHT / 2], dtype=float)
BOWL_RADIUS = 300

#particle properties
NUM_PARTICLES = 5
PARTICLE_RADIUS = 12
PARTICLE_SPEED = 150.0

GRAVITY = 900.0

#energy loss
WALL_RESTITUTION = 1.0
RESTITUTION = 1.0

#frame rate
FPS = 60

positions = []
velocities = []

for i in range(NUM_PARTICLES):

    #random positon and direction for partical
    angle = random.uniform(0, 2 * np.pi)
    distance = random.uniform(0, BOWL_RADIUS - PARTICLE_RADIUS)

    positions.append(BOWL_CENTER + distance * np.array([np.cos(angle),np.sin(angle)]))

    #swap for np.array([0.0, 0.0]) to drop the ball from rest.
    angle = random.uniform(0, 2 * np.pi)

    velocities.append(PARTICLE_SPEED * np.array([np.cos(angle),np.sin(angle)]))

#pygame setup

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Particle Simulation")

clock = pygame.time.Clock()

#----------extra: added text to diplay number of collsions--------
font = pygame.font.SysFont("Times New Roman", 44)
wbcount = 0 #wall ball collision count
bbcount = 0 #ball ball collision count
#-----------------------------------------------------------------

running = True

#Main loop

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    #Seconds since the last frame. This is your timestep.
    dt = clock.tick(FPS) / 1000.0
    
    
    #accounting for gravity and wall collisions

    for i in range(len(positions)):
        velocities[i][1] += GRAVITY * dt
        positions[i] += velocities[i] * dt

        offset = positions[i] - BOWL_CENTER
        distance = np.linalg.norm(offset)

        if distance > BOWL_RADIUS - PARTICLE_RADIUS:
            normal = offset / distance

            #----Extra-----
            wbcount += 1
            #--------------


            positions[i] = BOWL_CENTER + normal * (BOWL_RADIUS - PARTICLE_RADIUS)

            v_n = np.dot(velocities[i], normal)
            if v_n > 0:
                velocities[i] -= (1 + WALL_RESTITUTION) * v_n * normal


    
    #accounting for ball-ball collisions

    n = len(positions)
    for i in range(n):
        for j in range(i + 1, n):
            delta = positions[i] - positions[j]
            distance = np.linalg.norm(delta)
            if distance < 2 * PARTICLE_RADIUS:
                normal = delta / distance

                relative_velocity = velocities[i] - velocities[j]
                v_n = np.dot(relative_velocity, normal)

                if v_n < 0:  # only resolve real, approaching collisions
                    correction = 0.5 * (1 + RESTITUTION) * v_n * normal
                    velocities[i] -= correction
                    velocities[j] += correction

                    #----Extra-----
                    bbcount += 1
                    #--------------

                overlap = 2 * PARTICLE_RADIUS - distance
                positions[i] += (overlap / 2) * normal
                positions[j] -= (overlap / 2) * normal

    #rendering

    screen.fill((255, 200, 87))

    pygame.draw.circle(
        screen,
        (115, 107, 96),
        BOWL_CENTER.astype(int),
        BOWL_RADIUS,
        width=3
    )

    for position in positions:
        pygame.draw.circle(
            screen,
            (75, 66, 55),
            position.astype(int),
            PARTICLE_RADIUS
        )
    #----------extra: added text to diplay number of collsions--------
    text_string = f"Wall collisions : {wbcount} | Ball collisions : {bbcount}"
    text_surface = font.render(text_string, True, (75, 66, 55))
    screen.blit(text_surface, (20, 15))
    #------------------------------------------------------------------

    pygame.display.flip()

pygame.quit()

#end of program