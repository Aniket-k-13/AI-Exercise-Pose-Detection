import tkinter as tk
from tkinter import ttk
import datetime
import os
import threading

class FitDeskApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("FitDesk - Lunges Exercise")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Theme setup
        self.theme = {
            "bg": "#FFFFFF", "fg": "#333333",
            "button_bg": "#3498db", "button_fg": "#FFFFFF",
            "highlight": "#e6f3fb", "border": "#d1d1d1"
        }
        
        # Container for pages
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Store frames
        self.frames = {}
        for F in (MenuPage, MyExercisesPage, LiveExercisePage):
            frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("MenuPage")
    
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.configure(bg=self.theme["bg"])
        frame.tkraise()
    
    def speak(self, text):
        """Voice feedback for exercises using Windows SAPI"""
        def speak_thread():
            try:
                # Try pyttsx3 first
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.say(text)
                engine.runAndWait()
            except:
                # Fallback to Windows SAPI
                try:
                    os.system(f'powershell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak(\'{text}\')"')
                except:
                    # If all else fails, just print
                    print(f"Voice: {text}")
        
        # Run in separate thread to prevent GUI freezing
        thread = threading.Thread(target=speak_thread)
        thread.daemon = True
        thread.start()

class BasePage(tk.Frame):
    """Base class for all pages"""
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.create_widgets()
    
    def create_widgets(self):
        pass

class MenuPage(BasePage):
    """Main menu page"""
    def create_widgets(self):
        self.configure(bg=self.controller.theme["bg"])
        
        # Header
        tk.Label(self, text="FitDesk", font=("Arial", 32, "bold"), 
                bg=self.controller.theme["bg"], fg=self.controller.theme["fg"]).pack(pady=30)
        
        tk.Label(self, text="Your Personal Exercise Assistant", font=("Arial", 14), 
                bg=self.controller.theme["bg"], fg="gray").pack(pady=10)
        
        # Single exercise button
        exercise_btn = tk.Button(self, text="Start Lunges Exercise", font=("Arial", 14), 
                               bg=self.controller.theme["button_bg"], fg=self.controller.theme["button_fg"],
                               width=25, height=2, relief=tk.RAISED,
                               command=lambda: self.controller.show_frame("MyExercisesPage"))
        exercise_btn.pack(pady=20)

class MyExercisesPage(BasePage):
    """Exercise selection page (only Lunges)"""
    def create_widgets(self):
        self.configure(bg=self.controller.theme["bg"])
        
        # Header
        header_frame = tk.Frame(self, bg=self.controller.theme["bg"])
        header_frame.pack(fill="x", padx=20, pady=15)
        
        tk.Button(header_frame, text="← Back", font=("Arial", 12),
                bg=self.controller.theme["button_bg"], fg=self.controller.theme["button_fg"],
                command=lambda: self.controller.show_frame("MenuPage")).pack(side="left")
        
        tk.Label(header_frame, text="Lunges Exercise", font=("Arial", 20, "bold"),
               bg=self.controller.theme["bg"], fg=self.controller.theme["fg"]).pack(side="left", padx=20)
        
        # Exercise description
        desc_frame = tk.Frame(self, bg=self.controller.theme["bg"])
        desc_frame.pack(fill="x", padx=40, pady=20)
        
        tk.Label(desc_frame, text="Target Muscles: Quadriceps, Glutes, Hamstrings", 
                font=("Arial", 12), bg=self.controller.theme["bg"], fg="gray").pack()
        tk.Label(desc_frame, text="Duration: 10-15 minutes | Difficulty: Beginner", 
                font=("Arial", 12), bg=self.controller.theme["bg"], fg="gray").pack()
        
        # Exercise button
        exercise_frame = tk.Frame(self, bg=self.controller.theme["bg"], pady=50)
        exercise_frame.pack(fill="both", expand=True)
        
        tk.Button(exercise_frame, text="Start Lunges", font=("Arial", 14),
                 bg="#4CAF50", fg="white", width=20, height=2,
                 command=lambda: self.start_exercise("Lunges")).pack()
    
    def start_exercise(self, exercise_name):
        self.controller.current_exercise = exercise_name
        live_page = self.controller.frames["LiveExercisePage"]
        live_page.update_exercise_info(exercise_name)
        self.controller.show_frame("LiveExercisePage")

