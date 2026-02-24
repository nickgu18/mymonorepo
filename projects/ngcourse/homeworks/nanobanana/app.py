import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from io import BytesIO
from google import genai
from google.genai import types
import os

class ImageGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nano Banana Image Generator")

        # The GOOGLE_API_KEY environment variable is used automatically.
        self.client = genai.Client()
        self.current_image = None
        self.current_prompt = ""
        self.output_directory = os.path.expanduser("~/Desktop")

        # --- GUI Elements ---
        self.setup_gui()

    def setup_gui(self):
        # Frame for controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # Prompt
        self.prompt_label = tk.Label(control_frame, text="Prompt:")
        self.prompt_label.pack(side=tk.LEFT, padx=5)
        self.prompt_entry = tk.Entry(control_frame, width=50)
        self.prompt_entry.pack(side=tk.LEFT, padx=5)

        # Buttons
        self.generate_button = tk.Button(control_frame, text="Generate/Edit Image", command=self.generate_image)
        self.generate_button.pack(side=tk.LEFT, padx=5)

        self.load_button = tk.Button(control_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(control_frame, text="Save Image", command=self.save_image)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.dir_button = tk.Button(control_frame, text="Select Directory", command=self.select_directory)
        self.dir_button.pack(side=tk.LEFT, padx=5)

        # Image Display
        self.image_label = tk.Label(self.root)
        self.image_label.pack(pady=10)

    def select_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_directory)
        if directory:
            self.output_directory = directory
            messagebox.showinfo("Directory Selected", f"Output directory set to: {self.output_directory}")

    def generate_image(self):
        self.current_prompt = self.prompt_entry.get()
        if not self.current_prompt:
            messagebox.showerror("Error", "Please enter a prompt.")
            return

        try:
            contents = [self.current_prompt]
            if self.current_image:
                contents.append(self.current_image)

            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=contents,
            )

            image_generated = False
            text_response = ""
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    text_response += part.text + "\n"
                elif part.inline_data is not None and 'image' in part.inline_data.mime_type:
                    image_data = part.inline_data.data
                    try:
                        self.current_image = Image.open(BytesIO(image_data))
                        self.display_image(self.current_image)
                        image_generated = True
                        break  # Found an image, so we can stop.
                    except Exception as e:
                        messagebox.showerror("Image Error", f"Cannot identify image file: {e}")
                        return

            if not image_generated:
                if text_response:
                    messagebox.showinfo("Model Response", text_response)
                else:
                    messagebox.showerror("Error", "No image data found in the response.")

        except Exception as e:
            messagebox.showerror("API Error", f"An error occurred: {e}")

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if file_path:
            self.current_image = Image.open(file_path)
            self.display_image(self.current_image)

            prompt_path = os.path.splitext(file_path)[0] + ".txt"
            if os.path.exists(prompt_path):
                with open(prompt_path, "r") as f:
                    self.current_prompt = f.read()
                    self.prompt_entry.delete(0, tk.END)
                    self.prompt_entry.insert(0, self.current_prompt)

    def save_image(self):
        if not self.current_image:
            messagebox.showerror("Error", "No image to save.")
            return

        file_path = filedialog.asksaveasfilename(
            initialdir=self.output_directory,
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
        )
        if file_path:
            self.current_image.save(file_path)
            prompt_path = os.path.splitext(file_path)[0] + ".txt"
            with open(prompt_path, "w") as f:
                f.write(self.current_prompt)
            messagebox.showinfo("Success", f"Image and prompt saved to {file_path}")

    def display_image(self, image):
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageGeneratorApp(root)
    root.mainloop()
