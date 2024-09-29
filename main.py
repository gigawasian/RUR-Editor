import pygame
import pretty_midi
import time
import simpleaudio as sa
from pydub import AudioSegment
import numpy as np

# Initialize Pygame
pygame.init()
pygame.display.set_caption("RU Revolution Editor by Luke Cardoza")
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
display = pygame.Surface((WIDTH // 2, HEIGHT // 2))  # Smaller surface to render onto and scale everything up
clock = pygame.time.Clock()

p = 0.00  # Current position in the song in seconds

# Initialize Pygame mixer
pygame.mixer.init()

midi_file = "test.mid"  # Replace with your MIDI file path

# Load the MIDI file with pretty_midi
midi_data = pretty_midi.PrettyMIDI(midi_file)

# Extract notes into a list (pitch(C4=60), start time, duration)
note_list = []
for instrument in midi_data.instruments:
    if not instrument.is_drum and instrument.program == 0:  # Piano instrument
        for note in instrument.notes:
            note_list.append((note.pitch, note.start, note.end - note.start))

# Sort notes by start time
note_list.sort(key=lambda x: x[1])

movement = [False, False]  # Up, Down
current_arrow = ""  # 'up', 'left', 'down', or 'right'
current_note_index = 0  # Keep track of the current note being checked

scroll = 0  # up/down

# Load arrow images
arrow_img = [
    pygame.image.load("UP.png"),
    pygame.image.load("LEFT.png"),
    pygame.image.load("DOWN.png"),
    pygame.image.load("RIGHT.png")
]
# Convert images to have per-pixel alpha (if needed)
for i in range(len(arrow_img)):
    arrow_img[i] = arrow_img[i].convert_alpha()



# Main loop
while True:
    #print(movement)
    # Update p based on movement or time
    if movement[0]:
        p += 1  # Move forward when UP key is held
    elif movement[1] and p > 0:
        p -= 1  # Move backward when DOWN key is held

    # Fill display
    display.fill('grey')

    #each item in note_list: (pitch(C4=60), start time, duration)
    print(note_list)

    if p < 0:
        p = 0  # Prevent p from going negative


    # Handle arrow display
    if current_arrow == "up":
        cimg = arrow_img[0]
    elif current_arrow == "left":
        cimg = arrow_img[1]
    elif current_arrow == "down":
        cimg = arrow_img[2]
    elif current_arrow == "right":
        cimg = arrow_img[3]
    else:
        cimg = None

    if cimg:
        display.blit(cimg, (200, 200))

    # Only allow the key press for one frame at a time to prevent repeats
    current_arrow = ''


    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                movement[0] = True
            if event.key == pygame.K_DOWN:
                movement[1] = True
            if event.key == pygame.K_w:
                current_arrow = "up"
            if event.key == pygame.K_a:
                current_arrow = "left"
            if event.key == pygame.K_s:
                current_arrow = "down"
            if event.key == pygame.K_d:
                current_arrow = "right"

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                movement[0] = False
            if event.key == pygame.K_DOWN:
                movement[1] = False
            if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                current_arrow = ""

    # Update display
    screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))
    pygame.display.update()