class LiveExercisePage(BasePage):
    """Live exercise guidance page"""
    def create_widgets(self):
        self.configure(bg=self.controller.theme["bg"])
        
        # Header
        header_frame = tk.Frame(self, bg=self.controller.theme["bg"])
        header_frame.pack(fill="x", padx=20, pady=15)
        
        tk.Button(header_frame, text="← Back", font=("Arial", 12),
                bg=self.controller.theme["button_bg"], fg=self.controller.theme["button_fg"],
                command=lambda: self.controller.show_frame("MyExercisesPage")).pack(side="left")
        
        self.exercise_title = tk.Label(header_frame, text="", font=("Arial", 20, "bold"),
                                     bg=self.controller.theme["bg"], fg=self.controller.theme["fg"])
        self.exercise_title.pack(side="left", padx=20)
        
        # Content
        content_frame = tk.Frame(self, bg=self.controller.theme["bg"])
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Exercise visualization area
        visual_frame = tk.Frame(content_frame, bg="#f8f9fa", width=500, height=400, relief=tk.RAISED, bd=2)
        visual_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))
        visual_frame.pack_propagate(False)
        
        # Exercise steps visualization
        self.visual_label = tk.Label(visual_frame, text="", font=("Arial", 16), 
                                   fg="#333333", bg="#f8f9fa", wraplength=450, justify="center")
        self.visual_label.pack(fill="both", expand=True)
        
        # Instructions panel
        guide_frame = tk.Frame(content_frame, bg=self.controller.theme["bg"], width=350)
        guide_frame.pack(side="right", fill="both", expand=True)
        guide_frame.pack_propagate(False)
        
        tk.Label(guide_frame, text="Exercise Guide", font=("Arial", 16, "bold"),
                bg=self.controller.theme["bg"], fg=self.controller.theme["fg"]).pack(pady=(0, 10))
        
        self.instruction_label = tk.Label(guide_frame, text="", font=("Arial", 12),
                                        bg=self.controller.theme["bg"], fg=self.controller.theme["fg"],
                                        wraplength=330, justify="left")
        self.instruction_label.pack(fill="x", pady=20)
        
        # Rep counter
        self.rep_frame = tk.Frame(guide_frame, bg=self.controller.theme["bg"])
        self.rep_frame.pack(fill="x", pady=20)
        
        tk.Label(self.rep_frame, text="Reps Completed:", font=("Arial", 12, "bold"),
                bg=self.controller.theme["bg"], fg=self.controller.theme["fg"]).pack()
        
        self.rep_count = tk.Label(self.rep_frame, text="0", font=("Arial", 24, "bold"),
                                bg=self.controller.theme["bg"], fg="#4CAF50")
        self.rep_count.pack()
        
        # Manual rep counter buttons
        counter_frame = tk.Frame(self.rep_frame, bg=self.controller.theme["bg"])
        counter_frame.pack(pady=10)
        
        tk.Button(counter_frame, text="+1 Rep", font=("Arial", 10),
                bg="#4CAF50", fg="white", width=8,
                command=self.increment_rep).pack(side="left", padx=5)
        
        tk.Button(counter_frame, text="Reset", font=("Arial", 10),
                bg="#f44336", fg="white", width=8,
                command=self.reset_reps).pack(side="left", padx=5)
        
        # Control buttons
        controls_frame = tk.Frame(self, bg=self.controller.theme["bg"])
        controls_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Button(controls_frame, text="Restart Exercise", font=("Arial", 14),
                bg="#4CAF50", fg="white", width=15,
                command=self.restart_exercise).pack(side="left", padx=10)
        
        tk.Button(controls_frame, text="Finish Exercise", font=("Arial", 14),
                bg="#F44336", fg="white", width=15,
                command=lambda: self.controller.show_frame("MyExercisesPage")).pack(side="left", padx=10)
        
        # Initialize rep counter
        self.reps = 0
    
    def update_exercise_info(self, exercise_name):
        self.exercise_title.config(text=exercise_name)
        
        if exercise_name == "Lunges":
            # Voice instruction
            self.controller.speak("Starting lunges exercise. Follow the visual guide and count your reps.")
            
            # Visual demonstration
            self.visual_label.config(
                text="🚶‍♀️ LUNGE DEMONSTRATION\n\n"
                     "Step 1: Stand straight, feet hip-width apart\n"
                     "Step 2: Step forward with right leg\n"
                     "Step 3: Lower hips until both knees at 90°\n"
                     "Step 4: Push back to starting position\n"
                     "Step 5: Repeat with left leg\n\n"
                     "💡 Keep your front knee over your ankle\n"
                     "💡 Keep your torso upright\n"
                     "💡 Engage your core throughout"
            )
            
            # Instructions
            self.instruction_label.config(
                text="Proper Lunge Form:\n\n"
                     "✓ Stand with feet hip-width apart\n"
                     "✓ Step forward into a lunge position\n"
                     "✓ Lower until both knees are at 90°\n"
                     "✓ Front knee should be over ankle\n"
                     "✓ Back knee should nearly touch floor\n"
                     "✓ Push through front heel to return\n"
                     "✓ Alternate legs or do sets per leg\n\n"
                     "Target: 3 sets of 10-12 reps per leg"
            )
    
    def increment_rep(self):
        self.reps += 1
        self.rep_count.config(text=str(self.reps))
        if self.reps % 5 == 0:
            self.controller.speak(f"Great job! {self.reps} reps completed.")
    
    def reset_reps(self):
        self.reps = 0
        self.rep_count.config(text="0")
        self.controller.speak("Rep counter reset.")
    
    def restart_exercise(self):
        self.reset_reps()
        self.controller.speak("Restarting lunges exercise.")
        self.update_exercise_info("Lunges")

if __name__ == "__main__":
    app = FitDeskApp()
    app.mainloop()