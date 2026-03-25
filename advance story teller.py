import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os, json, datetime, threading, random
from dotenv import load_dotenv

load_dotenv()

# Optional modules
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

# Gemini API
try:
    from google import genai
    from google.genai.errors import APIError
except ImportError:
    genai = None
    APIError = Exception

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
client = None
if genai and GEMINI_KEY:
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        print("Gemini client initialized.")
    except Exception as e:
        client = None
        print("Gemini init error:", e)

# ---------------- Config ----------------
APP_TITLE = "✨ AI Story Teller ✨ "
HISTORY_FILE = "history.json"

genres = ["Fantasy", "Mystery", "Science Fiction", "Romance", "Horror"]
themes = ["Redemption", "Betrayal", "Survival", "Friendship", "Loss", "Discovery"]
characters = ["Hero", "Villain", "Mentor", "Child", "Time Traveler", "Alien", "Robot Companion", "Parent", "Detective", "Wanderer"]

genre_images = {
    "Fantasy": r"C:\Users\pky80\Downloads\fantasy.png",
    "Mystery": r"C:\Users\pky80\Downloads\mystery.png",
    "Science Fiction": r"C:\Users\pky80\Downloads\Scif.png",
    "Romance": r"C:\Users\pky80\Downloads\romance.png",
    "Horror": r"C:\Users\pky80\Downloads\horror.png",
}

