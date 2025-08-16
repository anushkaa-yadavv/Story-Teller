import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import random
import os

# -------------------- Data --------------------
genres = ["Fantasy", "Mystery", "Science Fiction", "Romance", "Horror"]
themes = ["Redemption", "Betrayal", "Survival", "Friendship"]
characters = [
    "Hero", "Villain", "Mentor", "Child",
    "Time Traveler", "Alien", "Robot Companion", "Parent"
]

genre_images = {
    "Fantasy": r"C:\\Users\\pky80\\Downloads\\fantasy.png",
    "Mystery": r"C:\\Users\\pky80\\Downloads\\mystery.png",
    "Science Fiction": r"C:\\Users\\pky80\\Downloads\\Scif.png",
    "Romance": r"C:\\Users\\pky80\\Downloads\\romance.png",
    "Horror": r"C:\\Users\\pky80\\Downloads\\horror.png",
}

# -------------------- Main Window --------------------
root = tk.Tk()
root.title("✨ Story Idea Generator")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")
root.configure(bg="#2b2d42")
root.resizable(True, True)

# -------------------- Background Image --------------------
background_label = tk.Label(root, bg="black")
background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

# -------------------- Title --------------------
title_label = tk.Label(
    root,
    text="✨ Story Idea Generator",
    font=("Georgia", 16, "bold"),
    bg="#0f0f0f",
    fg="white",
    padx=20,
    pady=10
)
title_label.place(relx=0.5, rely=0.05, anchor="n")

# -------------------- Story Display --------------------
story_label = tk.Label(
    root, text="", wraplength=screen_width * 0.85,
    font=("Georgia", 20, "bold"),
    bg="#1a1a1a", fg="#f8f8f8",
    justify="center", padx=30, pady=20,
    bd=4, relief="groove"
)
story_label.place(relx=0.5, rely=0.18, anchor="n")

# -------------------- Form Frame --------------------
form_frame = tk.Frame(root, bg="#0f0f0f", bd=3, relief="ridge")
form_frame.place(relx=0.5, rely=0.58, anchor="center")

# Genre
genre_var = tk.StringVar()
tk.Label(form_frame, text="Select Genre:", font=("Helvetica", 14), fg="white", bg="#0f0f0f").grid(row=0, column=0, padx=10, pady=10)
genre_menu = ttk.Combobox(form_frame, textvariable=genre_var, values=genres, state="readonly", width=30)
genre_menu.grid(row=0, column=1)

# Theme
theme_var = tk.StringVar()
tk.Label(form_frame, text="Select Theme:", font=("Helvetica", 14), fg="white", bg="#0f0f0f").grid(row=1, column=0, padx=10, pady=10)
theme_menu = ttk.Combobox(form_frame, textvariable=theme_var, values=themes, state="readonly", width=30)
theme_menu.grid(row=1, column=1)

# Character
character_var = tk.StringVar()
tk.Label(form_frame, text="Select Character:", font=("Helvetica", 14), fg="white", bg="#0f0f0f").grid(row=2, column=0, padx=10, pady=10)
character_menu = ttk.Combobox(form_frame, textvariable=character_var, values=characters, state="readonly", width=30)
character_menu.grid(row=2, column=1)

# -------------------- Functions --------------------
def generate_story():
    genre = genre_var.get().strip()
    theme = theme_var.get().strip()
    character = character_var.get().strip()

    if not (genre and theme and character):
        messagebox.showwarning("Missing Fields", "Please select Genre, Theme, and Character!")
        return

    article = "an" if genre[0].lower() in "aeiou" else "a"
    prompt = (
        f"In {article} {genre.lower()} world, a {character.lower()} must face the challenge of {theme.lower()}, "
        f"navigating twists and decisions that could change everything."
    )
    story_label.config(text=prompt)

    # Show genre background
    img_path = genre_images.get(genre)
    if img_path and os.path.exists(img_path):
        try:
            img = Image.open(img_path).resize((screen_width, screen_height))
            photo = ImageTk.PhotoImage(img)
            background_label.config(image=photo)
            background_label.image = photo
        except Exception as e:
            print("Image Load Error:", e)
            story_label.config(text="⚠️ Image failed to load")
    else:
        background_label.config(image='', bg="black")
        background_label.image = None

def clear_all():
    genre_var.set("")
    theme_var.set("")
    character_var.set("")
    story_label.config(text="")
    background_label.config(image='', bg="black")
    background_label.image = None

def surprise_me():
    genre_var.set(random.choice(genres))
    theme_var.set(random.choice(themes))
    character_var.set(random.choice(characters))
    generate_story()

def save_prompt():
    story = story_label.cget("text")
    if not story:
        messagebox.showinfo("No Story", "Generate a story first!")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if filepath:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(story)
        messagebox.showinfo("Saved", f"Story saved to:\n{filepath}")

# -------------------- Buttons --------------------
button_frame = tk.Frame(root, bg="#1e1e1e")
button_frame.pack(pady=10)
button_frame.place(relx=0.5, rely=0.82, anchor="center")
button_style = {"bg": "#000000", "fg": "white", "activebackground": "#333333",
"activeforeground": "white", "padx": 15}
tk.Button(button_frame, text="Generate", command=generate_story,**button_style).grid(row=0, column=0, padx=15)
tk.Button(button_frame, text="Clear", command=clear_all,**button_style).grid(row=0, column=1, padx=15)
tk.Button(button_frame, text="Surprise Me", command=surprise_me,**button_style).grid(row=0, column=2, padx=15)
tk.Button(button_frame, text="Save", command=save_prompt, **button_style).grid(row=0, column=3, padx=15)






# -------------------- Main Loop --------------------
root.mainloop()

