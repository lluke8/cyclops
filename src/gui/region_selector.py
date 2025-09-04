"""
Region selector for Cyclops automation system.
Provides a full-screen overlay for selecting screen regions.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import time
from typing import Callable, Optional

class RegionSelector:
    """Full-screen region selector with overlay"""
    
    def __init__(self, parent, on_selected: Callable, on_cancelled: Callable):
        """
        Initialize region selector
        
        Args:
            parent: Parent window
            on_selected: Callback when region is selected (x, y, width, height)
            on_cancelled: Callback when selection is cancelled
        """
        self.parent = parent
        self.on_selected = on_selected
        self.on_cancelled = on_cancelled
        self.logger = logging.getLogger(__name__)
        
        # Selection state
        self.start_x = 0
        self.start_y = 0
        self.current_x = 0
        self.current_y = 0
        self.is_selecting = False
        self.selection_rect = None
        
        # Create overlay window
        self._create_overlay()
        
        self.logger.info("Region selector initialized")
    
    def _create_overlay(self):
        """Create full-screen overlay window"""
        # Create overlay window
        self.overlay = tk.Toplevel(self.parent)
        self.overlay.title("Select Health Bar Region")
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-topmost', True)
        self.overlay.attributes('-alpha', 0.5)  # Semi-transparent
        self.overlay.configure(bg='black')
        
        # Get screen dimensions
        screen_width = self.overlay.winfo_screenwidth()
        screen_height = self.overlay.winfo_screenheight()
        
        # Create canvas for drawing selection rectangle
        self.canvas = tk.Canvas(
            self.overlay, 
            highlightthickness=0, 
            bg='black',
            width=screen_width,
            height=screen_height
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create instruction label
        self.instruction_label = tk.Label(
            self.overlay,
            text="Click and drag to select the health bar region\nPress ESC to cancel, ENTER to confirm",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='black'
        )
        self.instruction_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        
        # Bind events
        self._bind_events()
        
        # Focus the overlay
        self.overlay.focus_set()
        self.overlay.grab_set()  # Make it modal
    
    def _bind_events(self):
        """Bind mouse and keyboard events"""
        # Mouse events - bind to both canvas and overlay
        self.canvas.bind('<Button-1>', self._on_mouse_down)
        self.canvas.bind('<B1-Motion>', self._on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_mouse_up)
        
        self.overlay.bind('<Button-1>', self._on_mouse_down)
        self.overlay.bind('<B1-Motion>', self._on_mouse_drag)
        self.overlay.bind('<ButtonRelease-1>', self._on_mouse_up)
        
        # Keyboard events
        self.overlay.bind('<KeyPress-Escape>', self._on_escape)
        self.overlay.bind('<KeyPress-Return>', self._on_enter)
        self.canvas.bind('<KeyPress-Escape>', self._on_escape)
        self.canvas.bind('<KeyPress-Return>', self._on_enter)
        
        # Window events
        self.overlay.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _on_mouse_down(self, event):
        """Handle mouse button down"""
        self.start_x = event.x
        self.start_y = event.y
        self.current_x = event.x
        self.current_y = event.y
        self.is_selecting = True
        
        # Clear previous selection
        self.canvas.delete("selection")
        
        # Draw initial point
        self.canvas.create_oval(
            self.start_x-2, self.start_y-2, self.start_x+2, self.start_y+2,
            fill='lime', outline='lime', tags="selection"
        )
        
        print(f"Selection started at ({self.start_x}, {self.start_y})")  # Debug print
        self.logger.debug(f"Selection started at ({self.start_x}, {self.start_y})")
    
    def _on_mouse_drag(self, event):
        """Handle mouse drag"""
        if not self.is_selecting:
            return
        
        self.current_x = event.x
        self.current_y = event.y
        
        # Clear previous rectangle
        self.canvas.delete("selection")
        
        # Draw new rectangle
        self.selection_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.current_x, self.current_y,
            outline='lime', width=3, tags="selection"
        )
        
        # Update instruction with coordinates
        width = abs(self.current_x - self.start_x)
        height = abs(self.current_y - self.start_y)
        x = min(self.start_x, self.current_x)
        y = min(self.start_y, self.current_y)
        
        self.instruction_label.config(
            text=f"Selecting region: X:{x}, Y:{y}, W:{width}, H:{height}\nPress ESC to cancel, ENTER to confirm"
        )
        
        print(f"Dragging to ({self.current_x}, {self.current_y})")  # Debug print
    
    def _on_mouse_up(self, event):
        """Handle mouse button up"""
        if not self.is_selecting:
            return
        
        self.is_selecting = False
        self.current_x = event.x
        self.current_y = event.y
        
        # Calculate final region
        x = min(self.start_x, self.current_x)
        y = min(self.start_y, self.current_y)
        width = abs(self.current_x - self.start_x)
        height = abs(self.current_y - self.start_y)
        
        print(f"Mouse up at ({self.current_x}, {self.current_y})")  # Debug print
        
        # Validate selection
        if width < 10 or height < 5:
            messagebox.showwarning("Invalid Selection", "Please select a larger region (minimum 10x5 pixels)")
            self.canvas.delete("selection")
            self.instruction_label.config(
                text="Click and drag to select the health bar region\nPress ESC to cancel, ENTER to confirm"
            )
            return
        
        # Update instruction
        self.instruction_label.config(
            text=f"Region selected: X:{x}, Y:{y}, W:{width}, H:{height}\nPress ENTER to confirm or ESC to cancel"
        )
        
        print(f"Region selected: X:{x}, Y:{y}, W:{width}, H:{height}")  # Debug print
        self.logger.info(f"Region selected: X:{x}, Y:{y}, W:{width}, H:{height}")
    
    def _on_enter(self, event):
        """Handle Enter key press"""
        print("Enter key pressed")  # Debug print
        if self.selection_rect is None:
            messagebox.showwarning("No Selection", "Please select a region first")
            return
        
        # Calculate final region
        x = min(self.start_x, self.current_x)
        y = min(self.start_y, self.current_y)
        width = abs(self.current_x - self.start_x)
        height = abs(self.current_y - self.start_y)
        
        print(f"Confirming selection: X:{x}, Y:{y}, W:{width}, H:{height}")  # Debug print
        
        # Close overlay and call callback
        self.overlay.destroy()
        self.on_selected(x, y, width, height)
    
    def _on_escape(self, event):
        """Handle Escape key press"""
        print("Escape key pressed")  # Debug print
        self._on_cancel()
    
    def _on_cancel(self):
        """Handle cancellation"""
        print("Cancelling selection")  # Debug print
        self.overlay.destroy()
        self.on_cancelled()

class RegionOverlay:
    """Persistent overlay for showing selected region"""
    
    def __init__(self, x: int, y: int, width: int, height: int, is_active: bool = False, color: str = 'yellow'):
        """
        Initialize region overlay
        
        Args:
            x: X coordinate of region
            y: Y coordinate of region
            width: Width of region
            height: Height of region
            is_active: Whether monitoring is active (green) or inactive (red)
            color: Base color for the overlay (yellow, cyan, etc.)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_active = is_active
        self.base_color = color
        self.logger = logging.getLogger(__name__)
        
        # Create overlay window
        self._create_overlay()
    
    def _create_overlay(self):
        """Create overlay window"""
        # Create 4 separate windows for each border side
        self.border_windows = []
        
        # Top border
        top_window = tk.Toplevel()
        top_window.geometry(f"{self.width}x3+{self.x}+{self.y}")
        top_window.attributes('-topmost', True)
        top_window.overrideredirect(True)
        top_window.configure(bg=self.base_color)
        self.border_windows.append(top_window)
        
        # Bottom border
        bottom_window = tk.Toplevel()
        bottom_window.geometry(f"{self.width}x3+{self.x}+{self.y + self.height - 3}")
        bottom_window.attributes('-topmost', True)
        bottom_window.overrideredirect(True)
        bottom_window.configure(bg=self.base_color)
        self.border_windows.append(bottom_window)
        
        # Left border
        left_window = tk.Toplevel()
        left_window.geometry(f"3x{self.height}+{self.x}+{self.y}")
        left_window.attributes('-topmost', True)
        left_window.overrideredirect(True)
        left_window.configure(bg=self.base_color)
        self.border_windows.append(left_window)
        
        # Right border
        right_window = tk.Toplevel()
        right_window.geometry(f"3x{self.height}+{self.x + self.width - 3}+{self.y}")
        right_window.attributes('-topmost', True)
        right_window.overrideredirect(True)
        right_window.configure(bg=self.base_color)
        self.border_windows.append(right_window)
        
        self.logger.info(f"Region overlay created at ({self.x}, {self.y}) - Border only")
    
    def update_status(self, is_active: bool):
        """Update overlay status"""
        self.is_active = is_active
        
        # Set border color based on status
        border_color = 'green' if is_active else self.base_color
        
        # Update all border windows
        for window in self.border_windows:
            window.configure(bg=border_color)
        
        status_text = "ACTIVE" if is_active else "INACTIVE"
        self.logger.debug(f"Overlay status updated to {status_text}")
    
    def destroy(self):
        """Destroy overlay"""
        if hasattr(self, 'border_windows'):
            for window in self.border_windows:
                window.destroy()
            self.logger.info("Region overlay destroyed")


