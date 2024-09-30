import pygame
import pretty_midi
import time, json
#import simpleaudio as sa
#from pydub import AudioSegment
import numpy as np


# Initialize Pygame
pygame.init()
pygame.display.set_caption("RUR-Editor by Luke Cardoza")
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
display = pygame.Surface((WIDTH // 2, HEIGHT // 2))  # Smaller surface to render onto and scale everything up
clock = pygame.time.Clock()
bg = pygame.image.load('bg.png').convert()
bg = pygame.transform.scale(bg, (500, 500))
bg_rect = bg.get_rect(center=(250, 0))

p = 0  # Current position in the song in seconds
note_to_str = {
    21: "A0", 22: "A#0", 23: "B0",
    24: "C1", 25: "C#1", 26: "D1", 27: "D#1", 28: "E1", 29: "F1", 30: "F#1", 31: "G1", 32: "G#1", 33: "A1", 34: "A#1", 35: "B1",
    36: "C2", 37: "C#2", 38: "D2", 39: "D#2", 40: "E2", 41: "F2", 42: "F#2", 43: "G2", 44: "G#2", 45: "A2", 46: "A#2", 47: "B2",
    48: "C3", 49: "C#3", 50: "D3", 51: "D#3", 52: "E3", 53: "F3", 54: "F#3", 55: "G3", 56: "G#3", 57: "A3", 58: "A#3", 59: "B3",
    60: "C4", 61: "C#4", 62: "D4", 63: "D#4", 64: "E4", 65: "F4", 66: "F#4", 67: "G4", 68: "G#4", 69: "A4", 70: "A#4", 71: "B4",
    72: "C5", 73: "C#5", 74: "D5", 75: "D#5", 76: "E5", 77: "F5", 78: "F#5", 79: "G5", 80: "G#5", 81: "A5", 82: "A#5", 83: "B5",
    84: "C6", 85: "C#6", 86: "D6", 87: "D#6", 88: "E6"
}


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
#current_note_index = 0  # Keep track of the current note being checked

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
    
# Preload all the note audio files
note_audio_files = {}
for pitch in set(note[0] for note in note_list):  # Get unique pitches
    try:
        sound = pygame.mixer.Sound(f"notes/{pitch}.wav")  # Preload the note
        note_audio_files[pitch] = sound
        print(f"Loaded note: notes/{pitch}.wav")
    except Exception as e:
        print(f"Error loading note {pitch}: {e}")

def play(note):
    sound = note_audio_files.get(note)
    if sound and note in note_audio_files.keys():
        sound.play()
    else:
        print(f"Warning: No audio file loaded for note {note}")
def display_text():
    print(f"#{p}\tCurrent note: {note_to_str[note_list[p][0]]} ({note_list[p][0]})\tArrows: {'None.' if list(output_json[f"note{p}"]["arrows"]) == [] else list(output_json[f"note{p}"]["arrows"])}\tElapsed: {note_list[p][1].item()}"
          +f"\nPress 'E' to edit arrows on current note, and 'O' to output and save.")
def save():
    path=input("Enter the file name (without extension). Press Enter to cancel.\n")
    if path=='':
        print("Save cancelled.")
        return
    f = open(f"{path}.json", "w")
    json.dump(output_json, f)
    f.close()
    print(f"File saved to {path}.json")
    return
output_json={}
for n in range(len(note_list)):
    pitch, start, duration = note_list[n]
    temp = {
        "pitch": pitch,
        "start": start,
#        "duration": duration,
        "arrows": []
    }
    output_json[f"note{n}"]=temp
#print(json.dumps(output_json))
first_up_press = True
e=False
o=False
r=False
edit_mode = False
# Main loop
while True:
    if movement[0]: # Up arrow pressed
        if edit_mode:
            print("Exited Edit Mode. ")
            edit_mode = False
        if not first_up_press:
            p = p+1 if p <len(note_list)-1 else p  # Move forward when UP key is pressed
        else:
            first_up_press = False
        display_text()
        play(note_list[p][0])
        movement[0] = False
    elif movement[1] and p > 0: # Down arrow pressed
        if edit_mode:
            print("Exited Edit Mode. ")
            edit_mode = False
        p = p-1 if p>0 else p  # Move backward when DOWN key is pressed and don't go below zero
        display_text()
        play(note_list[p][0])
        movement[1] = False
    if(e): # if e pressed, enable/disable edit mode
        if not edit_mode:
            print(f"Editing arrows of note: {note_to_str[note_list[p][0]]}. Press 'R' to remove arrow(s). Press 'E' again to exit.")
            edit_mode = True
        else:
            print("Exited Edit Mode. ")
            edit_mode = False
        e = False
    if(edit_mode):
        if(r):
            rmv=input("Remove which note (press Enter to cancel)? \n")
            if rmv == "":
                print("Removal cancelled. ")
                r=False
            elif rmv in ('up', 'down', 'left', 'right'):
                arrow_set = set(output_json[f"note{p}"]["arrows"])
                if rmv in arrow_set:
                    arrow_set.remove(rmv)
                    output_json[f"note{p}"]["arrows"]=arrow_set
                    print("Note removed. ")
                    r=False
                else:
                    print(f"{rmv} is not in note {note_to_str[note_list[p][0]]}. ")
                    # r remains True - ask again
            else:
                print(f"{rmv} is not a valid arrow. Please enter either: 'up', 'down', 'left', or 'right'. ")
                # r remains True - ask again
        if current_arrow != '':
            # if the user presses a WASD key in edit mode, add it to the output_json note's arrows (list-set thing prevents duplicates.)
            print(f"Added: {current_arrow}. ")
            arrow_set = set(output_json[f"note{p}"]["arrows"])
            arrow_set.add(current_arrow)
            output_json[f"note{p}"]["arrows"]=list(arrow_set)
    if(r and not edit_mode):
        r = False
    if(o): # if o pressed, output the file
        if edit_mode:
            print("Exited Edit Mode. ")
            edit_mode = False
        save()
        o = False


    
    # Fill display
    display.fill('grey')
    display.blit(bg, bg_rect)

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
            if event.key == pygame.K_e:
                e = True
            if event.key == pygame.K_o:
                o = True
            if event.key == pygame.K_r:
                r = True

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
