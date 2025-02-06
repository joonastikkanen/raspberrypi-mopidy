import curses
import time
import requests
import RPi.GPIO as GPIO

# Setup GPIO
BUTTON_PIN = 17  # Change this to the correct pin number

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def get_current_song():
    try:
        response = requests.post("http://localhost:6680/mopidy/rpc", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "core.playback.get_current_track"
        })
        data = response.json()
        track = data.get("result", None)
        if track:
            artist_name = track["artists"][0]["name"] if "artists" in track and track["artists"] else "Unknown Artist"
            title = track.get("name", "Unknown Title")
            return f"{artist_name} - {title}"
        return "No song playing"
    except Exception as e:
        return f"Error: {e}"

def next_song(channel):
    try:
        requests.post("http://localhost:6680/mopidy/rpc", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "core.playback.next"
        })
    except Exception as e:
        print(f"Error: {e}")

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(1000)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

    # Add event detection for the button
    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=next_song, bouncetime=300)
    
    while True:
        stdscr.clear()
        stdscr.attron(curses.color_pair(1))
        song = get_current_song()
        height, width = stdscr.getmaxyx()
        x = width // 2 - len(song) // 2
        y = height // 2
        stdscr.addstr(y, max(x, 0), song)
        stdscr.attroff(curses.color_pair(1))
        stdscr.refresh()
        
        key = stdscr.getch()
        if key == ord('q'):
            break

    # Cleanup GPIO
    GPIO.cleanup()

if __name__ == "__main__":
    curses.wrapper(main)
