import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Footer, Header, Label, ListItem, ListView, Markdown, Static
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .config import load_release_config, parse_initial_variables


class TUIFileHandler(FileSystemEventHandler):
    def __init__(self, restart_callback):
        super().__init__()
        self.restart_callback = restart_callback

    def on_modified(self, event):
        if not event.is_directory and (
            event.src_path.endswith(".py") or event.src_path.endswith(".tcss")
        ):
            self.restart_callback()


class StepsList(ListView):
    def __init__(self, steps, current_step_index=0, **kwargs):
        super().__init__(**kwargs)
        self.steps = steps
        self.current_step_index = current_step_index

    def on_mount(self) -> None:
        for i, step in enumerate(self.steps):
            list_item = ListItem(Label(f"{i + 1}. {step.title}"))
            self.append(list_item)
        if self.steps:
            # Schedule the index setting after the next refresh to ensure ListView is fully initialized
            self.call_after_refresh(self._set_initial_selection)

    def _set_initial_selection(self) -> None:
        """Set the initial selection after the ListView is fully initialized"""
        if 0 <= self.current_step_index < len(self.steps):
            self.index = self.current_step_index

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Handle step highlighting from the ListView"""
        highlighted_index = event.list_view.index
        if highlighted_index is not None:
            self.post_message(self.StepSelected(highlighted_index))

    class StepSelected(Message):
        """Message sent when a step is selected"""

        def __init__(self, step_index: int):
            super().__init__()
            self.step_index = step_index


class LeftPanel(Static):
    def __init__(self, steps, current_step_index=0, **kwargs):
        super().__init__(**kwargs)
        self.steps = steps
        self.current_step_index = current_step_index

    def compose(self) -> ComposeResult:
        with Vertical():
            progress_text = f"Steps ({self.current_step_index + 1}/{len(self.steps)})"
            yield Static(progress_text, classes="steps-header", id="steps-header")
            yield StepsList(self.steps, self.current_step_index, classes="steps-list")

    def update_progress(self, current_step_index):
        """Update the progress display"""
        self.current_step_index = current_step_index
        header_widget = self.query_one("#steps-header", Static)
        progress_text = f"Steps ({current_step_index + 1}/{len(self.steps)})"
        header_widget.update(progress_text)


class RightPanel(Static):
    def __init__(self, current_step=None, **kwargs):
        super().__init__(**kwargs)
        self.current_step = current_step

    def compose(self) -> ComposeResult:
        with Vertical():
            header_text = (
                self.current_step.title
                if self.current_step and self.current_step.title
                else "No step selected"
            )
            yield Static(
                header_text, classes="description-header", id="description-header"
            )
            description_text = (
                self.current_step.description
                if self.current_step and self.current_step.description
                else "No description available"
            )
            yield Markdown(
                description_text,
                classes="description-content",
                id="description-content",
            )

    def update_description(self, step):
        """Update the description content and header with a new step"""
        # Update header with step title
        header_widget = self.query_one("#description-header", Static)
        header_text = step.title if step.title else "No step selected"
        header_widget.update(header_text)

        # Update description content
        description_widget = self.query_one("#description-content", Markdown)
        description_text = (
            step.description if step.description else "No description available"
        )
        description_widget.update(description_text)


class ReleaseApp(App):
    CSS_PATH = "tui.tcss"
    BINDINGS = [
        Binding("up", "move_up", "Move Up"),
        Binding("down", "move_down", "Move Down"),
    ]

    def __init__(
        self, config_path=None, restart_on_change=False, initial_state=None, **kwargs
    ):
        super().__init__(**kwargs)
        self.config_path = config_path or Path("nogit/release.yaml")
        self.config = load_release_config(self.config_path)

        # Initialize state from previous run or defaults
        if initial_state:
            self.current_step_index = initial_state.get("current_step_index", 0)
            self.variables = initial_state.get("variables")
        else:
            self.current_step_index = 0
            self.variables = None

        # Initialize variables if not already set
        if self.variables is None:
            self.variables = parse_initial_variables(self.config, os.environ)

        self.restart_on_change = restart_on_change
        self.observer = None
        self.should_restart = False

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(classes="main-content"):
            yield LeftPanel(
                self.config.steps, self.current_step_index, classes="left-panel"
            )
            yield RightPanel(
                self.config.steps[self.current_step_index],
                classes="right-panel",
                id="right-panel",
            )

        yield Footer()

    def action_move_up(self) -> None:
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.update_current_step()
            # Update ListView selection after a refresh to ensure proper synchronization
            self.call_after_refresh(self._sync_listview_selection)

    def action_move_down(self) -> None:
        if self.current_step_index < len(self.config.steps) - 1:
            self.current_step_index += 1
            self.update_current_step()
            # Update ListView selection after a refresh to ensure proper synchronization
            self.call_after_refresh(self._sync_listview_selection)

    def _sync_listview_selection(self) -> None:
        """Synchronize the ListView selection with current_step_index"""
        steps_list = self.query_one(StepsList)
        steps_list.index = self.current_step_index

    def update_current_step(self) -> None:
        # Update the left panel progress
        left_panel = self.query_one(".left-panel", LeftPanel)
        left_panel.update_progress(self.current_step_index)

        # Update the right panel description
        right_panel = self.query_one("#right-panel", RightPanel)
        right_panel.update_description(self.config.steps[self.current_step_index])

    def on_steps_list_step_selected(self, message: StepsList.StepSelected) -> None:
        """Handle step selection from the steps list"""
        self.current_step_index = message.step_index
        self.update_current_step()

    def restart_app(self):
        """Callback to restart the app when files change"""
        self.should_restart = True
        self.exit()

    def get_state(self):
        """Return current app state for persistence across restarts"""
        return {
            "current_step_index": self.current_step_index,
            "variables": self.variables,
        }

    def on_mount(self) -> None:
        """Set up file watcher when app starts"""
        if self.restart_on_change:
            self.setup_file_watcher()

    def setup_file_watcher(self):
        """Set up the file watcher for Python and CSS files in the release package"""
        release_package_path = Path(__file__).parent

        self.observer = Observer()
        event_handler = TUIFileHandler(self.restart_app)
        self.observer.schedule(event_handler, str(release_package_path), recursive=True)
        self.observer.start()

    def on_unmount(self) -> None:
        """Clean up file watcher when app exits"""
        if self.observer:
            self.observer.stop()
            self.observer.join()


if __name__ == "__main__":
    ReleaseApp().run()
