from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from .config import load_release_config


class StepsList(ListView):
    def __init__(self, steps, **kwargs):
        super().__init__(**kwargs)
        self.steps = steps
        self.current_step = 0

    def on_mount(self) -> None:
        for i, step in enumerate(self.steps):
            list_item = ListItem(Label(f"{i + 1}. {step.title}"))
            self.append(list_item)
        if self.steps:
            self.index = 0


class LeftPanel(Static):
    def __init__(self, steps, **kwargs):
        super().__init__(**kwargs)
        self.steps = steps

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Steps", classes="steps-header")
            yield StepsList(self.steps, classes="steps-list")


class RightPanel(Static):
    def compose(self) -> ComposeResult:
        yield Static("Logs", classes="panel-content")


class ReleaseApp(App):
    CSS_PATH = "tui.tcss"
    BINDINGS = [
        Binding("up", "move_up", "Move Up"),
        Binding("down", "move_down", "Move Down"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_path = Path("nogit/release.yaml")
        self.config = load_release_config(self.config_path)
        self.current_step_index = 0

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical():
            yield Static(
                f"Current Step: {self.current_step_index + 1}/{len(self.config.steps)} - {self.config.steps[self.current_step_index].title}",
                classes="current-step",
                id="current-step",
            )

            with Horizontal(classes="main-content"):
                yield LeftPanel(self.config.steps, classes="left-panel")
                yield RightPanel(classes="right-panel")

        yield Footer()

    def action_move_up(self) -> None:
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.update_current_step()
            steps_list = self.query_one(StepsList)
            steps_list.index = self.current_step_index

    def action_move_down(self) -> None:
        if self.current_step_index < len(self.config.steps) - 1:
            self.current_step_index += 1
            self.update_current_step()
            steps_list = self.query_one(StepsList)
            steps_list.index = self.current_step_index

    def update_current_step(self) -> None:
        current_step_widget = self.query_one("#current-step", Static)
        current_step_widget.update(
            f"Current Step: {self.current_step_index + 1}/{len(self.config.steps)} - {self.config.steps[self.current_step_index].title}"
        )


if __name__ == "__main__":
    ReleaseApp().run()
