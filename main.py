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

p = np.float64(0.0)  # Current position in the song in seconds

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

# Preload all the note audio files (assuming 'notes/{note}.wav' format for all notes)
note_audio_files = {}
for pitch in set(note[0] for note in note_list):  # Get unique pitches
    note_audio_files[pitch] = sa.WaveObject.from_wave_file(f"notes/{pitch}.wav")  # Preload the note


def play(note):
    # Load the piano note (wav file)
    note = AudioSegment.from_wav(f"notes/{note}.wav")

    # Export the note to a temporary wav file and play it
    note.export(f"temp_note{note}.wav", format="wav")
    wave_obj = sa.WaveObject.from_wave_file(f"temp_note{note}.wav")

    # Play the sound
    play_obj = wave_obj.play()

    # Wait until the sound finishes playing
    play_obj.wait_done()

# Main loop
while True:
    #print(movement)
    # Update p based on movement or time
    print(p)
    #each item in note_list: (pitch(C4=60), start time, duration)
    if movement[0]:
        p += 0.0333333333  # Move forward when UP key is held
    elif movement[1] and p > 0:
        p -= 1  # Move backward when DOWN key is held
    if p < 0:
        p = 0  # Prevent p from going negative

    # Time window: Last 0.033333 seconds
    time_window = 0.0333333333
    """
    # Check if a note's start time is within the last 0.033333 seconds
    while current_note_index < len(note_list) and p - time_window <= note_list[current_note_index][1] <= p:
        pitch, start, duration = note_list[current_note_index]
        play(pitch)
        current_note_index += 1
    """
    # Fill display
    display.fill('grey')





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
