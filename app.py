"""
ASCII Art Generator Application
Converts images to ASCII art with various customization options
"""

import os
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import html
import webbrowser
from time import sleep

class AsciiArtGenerator:
    """Main application class for the ASCII Art Generator"""
    
    def __init__(self, root_window):
        """Initialize the application with main window"""
        self.root_window = root_window
        self.root_window.title("ASCII Art Generator")
        self.root_window.geometry("800x600")
        
        # Initialize image-related attributes
        self.current_image_path = None
        self.original_image = None
        self.preview_image = None
        
        # Initialize settings with default values
        self.max_width = IntVar(value=100)  # Default max width of ASCII art
        self.height_scale = DoubleVar(value=0.5)  # Height scaling factor
        self.invert_brightness = BooleanVar(value=False)  # Invert brightness toggle
        self.live_render = BooleanVar(value=False)  # Real-time rendering toggle
        self.animation_enabled = BooleanVar(value=False)  # Animation toggle
        self.animation_delay = DoubleVar(value=0.01)  # Animation speed
        
        # Character set for ASCII conversion
        self.char_set = StringVar()
        self.default_characters = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
        self.char_set.set(self.default_characters)
        
        # Output configuration
        self.output_format = StringVar(value="terminal")  # Default output format
        self.html_output_path = StringVar()  # Path for HTML output
        
        # Build the user interface
        self.initialize_interface()
        
    def initialize_interface(self):
        """Create and arrange all GUI components"""
        # Main container frame
        main_container = Frame(self.root_window)
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for image controls
        self.create_image_panel(main_container)
        
        # Right panel for output and settings
        self.create_output_panel(main_container)
        
        # Bind output format change handler
        self.output_format.trace_add("write", self.toggle_html_file_selector)
        self.toggle_html_file_selector()
    
    def create_image_panel(self, parent):
        """Create the left panel with image controls"""
        left_panel = Frame(parent)
        left_panel.pack(side=LEFT, fill=Y, padx=5, pady=5)
        
        # Image selection controls
        selection_frame = LabelFrame(left_panel, text="Image Selection", padx=5, pady=5)
        selection_frame.pack(fill=X, pady=5)
        
        self.image_path_label = Label(selection_frame, text="No image selected", width=40, anchor=W)
        self.image_path_label.pack(side=LEFT, padx=5)
        
        browse_button = Button(selection_frame, text="Browse...", command=self.select_image_file)
        browse_button.pack(side=RIGHT, padx=5)
        
        # Image preview area
        self.preview_label = Label(
            left_panel, 
            text="Image Preview", 
            bg="white", 
            relief=SUNKEN, 
            width=40, 
            height=15
        )
        self.preview_label.pack(fill=BOTH, expand=True, pady=5)
        
        # Settings panel
        self.create_settings_panel(left_panel)
    
    def create_settings_panel(self, parent):
        """Create the settings panel with conversion options"""
        settings_frame = LabelFrame(parent, text="Conversion Settings", padx=5, pady=5)
        settings_frame.pack(fill=X, pady=5)
        
        # Max width setting
        Label(settings_frame, text="Max Width:").grid(row=0, column=0, sticky=W, padx=5, pady=2)
        Spinbox(
            settings_frame, 
            from_=20, 
            to=200, 
            textvariable=self.max_width, 
            width=5
        ).grid(row=0, column=1, sticky=W, padx=5, pady=2)
        
        # Height scale setting
        Label(settings_frame, text="Height Scale:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        Spinbox(
            settings_frame, 
            from_=0.1, 
            to=2.0, 
            increment=0.1, 
            textvariable=self.height_scale, 
            width=5
        ).grid(row=1, column=1, sticky=W, padx=5, pady=2)
        
        # Invert brightness checkbox
        Checkbutton(
            settings_frame, 
            text="Invert Brightness", 
            variable=self.invert_brightness
        ).grid(row=2, column=0, columnspan=2, sticky=W, padx=5, pady=2)
        
        # Character set entry
        Label(settings_frame, text="Character Set:").grid(row=3, column=0, sticky=W, padx=5, pady=2)
        Entry(
            settings_frame, 
            textvariable=self.char_set, 
            width=30
        ).grid(row=3, column=1, sticky=W, padx=5, pady=2)
    
    def create_output_panel(self, parent):
        """Create the right panel with output options"""
        right_panel = Frame(parent)
        right_panel.pack(side=RIGHT, fill=BOTH, expand=True, padx=5, pady=5)
        
        # Output format selection
        output_frame = LabelFrame(right_panel, text="Output Format", padx=5, pady=5)
        output_frame.pack(fill=X, pady=5)
        
        Radiobutton(
            output_frame, 
            text="Terminal Output", 
            variable=self.output_format, 
            value="terminal"
        ).pack(anchor=W)
        
        Radiobutton(
            output_frame, 
            text="HTML Output", 
            variable=self.output_format, 
            value="html"
        ).pack(anchor=W)
        
        # HTML file selection (conditional display)
        self.html_file_frame = Frame(output_frame)
        self.html_path_label = Label(self.html_file_frame, text="No file selected", width=30, anchor=W)
        self.html_path_label.pack(side=LEFT, padx=5)
        
        self.html_browse_button = Button(
            self.html_file_frame, 
            text="Browse...", 
            command=self.select_html_output_file
        )
        self.html_browse_button.pack(side=RIGHT, padx=5)
        
        # Render options
        self.create_render_options_panel(right_panel)
        
        # Generate button
        generate_button = Button(
            right_panel, 
            text="Generate ASCII Art", 
            command=self.generate_ascii_art, 
            height=2
        )
        generate_button.pack(fill=X, pady=10)
        
        # Output display area
        self.create_output_display(right_panel)
    
    def create_render_options_panel(self, parent):
        """Create panel for render options"""
        render_frame = LabelFrame(parent, text="Render Options", padx=5, pady=5)
        render_frame.pack(fill=X, pady=5)
        
        Checkbutton(
            render_frame, 
            text="Live Render", 
            variable=self.live_render
        ).pack(anchor=W)
        
        Checkbutton(
            render_frame, 
            text="Animate", 
            variable=self.animation_enabled
        ).pack(anchor=W)
        
        Label(render_frame, text="Animation Delay:").pack(anchor=W)
        Spinbox(
            render_frame, 
            from_=0.001, 
            to=0.1, 
            increment=0.001, 
            textvariable=self.animation_delay, 
            width=5
        ).pack(anchor=W)
    
    def create_output_display(self, parent):
        """Create the ASCII art output display"""
        output_frame = LabelFrame(parent, text="ASCII Art Preview", padx=5, pady=5)
        output_frame.pack(fill=BOTH, expand=True)
        
        # Configure text widget with scrollbars
        self.output_display = Text(
            output_frame, 
            wrap=NONE, 
            font=("Courier", 8), 
            bg="black", 
            fg="white"
        )
        
        x_scrollbar = Scrollbar(output_frame, orient=HORIZONTAL, command=self.output_display.xview)
        y_scrollbar = Scrollbar(output_frame, orient=VERTICAL, command=self.output_display.yview)
        
        self.output_display.configure(
            xscrollcommand=x_scrollbar.set, 
            yscrollcommand=y_scrollbar.set
        )
        
        y_scrollbar.pack(side=RIGHT, fill=Y)
        x_scrollbar.pack(side=BOTTOM, fill=X)
        self.output_display.pack(side=LEFT, fill=BOTH, expand=True)
    
    def toggle_html_file_selector(self, *args):
        """Toggle visibility of HTML file selector based on output format"""
        if self.output_format.get() == "html":
            self.html_file_frame.pack(fill=X, pady=5)
        else:
            self.html_file_frame.pack_forget()
    
    def select_image_file(self):
        """Open dialog to select an image file"""
        file_types = (
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
            ("All files", "*.*")
        )
        
        selected_path = filedialog.askopenfilename(
            title="Select an image",
            initialdir=os.path.expanduser("~/Pictures"),
            filetypes=file_types
        )
        
        if selected_path:
            self.current_image_path = selected_path
            self.image_path_label.config(text=os.path.basename(selected_path))
            self.display_image_preview(selected_path)
    
    def display_image_preview(self, image_path):
        """Display a thumbnail preview of the selected image"""
        try:
            self.original_image = Image.open(image_path)
            
            # Create thumbnail for preview
            thumbnail_size = (300, 300)
            thumbnail = self.original_image.copy()
            thumbnail.thumbnail(thumbnail_size)
            
            self.preview_image = ImageTk.PhotoImage(thumbnail)
            self.preview_label.config(image=self.preview_image, text="")
        except Exception as error:
            messagebox.showerror("Error", f"Could not load image: {error}")
            self.preview_label.config(image=None, text="Image Preview")
    
    def select_html_output_file(self):
        """Select destination for HTML output"""
        output_file = filedialog.asksaveasfilename(
            title="Save HTML As",
            defaultextension=".html",
            filetypes=(("HTML files", "*.html"), ("All files", "*.*"))
        )
        
        if output_file:
            self.html_output_path.set(output_file)
            self.html_path_label.config(text=os.path.basename(output_file))
    
    def generate_ascii_art(self):
        """Main function to generate ASCII art from image"""
        if not self.current_image_path:
            messagebox.showwarning("No Image", "Please select an image first")
            return
        
        if self.output_format.get() == "html" and not self.html_output_path.get():
            messagebox.showwarning("No Output File", "Please select an HTML output file")
            return
        
        try:
            # Clear previous output
            self.output_display.delete(1.0, END)
            self.output_display.update()
            
            # Process the image
            processed_image = self.process_image()
            
            # Generate ASCII art
            ascii_result = self.convert_to_ascii(processed_image)
            
            # Handle output based on selected format
            if self.output_format.get() == "terminal":
                self.display_terminal_output(ascii_result)
            else:
                self.save_html_output(ascii_result, *processed_image.size)
            
        except Exception as error:
            messagebox.showerror("Error", f"Failed to generate ASCII art: {error}")
    
    def process_image(self):
        """Load and process the image based on settings"""
        image = Image.open(self.current_image_path)
        image = self.resize_image(image)
        return image.convert("RGB")
    
    def resize_image(self, image):
        """Resize image while maintaining aspect ratio"""
        original_width, original_height = image.size
        new_width = min(original_width, self.max_width.get())
        new_height = int(new_width * self.height_scale.get() * (original_height / original_width))
        return image.resize((new_width, new_height))
    
    def convert_to_ascii(self, image):
        """Convert image pixels to ASCII characters"""
        width, height = image.size
        pixels = image.load()
        character_set = self.char_set.get() or self.default_characters
        ascii_lines = []
        
        for y in range(height):
            line = ""
            for x in range(width):
                red, green, blue = pixels[x, y]
                brightness = self.calculate_brightness(red, green, blue)
                
                if self.invert_brightness.get():
                    brightness = 255 - brightness
                
                char_index = int(brightness / 255 * (len(character_set) - 1))
                line += character_set[char_index]
            
            ascii_lines.append(line)
        
        return ascii_lines
    
    def calculate_brightness(self, red, green, blue):
        """Calculate perceived brightness of an RGB color"""
        return 0.299 * red + 0.587 * green + 0.114 * blue
    
    def display_terminal_output(self, ascii_art):
        """Display ASCII art in the output widget"""
        self.output_display.config(state=NORMAL)
        self.output_display.delete(1.0, END)
        
        if self.live_render.get() or self.animation_enabled.get():
            self.render_with_animation(ascii_art)
        else:
            for line in ascii_art:
                self.output_display.insert(END, line + "\n")
        
        self.output_display.config(state=DISABLED)
    
    def render_with_animation(self, ascii_art):
        """Render ASCII art with animation effects"""
        self.output_display.config(state=NORMAL)
        delay = self.animation_delay.get()
        
        if self.animation_enabled.get():
            # Character-by-character animation
            for line in ascii_art:
                self.output_display.insert(END, "\n")
                for char in line:
                    self.output_display.insert(END, char)
                    self.output_display.see(END)
                    self.output_display.update()
                    sleep(delay / 10)
        else:
            # Line-by-line animation
            for line in ascii_art:
                self.output_display.insert(END, line + "\n")
                self.output_display.see(END)
                self.output_display.update()
                sleep(delay)
        
        self.output_display.config(state=DISABLED)
    
    def save_html_output(self, ascii_art, width, height):
        """Generate and save HTML version of ASCII art"""
        html_content = self.generate_html_content(ascii_art, width, height)
        
        try:
            with open(self.html_output_path.get(), "w") as output_file:
                output_file.write(html_content)
            
            if messagebox.askyesno(
                "Success", 
                "HTML file saved successfully. Would you like to open it now?"
            ):
                webbrowser.open_new_tab("file://" + os.path.abspath(self.html_output_path.get()))
        except Exception as error:
            messagebox.showerror("Error", f"Failed to save HTML file: {error}")
    
    def generate_html_content(self, ascii_art, width, height):
        """Generate HTML content for ASCII art"""
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <title>ASCII Art</title>
    <style>
        body {{
            background-color: #000;
            color: #fff;
            font-family: monospace;
            font-size: 12px;
            line-height: 12px;
            margin: 0;
            padding: 20px;
        }}
        pre {{
            margin: 0;
            letter-spacing: 2px;
            white-space: pre;
        }}
    </style>
</head>
<body>
    <pre>
"""
        
        # Add escaped ASCII art lines
        for line in ascii_art:
            html_template += html.escape(line) + "\n"
        
        html_template += """    </pre>
</body>
</html>"""
        
        return html_template

if __name__ == "__main__":
    # Create and run the application
    root = Tk()
    app = AsciiArtGenerator(root)
    root.mainloop()