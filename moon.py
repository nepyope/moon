from moonutils import *
import launchpad_py as launchpad
from pygame import time

def button_mapping(button_code):
    special_buttons = { 
        200: "Special: Special Button 1",
        201: "Special: Special Button 2",
        202: "Special: Special Button 3",
        203: "Special: Special Button 4",
        204: "Special: Scene Launch Button 5",
        205: "Special: Scene Launch Button 6",
        206: "Special: Scene Launch Button 7",
        207: "Special: Scene Launch Button 8",
        120: "Special: Quit",
    }
    # Main grid buttons
    if button_code in range(0, 88+32):
        # Calculate x, y coordinates for the main grid buttons
        x = button_code % 8
        y = button_code // 16+1
        return x, y
    else:
        return special_buttons.get(button_code, "Unknown button")


def load_audio_segment(file_path, start_ms, end_ms):
    song = AudioSegment.from_mp3(file_path)
    segment = song[start_ms:end_ms]
    return segment

chunk_num = 64
chunk_length = 12000
# Define audio segment time ranges for each special button
special_button_time_ranges = {
    200: (0, chunk_length),        # Special Button 1: 0-10 seconds
    201: (chunk_length, chunk_length*2),        # Special Button 2: 10-20 seconds
    202: (chunk_length*2, chunk_length*3),        # Special Button 3: 20-30 seconds
    203: (chunk_length*3, chunk_length*4),        # Special Button 4: 30-40 seconds
    204: (chunk_length*4, chunk_length*5),        # Scene Launch Button 5: 40-50 seconds
    205: (chunk_length*5, chunk_length*6),        # Scene Launch Button 6: 50-60 seconds
    206: (chunk_length*6, chunk_length*7),        # Scene Launch Button 7: 60-70 seconds
    207: (chunk_length*7, chunk_length*8),        # Scene Launch Button 8: 70-80 seconds
}

def main():
    # Load and slice the audio file
    audio_chunks = load_and_slice_audio('moon.mp3', 64,[0,10000])
    #load all the audio chunks given special button time ranges
    sections = []
    for range in special_button_time_ranges.values():
        sections.append(load_and_slice_audio('moon.mp3', 64, range))
    
    # create an instance
    lp = launchpad.Launchpad()
    if lp.Open():
        print("Launchpad Mk1/S/Mini")
    else:
        print("Did not find a Launchpad Mk1/S/Mini.")
        return
    
    while True:
        # Check for button events
        events = lp.ButtonStateRaw()
        if events:
            button = button_mapping(events[0])
            if type(button) == tuple and events[1]:  # Button is pressed
                x, y = button
                chunk_index = y * 8 + x
                print(chunk_index)
                avg_freq, loudness = play_chunk(audio_chunks[chunk_index-8])

                # Map avg_freq to red color intensity (r) and loudness to green color intensity (g)
                r = int(np.interp(avg_freq, [20, 20000], [0, 7]))  # Example range (20Hz to 2000Hz)
                g = int(np.interp(loudness, [-20, 0], [7, 0]))    # Example range (-60dB to 0dB)

                lp.LedCtrlXY(x, y, r, g)  # Set LED color based on avg frequency and loudness
            else:
                print(button)
                if events[1]:  # Button is pressed
                    range = special_button_time_ranges.get(events[0], (0, 10000))
                    audio_chunks = sections[events[0]-200]
                    lp.LedCtrlRaw(events[0], 7, 7)  # Turn on the LED with blue color
                else:  # Button is released
                    lp.LedCtrlRaw(events[0], 0, 0)  # Turn off the LED

        time.wait(5)

if __name__ == '__main__':
    main()