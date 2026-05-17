import serial
import speech_recognition as sr

# Replace 'COM3' with your actual Arduino port
arduino = serial.Serial('COM3', 9600)
recognizer = sr.Recognizer()
mic = sr.Microphone()

print("Say 'light on' or 'light off'...")

while True:
    with mic as source:
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print("You said:", command)

        if "light on" in command:
            arduino.write(b'1')
        elif "light off" in command:
            arduino.write(b'0')
    except:
        print("Sorry, could not understand.")
