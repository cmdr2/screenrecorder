import tkinter as tk
import os
import subprocess
import tempfile

from .. import theme
from ..utils import get_ffmpeg_path


class Toolbar:
    def __init__(self, parent, video_player, video_path, preview_window=None):
        self.parent = parent
        self.video_player = video_player
        self.video_path = video_path
        self.preview_window = preview_window  # Reference to PreviewEditorWindow for toast messages
        self.video_history = [video_path]  # Track video versions for undo
        self.current_video_index = 0

        # State tracking
        self.active_panel = None  # 'trim' or 'resize'
        # Set initial end time to video duration
        self.initial_end_time = self._get_video_duration_str()

        # Create main toolbar frame
        self.toolbar_frame = tk.Frame(parent, bg=theme.COLOR_BG)
        self.toolbar_frame.pack(fill=tk.X, padx=0, pady=0)

        # Create buttons frame
        self.buttons_frame = tk.Frame(self.toolbar_frame, bg=theme.COLOR_BG)
        self.buttons_frame.pack(side=tk.TOP, fill=tk.X, padx=theme.PANEL_PADX, pady=theme.PANEL_PADY)

        # Create buttons
        self.trim_button = self._create_button("Trim", self._toggle_trim_panel)
        self.resize_button = self._create_button("Resize", self._toggle_resize_panel)

        # Create panels frame (hidden by default)
        self.panels_frame = tk.Frame(self.toolbar_frame, bg=theme.COLOR_BG)

        # Initialize panels
        self._create_trim_panel()
        self._create_resize_panel()

    def _create_button(self, text, command):
        """Create a themed button for the toolbar."""
        button = tk.Button(
            self.buttons_frame,
            text=text,
            command=command,
            bg=theme.BTN_BG,
            fg=theme.BTN_FG,
            font=theme.BTN_FONT,
            relief=theme.BTN_RELIEF,
            bd=theme.BTN_BORDER_WIDTH,
            padx=theme.BTN_PADX,
            pady=theme.BTN_PADY,
            cursor="hand2",
        )
        button.pack(side=tk.LEFT, padx=(0, theme.BTN_PACK_PADX))

        # Hover effects
        def on_enter(e):
            if button != self._get_active_button():
                button.config(bg=theme.BTN_ACTIVE_BG)

        def on_leave(e):
            if button != self._get_active_button():
                button.config(bg=theme.BTN_BG)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

        return button

    def _get_active_button(self):
        """Get the currently active button based on active panel."""
        if self.active_panel == "trim":
            return self.trim_button
        elif self.active_panel == "resize":
            return self.resize_button
        return None

    def _update_button_states(self):
        """Update visual state of buttons."""
        # Reset all buttons to normal state
        self.trim_button.config(bg=theme.BTN_BG, fg=theme.BTN_FG)
        self.resize_button.config(bg=theme.BTN_BG, fg=theme.BTN_FG)

        # Highlight active button
        active_button = self._get_active_button()
        if active_button:
            active_button.config(bg=theme.BTN_ACTIVE_BG, fg=theme.BTN_ACTIVE_FG)

    def _show_panel(self, panel_name):
        """Show specified panel and hide others."""
        # Hide all panels first
        self.trim_panel.pack_forget()
        self.resize_panel.pack_forget()

        # Show requested panel
        if panel_name == "trim":
            self.trim_panel.pack(fill=tk.X, padx=theme.PANEL_PADX, pady=(0, theme.PANEL_PADY))
        elif panel_name == "resize":
            self.resize_panel.pack(fill=tk.X, padx=theme.PANEL_PADX, pady=(0, theme.PANEL_PADY))

        # Show panels frame if a panel is active
        if panel_name:
            self.panels_frame.pack(fill=tk.X, after=self.buttons_frame)
        else:
            self.panels_frame.pack_forget()

    def _toggle_trim_panel(self):
        """Toggle the trim panel visibility."""
        if self.active_panel == "trim":
            # Close current panel
            self.active_panel = None
            self._show_panel(None)
        else:
            # Open trim panel
            self.active_panel = "trim"
            self._show_panel("trim")

        self._update_button_states()

    def _toggle_resize_panel(self):
        """Toggle the resize panel visibility."""
        if self.active_panel == "resize":
            # Close current panel
            self.active_panel = None
            self._show_panel(None)
        else:
            # Open resize panel
            self.active_panel = "resize"
            self._show_panel("resize")

        self._update_button_states()

    def _create_trim_panel(self):
        """Create the trim panel with controls."""
        self.trim_panel = tk.Frame(
            self.panels_frame,
            bg=theme.PANEL_BG,
            relief="solid",
            bd=theme.PANEL_BORDER_WIDTH,
            highlightbackground=theme.PANEL_BORDER_COLOR,
            highlightthickness=theme.PANEL_BORDER_WIDTH,
        )

        # Controls frame
        controls_frame = tk.Frame(self.trim_panel, bg=theme.PANEL_BG)
        controls_frame.pack(fill=tk.X, padx=theme.PANEL_PADX, pady=theme.PANEL_PADY)

        # Start time controls
        start_frame = tk.Frame(controls_frame, bg=theme.PANEL_BG)
        start_frame.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            start_frame, text="Start Time (sec):", bg=theme.PANEL_BG, fg=theme.COLOR_FG, font=("Segoe UI", 10)
        ).pack(anchor=tk.W)

        self.start_time_var = tk.StringVar(value="0")
        self.start_time_entry = tk.Entry(start_frame, textvariable=self.start_time_var, width=8, font=("Segoe UI", 10))
        self.start_time_entry.pack(anchor=tk.W, pady=(2, 0))

        # End time controls
        end_frame = tk.Frame(controls_frame, bg=theme.PANEL_BG)
        end_frame.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(end_frame, text="End Time (sec):", bg=theme.PANEL_BG, fg=theme.COLOR_FG, font=("Segoe UI", 10)).pack(
            anchor=tk.W
        )

        # Set end time to current video duration by default
        self.end_time_var = tk.StringVar(value=self.initial_end_time)
        self.end_time_entry = tk.Entry(end_frame, textvariable=self.end_time_var, width=8, font=("Segoe UI", 10))
        self.end_time_entry.pack(anchor=tk.W, pady=(2, 0))

        # Buttons frame
        buttons_frame = tk.Frame(controls_frame, bg=theme.PANEL_BG)
        buttons_frame.pack(side=tk.LEFT)

        # Apply button
        self.apply_button = tk.Button(
            buttons_frame,
            text="Trim",
            command=self._apply_trim,
            bg=theme.COLOR_PRIMARY,
            fg=theme.COLOR_FG,
            font=("Segoe UI", 10, "bold"),
            relief=theme.BTN_RELIEF,
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
        )
        self.apply_button.pack(side=tk.LEFT, padx=(0, 8))

        # Undo button
        self.undo_button = tk.Button(
            buttons_frame,
            text="Undo",
            command=self._undo_trim,
            bg=theme.COLOR_TERTIARY,
            fg=theme.COLOR_FG,
            font=("Segoe UI", 10, "bold"),
            relief=theme.BTN_RELIEF,
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
        )
        self.undo_button.pack(side=tk.LEFT)

        # Update undo button state
        self._update_undo_button_state()

    def _create_resize_panel(self):
        """Create the resize panel placeholder."""
        self.resize_panel = tk.Frame(
            self.panels_frame,
            bg=theme.PANEL_BG,
            relief="solid",
            bd=theme.PANEL_BORDER_WIDTH,
            highlightbackground=theme.PANEL_BORDER_COLOR,
            highlightthickness=theme.PANEL_BORDER_WIDTH,
        )

        # Coming soon message
        message_frame = tk.Frame(self.resize_panel, bg=theme.PANEL_BG)
        message_frame.pack(fill=tk.X, padx=theme.PANEL_PADX, pady=theme.PANEL_PADY)

        tk.Label(
            message_frame,
            text="🚧 Coming soon...",
            bg=theme.PANEL_BG,
            fg=theme.COLOR_TERTIARY,
            font=("Segoe UI", 12, "italic"),
        ).pack()

    def _apply_trim(self):
        """Apply video trimming using ffmpeg."""
        try:
            start_time = float(self.start_time_var.get() or "0")
            end_time_str = self.end_time_var.get().strip()

            if not end_time_str:
                self._show_error("Please enter an end time.")
                return

            end_time = float(end_time_str)

            if start_time >= end_time:
                self._show_error("Start time must be less than end time.")
                return

            if start_time < 0:
                self._show_error("Start time must be positive.")
                return

            # Create temporary file for trimmed video
            temp_fd, temp_path = tempfile.mkstemp(suffix=".mp4")
            os.close(temp_fd)

            # Build ffmpeg command
            current_video = self.video_history[self.current_video_index]
            ffmpeg_path = get_ffmpeg_path()

            duration = end_time - start_time

            cmd = [
                ffmpeg_path,
                "-ss",
                str(start_time),
                "-i",
                current_video,
                "-c",
                "copy",
                "-t",
                str(duration),
                "-y",  # Overwrite output file
                temp_path,
            ]

            # Execute ffmpeg command
            process = subprocess.run(cmd, capture_output=True, text=True)

            if process.returncode == 0:
                # Success - update video player and history
                self._add_to_history(temp_path)
                print(temp_path)
                self.video_player.src = temp_path
                self._show_success("Video trimmed successfully!")

                # Reset form
                self.start_time_var.set("0")
                # Update end time to new duration
                self.end_time_var.set(self._get_video_duration_str())

                # Update undo button state
                self._update_undo_button_state()
            else:
                self._show_error(f"Trimming failed: {process.stderr}")
                # Clean up temp file on failure
                try:
                    os.unlink(temp_path)
                except:
                    pass

        except ValueError:
            self._show_error("Please enter valid numeric values for times.")
        except Exception as e:
            self._show_error(f"An error occurred: {str(e)}")

    def _undo_trim(self):
        """Undo the last trim operation."""
        if self.current_video_index > 0:
            self.current_video_index -= 1
            previous_video = self.video_history[self.current_video_index]
            self.video_player.src = previous_video
            # Update end time to previous video's duration
            self.end_time_var.set(self._get_video_duration_str())
            self._show_success("Undo successful!")
            self._update_undo_button_state()

    def _add_to_history(self, video_path):
        """Add a new video to the history."""
        # Remove any history after current index (if user undid and then made new changes)
        self.video_history = self.video_history[: self.current_video_index + 1]

        # Add new video
        self.video_history.append(video_path)
        self.current_video_index += 1

    def _update_undo_button_state(self):
        """Enable/disable undo button based on history."""
        if hasattr(self, "undo_button"):
            if self.current_video_index > 0:
                self.undo_button.config(state=tk.NORMAL, bg=theme.COLOR_TERTIARY)
            else:
                self.undo_button.config(state=tk.DISABLED, bg="#555")

    def _show_error(self, message):
        """Show error message to user."""
        if self.preview_window and hasattr(self.preview_window, "show_toast"):
            self.preview_window.show_toast(f"❌ {message}")
        else:
            print(f"Error: {message}")

    def _show_success(self, message):
        """Show success message to user."""
        if self.preview_window and hasattr(self.preview_window, "show_toast"):
            self.preview_window.show_toast(f"✅ {message}")
        else:
            print(f"Success: {message}")

    def _get_video_duration_str(self):
        """Get the duration of the current video as a string."""
        return str(round(self.video_player.duration, 1))

    def get_current_video_path(self):
        """Get the path of the currently active video."""
        return self.video_history[self.current_video_index]