# ---------------- History ----------------
def ensure_history_file():
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def add_to_history(story_text, metadata):
    ensure_history_file()
    with open(HISTORY_FILE, "r+", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except:
            data = []
        entry = {"story": story_text, "meta": metadata, "timestamp": datetime.datetime.now().isoformat()}
        data.insert(0, entry)
        f.seek(0)
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.truncate()

def load_history():
    ensure_history_file()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

# ---------------- Gemini ----------------
def generate_with_gemini(prompt):
    global client
    if not client:
        return "Gemini client not initialized."
    try:
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return getattr(resp, "text", str(resp))
    except APIError as e:
        return f"Gemini API Error: {e}"
    except Exception as e:
        return f"Gemini unexpected error: {e}"

# ---------------- GUI ----------------
class SuperStoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1200x700")
        self.root.configure(bg="#1a1a1a")
        self.root.minsize(1000, 600)

        # ---------- Config for GUI Improvement ----------
        # Set a standard size for the story image (Width x Height)
        self.IMAGE_SIZE = (400, 250) 
        # Set a fixed height for the text widget (in lines)
        self.STORY_TEXT_HEIGHT = 15 

        # ---------- Fonts ----------
        self.title_font = ("Helvetica", 24, "bold")
        self.label_font = ("Helvetica", 12)
        # Slightly smaller story font to fit more text
        self.story_font = ("Georgia", 14) 
        self.btn_font = ("Helvetica", 11, "bold")

        # ---------- Top Title ----------
        tk.Label(root, text=APP_TITLE, font=self.title_font, bg="#1a1a1a", fg="white").pack(fill="x", pady=10)

        # ---------- Main Frame ----------
        self.main_frame = tk.Frame(root, bg="#1a1a1a")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        # Configure grid column 1 (right panel) to expand
        self.main_frame.grid_columnconfigure(1, weight=1) 
        
        # Use grid for main_frame content
        self.left_panel = tk.Frame(self.main_frame, bg="#2b2b2b", width=300)
        self.left_panel.grid(row=0, column=0, sticky="ns", padx=(0, 10), pady=5)
        
        # ---------- Left Panel (Controls) ----------
        # (Content unchanged)
        
        # Genre
        tk.Label(self.left_panel, text="Genre:", bg="#2b2b2b", fg="white", font=self.label_font).pack(anchor="w", pady=(10,2), padx=10)
        self.genre_var = tk.StringVar()
        ttk.Combobox(self.left_panel, textvariable=self.genre_var, values=genres, state="readonly").pack(fill="x", padx=10, pady=5)

        # Theme
        tk.Label(self.left_panel, text="Theme:", bg="#2b2b2b", fg="white", font=self.label_font).pack(anchor="w", pady=(10,2), padx=10)
        self.theme_var = tk.StringVar()
        ttk.Combobox(self.left_panel, textvariable=self.theme_var, values=themes, state="readonly").pack(fill="x", padx=10, pady=5)

        # Character
        tk.Label(self.left_panel, text="Character:", bg="#2b2b2b", fg="white", font=self.label_font).pack(anchor="w", pady=(10,2), padx=10)
        self.character_var = tk.StringVar()
        ttk.Combobox(self.left_panel, textvariable=self.character_var, values=characters, state="readonly").pack(fill="x", padx=10, pady=5)

        # Buttons
        self.create_left_buttons()

        # ---------- Right Panel (Story & Image) - Now uses grid ----------
        self.right_panel = tk.Frame(self.main_frame, bg="#1b1b1b")
        self.right_panel.grid(row=0, column=1, sticky="nsew", pady=5)
        self.right_panel.grid_rowconfigure(1, weight=1) # Row for text box expands
        self.right_panel.grid_columnconfigure(0, weight=1) # Column expands

        # 1. Story Image Frame (to enforce fixed size and centering)
        self.image_frame = tk.Frame(self.right_panel, bg="#1b1b1b", width=self.IMAGE_SIZE[0], height=self.IMAGE_SIZE[1])
        self.image_frame.grid(row=0, column=0, padx=10, pady=(10, 5))
        # Prevent frame from shrinking to fit content, maintaining IMAGE_SIZE
        self.image_frame.grid_propagate(False) 

        self.story_image_label = tk.Label(self.image_frame, bg="#1b1b1b")
        # Center image label within the fixed-size frame
        self.story_image_label.pack(expand=True) 

        # 2. Story Text Box (Smaller due to fixed height)
        # Added height attribute
        self.story_text = tk.Text(self.right_panel, wrap="word", font=self.story_font, bg="black", fg="#f0f0f0", bd=2, relief="groove", height=self.STORY_TEXT_HEIGHT)
        # Use sticky="nsew" to make it fill the grid cell
        self.story_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10)) 

        # 3. Narration Buttons
        self.narration_frame = tk.Frame(self.right_panel, bg="#1b1b1b")
        self.narration_frame.grid(row=2, column=0, pady=5)
        self.create_narration_buttons()

        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(root, textvariable=self.status_var, relief="sunken", anchor="w", bg="#111111", fg="#ddd").pack(fill="x", side="bottom")

        # TTS
        self.tts_engine = None
        self.narration_thread = None
        self.narrating = False

        # Typing effect
        self.typing_index = 0
        self.current_text = ""
        self.typing_job = None

        # Initial image load (optional)
        self._set_image(self.genre_var.get())

    # ---------- Button Creation (UNCHANGED) ----------
    def create_left_buttons(self):
        btn_bg, btn_fg, hover_bg = "#523d8f", "#fff", "black"
        def create_btn(text, command):
            btn = tk.Button(self.left_panel, text=text, font=self.btn_font, bg=btn_bg, fg=btn_fg, bd=0, relief="ridge", command=command)
            btn.pack(fill="x", padx=10, pady=5)
            btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
            btn.bind("<Leave>", lambda e: btn.config(bg=btn_bg))
            return btn
        self.generate_btn = create_btn("Generate", self.on_generate)
        self.surprise_btn = create_btn("Surprise Me", self.on_surprise)
        self.save_txt_btn = create_btn("Save TXT", self.on_save_txt)
        self.save_pdf_btn = create_btn("Save PDF", self.on_save_pdf)
        self.history_btn = create_btn("History", self.on_history)
        self.clear_btn = create_btn("Clear", self.on_clear)

    def create_narration_buttons(self):
        btn_bg, btn_fg, hover_bg = "#523d8f", "#fff", "black"
        def create_btn(text, command):
            btn = tk.Button(self.narration_frame, text=text, font=self.btn_font, bg=btn_bg, fg=btn_fg, bd=0, relief="ridge", command=command)
            btn.pack(side="left", padx=10)
            btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
            btn.bind("<Leave>", lambda e: btn.config(bg=btn_bg))
            return btn
        self.narrate_btn = create_btn("Narrate", self.on_narrate)
        self.stop_btn = create_btn("Stop", self.stop_narration)

    # ---------- Status (UNCHANGED) ----------
    def set_status(self, text):
        self.status_var.set(text)
        self.root.update_idletasks()

    # ---------- Image (UPDATED for fixed size) ----------
    def _set_image(self, genre):
        img_path = genre_images.get(genre)
        if img_path and os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                # Resize the image to the fixed size
                img = img.resize(self.IMAGE_SIZE, Image.Resampling.LANCZOS)
                self.story_image = ImageTk.PhotoImage(img)
                self.story_image_label.config(image=self.story_image, text="")
            except Exception as e:
                 print(f"Error loading or resizing image: {e}")
                 self.story_image_label.config(image='', text="Image Error", fg="red")
        else:
            self.story_image_label.config(image='', text="No Image", fg="#666")

    # ---------- Story Generation (UNCHANGED) ----------
    def on_surprise(self):
        self.genre_var.set(random.choice(genres))
        self.theme_var.set(random.choice(themes))
        self.character_var.set(random.choice(characters))
        self.on_generate()

    def build_prompt(self):
        genre = self.genre_var.get() or random.choice(genres)
        theme = self.theme_var.get() or random.choice(themes)
        character = self.character_var.get() or random.choice(characters)
        return f"Write a vivid 4-6 sentence short story with genre={genre}, theme={theme}, character={character}"

    def on_generate(self):
        self.set_status("Generating...")
        self.story_text.delete(1.0, tk.END)
        self._set_image(self.genre_var.get())
        prompt = self.build_prompt()
        threading.Thread(target=self._generate_thread, args=(prompt,), daemon=True).start()

    def _generate_thread(self, prompt):
        story = generate_with_gemini(prompt)
        self.current_text = story
        self.typing_index = 0
        self._type_text()

    def _type_text(self):
        if self.typing_index <= len(self.current_text):
            self.story_text.delete(1.0, tk.END)
            self.story_text.insert(tk.END, self.current_text[:self.typing_index])
            self.typing_index += 1
            self.typing_job = self.root.after(15, self._type_text)
        else:
            self.typing_job = None
            add_to_history(self.current_text, {"genre": self.genre_var.get(), "theme": self.theme_var.get(), "character": self.character_var.get()})
            self.set_status("Story generated!")

    # ---------- TTS (UNCHANGED) ----------
    def on_narrate(self):
        if pyttsx3 is None:
            messagebox.showwarning("TTS Missing", "Install pyttsx3 to enable narration.")
            return
        story = self.story_text.get(1.0, tk.END).strip()
        if not story or self.narrating:
            return
        self.narration_thread = threading.Thread(target=self._narrate_thread, args=(story,), daemon=True)
        self.narration_thread.start()

    def _narrate_thread(self, text):
        self.narrating = True
        if self.tts_engine is None:
            self.tts_engine = pyttsx3.init()
        self.set_status("Narrating...")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
        self.narrating = False
        self.set_status("Narration finished")

    def stop_narration(self):
        if self.tts_engine and self.narrating:
            self.tts_engine.stop()
            self.narrating = False
            self.set_status("Narration stopped")
        if self.typing_job:
            self.root.after_cancel(self.typing_job)
            self.typing_job = None
            self.story_text.delete(1.0, tk.END)
            self.story_text.insert(tk.END, self.current_text)
            self.set_status("Typing stopped")

    # ---------- File & History (UNCHANGED) ----------
    def on_save_txt(self):
        content = self.story_text.get(1.0, tk.END).strip()
        if not content:
            self.set_status("Nothing to save.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files","*.txt")])
        if file:
            with open(file, "w", encoding="utf-8") as f:
                f.write(content)
            self.set_status(f"Saved to {file}")

    def on_save_pdf(self):
        self.set_status("PDF export not implemented yet.")

    def on_history(self):
        history = load_history()
        if not history:
            messagebox.showinfo("History", "No stories in history.")
            return
        msg = "\n\n".join([f"{h['timestamp']}\n{h['story']}" for h in history[:5]])
        messagebox.showinfo("History", msg)

    def on_clear(self):
        self.story_text.delete(1.0, tk.END)
        self.story_image_label.config(image='', text="") # Also clear 'No Image' text if present
        self.set_status("Cleared")

# ---------------- Run ----------------
def main():
    root = tk.Tk()
    app = SuperStoryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
