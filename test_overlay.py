import tkinter as tk
from tkinter import ttk
import sys

class TestOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Overlay Test Window - Control Panel")
        
        # Keep control panel always on top
        self.root.attributes('-topmost', True)
        
        # Control panel
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack()
        
        tk.Label(control_frame, text="Test Overlay Generator", font=("Arial", 14, "bold")).pack(pady=5)
        tk.Label(control_frame, text="Create suspicious overlays to test the detector", font=("Arial", 9)).pack(pady=5)
        
        # Overlay options
        options_frame = tk.LabelFrame(control_frame, text="Overlay Options", padx=10, pady=10)
        options_frame.pack(pady=10, fill="x")
        
        # Alpha/Transparency slider
        tk.Label(options_frame, text="Transparency (0=invisible, 255=opaque):").pack(anchor="w")
        self.alpha_var = tk.IntVar(value=128)
        alpha_slider = tk.Scale(options_frame, from_=0, to=255, orient="horizontal", 
                                variable=self.alpha_var, length=300)
        alpha_slider.pack(fill="x", pady=5)
        
        # Topmost checkbox
        self.topmost_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Always on top (topmost)", 
                       variable=self.topmost_var).pack(anchor="w", pady=2)
        
        # Click-through checkbox
        self.clickthrough_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Click-through (WS_EX_TRANSPARENT)", 
                       variable=self.clickthrough_var).pack(anchor="w", pady=2)
        
        # Show title checkbox
        self.show_title_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Show window title", 
                       variable=self.show_title_var).pack(anchor="w", pady=2)
        
        # Size options
        size_frame = tk.Frame(options_frame)
        size_frame.pack(fill="x", pady=5)
        tk.Label(size_frame, text="Size:").pack(side="left")
        self.size_var = tk.StringVar(value="medium")
        tk.Radiobutton(size_frame, text="Small (400x300)", variable=self.size_var, 
                       value="small").pack(side="left", padx=5)
        tk.Radiobutton(size_frame, text="Medium (800x600)", variable=self.size_var, 
                       value="medium").pack(side="left", padx=5)
        tk.Radiobutton(size_frame, text="Large (1200x800)", variable=self.size_var, 
                       value="large").pack(side="left", padx=5)
        
        # Buttons
        button_frame = tk.Frame(control_frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Create Overlay", command=self.create_overlay, 
                  bg="#4CAF50", fg="white", padx=20, pady=5).pack(side="left", padx=5)
        tk.Button(button_frame, text="Close All Overlays", command=self.close_all_overlays, 
                  bg="#f44336", fg="white", padx=20, pady=5).pack(side="left", padx=5)
        
        # Presets
        preset_frame = tk.LabelFrame(control_frame, text="Quick Test Presets", padx=10, pady=10)
        preset_frame.pack(pady=10, fill="x")
        
        tk.Button(preset_frame, text="Nearly Invisible Overlay", 
                  command=lambda: self.apply_preset(20, True, False, False, "large"),
                  width=25).pack(pady=2)
        tk.Button(preset_frame, text="Semi-Transparent + Topmost", 
                  command=lambda: self.apply_preset(100, True, False, False, "medium"),
                  width=25).pack(pady=2)
        tk.Button(preset_frame, text="Click-Through Overlay", 
                  command=lambda: self.apply_preset(150, True, True, False, "large"),
                  width=25).pack(pady=2)
        tk.Button(preset_frame, text="Invisible + Click-Through", 
                  command=lambda: self.apply_preset(10, True, True, False, "large"),
                  width=25).pack(pady=2)
        
        # Status
        self.status_label = tk.Label(control_frame, text="Ready", fg="green", font=("Arial", 9))
        self.status_label.pack(pady=5)
        
        self.overlays = []
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def apply_preset(self, alpha, topmost, clickthrough, show_title, size):
        """Apply a preset configuration."""
        self.alpha_var.set(alpha)
        self.topmost_var.set(topmost)
        self.clickthrough_var.set(clickthrough)
        self.show_title_var.set(show_title)
        self.size_var.set(size)
        self.create_overlay()
    
    def create_overlay(self):
        """Create an overlay window with specified properties."""
        overlay = tk.Toplevel(self.root)
        
        # Important: Don't let test overlays block the control panel
        overlay.attributes('-topmost', False)  # Start as not topmost
        
        # Set title
        if self.show_title_var.get():
            overlay.title("Test Overlay")
        else:
            overlay.overrideredirect(True)  # Remove title bar
        
        # Set size
        sizes = {
            "small": (400, 300),
            "medium": (800, 600),
            "large": (1200, 800)
        }
        width, height = sizes[self.size_var.get()]
        
        # Position offset from center to avoid covering control panel
        screen_width = overlay.winfo_screenwidth()
        screen_height = overlay.winfo_screenheight()
        x = (screen_width - width) // 2 + len(self.overlays) * 30  # Offset each overlay
        y = (screen_height - height) // 2 + len(self.overlays) * 30
        overlay.geometry(f"{width}x{height}+{x}+{y}")
        
        # Set transparency
        alpha_value = self.alpha_var.get() / 255.0
        overlay.attributes('-alpha', alpha_value)
        
        # Add visual content
        frame = tk.Frame(overlay, bg="#FF5722")
        frame.pack(fill="both", expand=True)
        
        # Add appropriate message based on click-through setting
        if self.clickthrough_var.get():
            message = f"TEST OVERLAY #{len(self.overlays) + 1}\n\nClick-through enabled\nClose from control panel only"
        else:
            message = f"TEST OVERLAY #{len(self.overlays) + 1}\n\nThis window should be detected\nby the overlay detector"
        
        label = tk.Label(frame, text=message,
                        font=("Arial", 16, "bold"), bg="#FF5722", fg="white")
        label.pack(expand=True)
        
        # Only show close button if NOT click-through (button won't work with click-through)
        if not self.clickthrough_var.get():
            close_btn = tk.Button(frame, text="Close This Overlay", 
                                  command=lambda: self.close_overlay(overlay),
                                  bg="white", fg="#FF5722", padx=10, pady=5, font=("Arial", 10, "bold"))
            close_btn.pack(pady=20)
        
        # Store overlay reference first
        self.overlays.append(overlay)
        
        # Apply topmost AFTER adding to list (so control panel stays above)
        if self.topmost_var.get():
            overlay.after(100, lambda: overlay.attributes('-topmost', True))
        
        # Apply click-through on Windows LAST
        if self.clickthrough_var.get() and sys.platform == "win32":
            try:
                import win32gui
                import win32con
                overlay.update()  # Ensure window is created
                hwnd = overlay.winfo_id()
                extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                                      extended_style | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED)
                # Refresh control panel to top
                self.root.lift()
                self.root.attributes('-topmost', True)
                self.status_label.config(text="✓ Click-through overlay created", fg="green")
            except Exception as e:
                self.status_label.config(text=f"⚠ Click-through failed: {e}", fg="orange")
        else:
            # Ensure control panel stays on top
            self.root.lift()
            self.status_label.config(text=f"✓ Overlay created (alpha={self.alpha_var.get()})", fg="green")
    
    def close_overlay(self, overlay):
        """Close a specific overlay."""
        if overlay in self.overlays:
            self.overlays.remove(overlay)
        overlay.destroy()
        self.status_label.config(text="Overlay closed", fg="blue")
    
    def close_all_overlays(self):
        """Close all overlay windows."""
        count = len(self.overlays)
        for overlay in self.overlays[:]:
            try:
                overlay.destroy()
            except:
                pass  # Window might already be destroyed
        self.overlays.clear()
        self.status_label.config(text=f"All {count} overlays closed", fg="blue")
        # Ensure control panel is visible
        self.root.lift()
        self.root.focus_force()
    
    def on_close(self):
        """Handle window close event."""
        self.close_all_overlays()
        self.root.destroy()
    
    def run(self):
        """Start the application."""
        self.root.mainloop()

if __name__ == "__main__":
    app = TestOverlay()
    app.run()