class ClickRecorder:
    """Records click locations for emergency actions"""
    
    def __init__(self, click_count: int, callback: callable):
        """
        Initialize click recorder
        
        Args:
            click_count: Number of clicks to record
            callback: Function to call when recording is complete
        """
        self.click_count = click_count
        self.callback = callback
        self.recorded_clicks = []
        self.overlay = None
        self.logger = logging.getLogger(__name__)
    
    def start_recording(self):
        """Start recording click locations"""
        try:
            # Create full-screen overlay for click recording
            self.overlay = tk.Toplevel()
            self.overlay.attributes('-fullscreen', True)
            self.overlay.attributes('-topmost', True)
            self.overlay.attributes('-alpha', 0.1)  # Semi-transparent
            self.overlay.configure(bg='black')
            
            # Create canvas for visual feedback
            self.canvas = tk.Canvas(self.overlay, highlightthickness=0)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
            # Add instructions
            self.canvas.create_text(
                self.overlay.winfo_screenwidth() // 2, 50,
                text=f"Click {self.click_count} location(s) for emergency actions",
                fill='white', font=('Arial', 16, 'bold')
            )
            
            self.canvas.create_text(
                self.overlay.winfo_screenwidth() // 2, 80,
                text=f"Click {len(self.recorded_clicks) + 1} of {self.click_count}",
                fill='yellow', font=('Arial', 14)
            )
            
            # Bind mouse events to canvas only (overlay binding causes duplicate events)
            self.canvas.bind('<Button-1>', self._on_click)
            self.overlay.bind('<Escape>', self._cancel_recording)
            
            # Add a timeout to prevent infinite recording
            self.overlay.after(30000, self._timeout_recording)  # 30 second timeout
            
            # Focus the overlay
            self.overlay.focus_set()
            self.overlay.grab_set()
            
            self.logger.info(f"Started recording {self.click_count} emergency clicks")
            self.logger.debug(f"Overlay created with size: {self.overlay.winfo_screenwidth()}x{self.overlay.winfo_screenheight()}")
            
        except Exception as e:
            self.logger.error(f"Failed to start click recording: {e}")
            self._cleanup()
    
    def _on_click(self, event):
        """Handle mouse click during recording"""
        try:
            # Record click location
            click_location = (event.x_root, event.y_root)
            
            # Check if this is a duplicate click (same location within a short time)
            if (hasattr(self, '_last_click_time') and 
                hasattr(self, '_last_click_location') and
                time.time() - self._last_click_time < 0.1 and
                self._last_click_location == click_location):
                self.logger.debug(f"Ignoring duplicate click at {click_location}")
                return
            
            # Store this click info to prevent duplicates
            self._last_click_time = time.time()
            self._last_click_location = click_location
            
            self.recorded_clicks.append(click_location)
            
            # Draw visual feedback
            self.canvas.create_oval(
                event.x - 10, event.y - 10,
                event.x + 10, event.y + 10,
                outline='red', width=3, fill=''
            )
            
            self.canvas.create_text(
                event.x, event.y - 20,
                text=str(len(self.recorded_clicks)),
                fill='red', font=('Arial', 12, 'bold')
            )
            
            self.logger.info(f"Recorded click {len(self.recorded_clicks)} at ({event.x_root}, {event.y_root})")
            
            # Check if recording is complete
            if len(self.recorded_clicks) >= self.click_count:
                self.logger.info(f"Recording complete! Got {len(self.recorded_clicks)} clicks out of {self.click_count} requested")
                self._finish_recording()
            else:
                # Update instruction text
                self.canvas.delete("instruction")
                self.canvas.create_text(
                    self.overlay.winfo_screenwidth() // 2, 80,
                    text=f"Click {len(self.recorded_clicks) + 1} of {self.click_count}",
                    fill='yellow', font=('Arial', 14), tags="instruction"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to record click: {e}")
            self._cleanup()
    
    def _finish_recording(self):
        """Finish recording and call callback"""
        try:
            self.logger.info(f"Finished recording {len(self.recorded_clicks)} emergency clicks")
            
            # Show completion message
            self.canvas.create_text(
                self.overlay.winfo_screenwidth() // 2, 120,
                text="Recording complete! Press any key to finish.",
                fill='green', font=('Arial', 14, 'bold')
            )
            
            # Unbind mouse events to prevent more clicks
            self.canvas.unbind('<Button-1>')
            
            # Bind key press to finish
            self.overlay.bind('<Key>', self._complete_recording)
            self.overlay.focus_set()
            
        except Exception as e:
            self.logger.error(f"Failed to finish recording: {e}")
            self._cleanup()
    
    def _complete_recording(self, event):
        """Complete the recording process"""
        try:
            self._cleanup()
            if self.callback:
                self.callback(self.recorded_clicks)
        except Exception as e:
            self.logger.error(f"Failed to complete recording: {e}")
    
    def _cancel_recording(self, event):
        """Cancel recording"""
        try:
            self.logger.info("Emergency click recording cancelled")
            self._cleanup()
        except Exception as e:
            self.logger.error(f"Failed to cancel recording: {e}")
    
    def _timeout_recording(self):
        """Handle recording timeout"""
        try:
            self.logger.warning("Emergency click recording timed out")
            if self.recorded_clicks:
                self.logger.info(f"Using {len(self.recorded_clicks)} recorded clicks")
                self._cleanup()
                if self.callback:
                    self.callback(self.recorded_clicks)
            else:
                self.logger.warning("No clicks recorded, cancelling")
                self._cleanup()
        except Exception as e:
            self.logger.error(f"Failed to handle timeout: {e}")
            self._cleanup()
    
    def _cleanup(self):
        """Clean up recording interface"""
        try:
            if self.overlay:
                self.overlay.grab_release()
                self.overlay.destroy()
                self.overlay = None
        except Exception as e:
            self.logger.error(f"Failed to cleanup recording interface: {e}")


class FoodPositionRecorder:
    """Simple recorder for 3 food positions"""
    
    def __init__(self, callback: callable):
        """
        Initialize food position recorder
        
        Args:
            callback: Function to call when all 3 positions are recorded
        """
        self.callback = callback
        self.overlay = None
        self.recorded_positions = []
        self.logger = logging.getLogger(__name__)
    
    def start_recording(self):
        """Start recording 3 food positions"""
        try:
            # Reset recorded positions
            self.recorded_positions = []
            
            # Create full-screen overlay for position recording
            self.overlay = tk.Toplevel()
            self.overlay.attributes('-fullscreen', True)
            self.overlay.attributes('-topmost', True)
            self.overlay.attributes('-alpha', 0.1)  # Semi-transparent
            self.overlay.configure(bg='black')
            
            # Create canvas for visual feedback
            self.canvas = tk.Canvas(self.overlay, highlightthickness=0)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
            # Add instructions
            self.canvas.create_text(
                self.overlay.winfo_screenwidth() // 2, 50,
                text="Click 3 positions for food locations",
                fill='white', font=('Arial', 16, 'bold')
            )
            
            self.canvas.create_text(
                self.overlay.winfo_screenwidth() // 2, 80,
                text="Click 1 of 3 - Press ESC to cancel",
                fill='yellow', font=('Arial', 14)
            )
            
            # Bind mouse events
            self.canvas.bind('<Button-1>', self._on_click)
            self.overlay.bind('<Escape>', self._cancel_recording)
            
            # Add a timeout to prevent infinite recording
            self.overlay.after(60000, self._timeout_recording)  # 60 second timeout
            
            # Focus the overlay
            self.overlay.focus_set()
            self.overlay.grab_set()
            
            self.logger.info("Started recording 3 food positions")
            
        except Exception as e:
            self.logger.error(f"Failed to start food position recording: {e}")
            self._cleanup()
    
    def _on_click(self, event):
        """Handle mouse click during recording"""
        try:
            # Record click location
            x, y = event.x_root, event.y_root
            self.recorded_positions.append((x, y))
            
            # Draw visual feedback
            self.canvas.create_oval(
                event.x - 10, event.y - 10,
                event.x + 10, event.y + 10,
                outline='lime', width=3, fill=''
            )
            
            # Update instruction text
            self.canvas.delete("instruction")
            click_count = len(self.recorded_positions)
            
            if click_count < 3:
                self.canvas.create_text(
                    self.overlay.winfo_screenwidth() // 2, 80,
                    text=f"Click {click_count + 1} of 3 - Press ESC to cancel",
                    fill='yellow', font=('Arial', 14), tags="instruction"
                )
                
                self.canvas.create_text(
                    event.x, event.y - 20,
                    text=f"Position {click_count} Recorded!",
                    fill='lime', font=('Arial', 12, 'bold')
                )
                
                self.logger.info(f"Recorded food position {click_count} at ({x}, {y})")
            else:
                # All 3 positions recorded
                self.canvas.create_text(
                    self.overlay.winfo_screenwidth() // 2, 80,
                    text="All 3 positions recorded! Completing...",
                    fill='green', font=('Arial', 14, 'bold'), tags="instruction"
                )
                
                self.canvas.create_text(
                    event.x, event.y - 20,
                    text="Position 3 Recorded!",
                    fill='lime', font=('Arial', 12, 'bold')
                )
                
                self.logger.info(f"Recorded final food position 3 at ({x}, {y})")
                
                # Wait a moment to show the feedback, then complete
                self.overlay.after(1500, self._complete_recording)
            
        except Exception as e:
            self.logger.error(f"Failed to record food position: {e}")
            self._cleanup()
    
    def _complete_recording(self):
        """Complete the recording process"""
        try:
            self._cleanup()
            if self.callback:
                self.callback(self.recorded_positions)
        except Exception as e:
            self.logger.error(f"Failed to complete food position recording: {e}")
    
    def _cancel_recording(self, event):
        """Cancel recording"""
        try:
            self.logger.info("Food position recording cancelled")
            self._cleanup()
            if self.callback:
                self.callback([])  # Empty list indicates cancellation
        except Exception as e:
            self.logger.error(f"Failed to cancel food position recording: {e}")
    
    def _timeout_recording(self):
        """Handle recording timeout"""
        try:
            self.logger.warning("Food position recording timed out")
            self._cleanup()
            if self.callback:
                self.callback([])  # Empty list indicates timeout
        except Exception as e:
            self.logger.error(f"Failed to handle food position recording timeout: {e}")
    
    def _cleanup(self):
        """Clean up resources"""
        try:
            if self.overlay:
                self.overlay.destroy()
                self.overlay = None
        except Exception as e:
            self.logger.error(f"Failed to cleanup food position recorder: {e}")


class RunePositionRecorder:
    """Recorder for 3 rune target positions"""

    def __init__(self, callback: callable):
        """
        Initialize rune position recorder

        Args:
            callback: Function to call when all 3 positions are recorded
        """
        self.callback = callback
        self.overlay = None
        self.recorded_positions = []
        self.logger = logging.getLogger(__name__)

    def start_recording(self):
        """Start recording 3 rune target positions"""
        try:
            # Reset recorded positions
            self.recorded_positions = []

            # Create full-screen overlay for position recording
            self.overlay = tk.Toplevel()
            self.overlay.attributes('-fullscreen', True)
            self.overlay.attributes('-topmost', True)
            self.overlay.attributes('-alpha', 0.1)  # Semi-transparent
            self.overlay.configure(bg='black')

            # Create canvas for visual feedback
            self.canvas = tk.Canvas(self.overlay, highlightthickness=0)
            self.canvas.pack(fill=tk.BOTH, expand=True)

            # Add instructions
            self.canvas.create_text(
                self.overlay.winfo_screenwidth() // 2, 50,
                text="Click 3 positions for rune target locations",
                fill='white', font=('Arial', 16, 'bold')
            )

            self.canvas.create_text(
                self.overlay.winfo_screenwidth() // 2, 80,
                text="Click 1 of 3 - Press ESC to cancel",
                fill='yellow', font=('Arial', 14), tags="instruction"
            )

            # Bind mouse events
            self.canvas.bind('<Button-1>', self._on_click)
            self.overlay.bind('<Escape>', self._cancel_recording)

            # Add a timeout to prevent infinite recording
            self.overlay.after(60000, self._timeout_recording)  # 60 second timeout

            # Focus the overlay
            self.overlay.focus_set()
            self.overlay.grab_set()

            self.logger.info("Started recording 3 rune target positions")

        except Exception as e:
            self.logger.error(f"Failed to start rune position recording: {e}")
            self._cleanup()

    def _on_click(self, event):
        """Handle mouse click during recording"""
        try:
            # Record click location
            x, y = event.x_root, event.y_root
            self.recorded_positions.append((x, y))

            # Draw visual feedback
            self.canvas.create_oval(
                event.x - 10, event.y - 10,
                event.x + 10, event.y + 10,
                outline='cyan', width=3, fill=''
            )

            # Update instruction text
            self.canvas.delete("instruction")
            click_count = len(self.recorded_positions)

            if click_count < 3:
                self.canvas.create_text(
                    self.overlay.winfo_screenwidth() // 2, 80,
                    text=f"Click {click_count + 1} of 3 - Press ESC to cancel",
                    fill='yellow', font=('Arial', 14), tags="instruction"
                )

                self.canvas.create_text(
                    event.x, event.y - 20,
                    text=f"Target {click_count} Recorded!",
                    fill='cyan', font=('Arial', 12, 'bold')
                )

                self.logger.info(f"Recorded rune target position {click_count} at ({x}, {y})")
            else:
                # All 3 positions recorded
                self.canvas.create_text(
                    self.overlay.winfo_screenwidth() // 2, 80,
                    text="All 3 target positions recorded! Completing...",
                    fill='green', font=('Arial', 14, 'bold'), tags="instruction"
                )

                self.canvas.create_text(
                    event.x, event.y - 20,
                    text="Target 3 Recorded!",
                    fill='cyan', font=('Arial', 12, 'bold')
                )

                self.logger.info(f"Recorded final rune target position 3 at ({x}, {y})")

                # Wait a moment to show the feedback, then complete
                self.overlay.after(1500, self._complete_recording)

        except Exception as e:
            self.logger.error(f"Failed to record rune position: {e}")
            self._cleanup()

    def _complete_recording(self):
        """Complete the recording process"""
        try:
            self._cleanup()
            if self.callback:
                self.callback(self.recorded_positions)
        except Exception as e:
            self.logger.error(f"Failed to complete rune position recording: {e}")

    def _cancel_recording(self, event):
        """Cancel recording"""
        try:
            self.logger.info("Rune position recording cancelled")
            self._cleanup()
            if self.callback:
                self.callback([])  # Empty list indicates cancellation
        except Exception as e:
            self.logger.error(f"Failed to cancel rune position recording: {e}")

    def _timeout_recording(self):
        """Handle recording timeout"""
        try:
            self.logger.warning("Rune position recording timed out")
            self._cleanup()
            if self.callback:
                self.callback([])  # Empty list indicates timeout
        except Exception as e:
            self.logger.error(f"Failed to handle rune position recording timeout: {e}")

    def _cleanup(self):
        """Clean up resources"""
        try:
            if self.overlay:
                self.overlay.destroy()
                self.overlay = None
        except Exception as e:
            self.logger.error(f"Failed to cleanup rune position recorder: {e}")
