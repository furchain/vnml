from dataclasses import dataclass
from functools import partial
from typing import Iterator

import reflex as rx


@dataclass
class Diff:
    do_log: dict
    undo_log: dict
    vnml: str


def continue_vnml(vnml: str, option: str) -> Iterator[str]:
    print(option)
    # TODO: continue vnml
    yield f"<button>{option}</button>"
    yield f"<button2>{option}</button>"
    yield f"<button3>{option}</button>"


def vnml2log(vnml: str) -> dict:
    return {"dialogue": vnml, "option_title": None, "options": []}


@dataclass
class GameSnapshot:
    background_url: str
    music_url: str
    character_url: str
    character_name: str
    dialogue: str
    option_title: str
    options: list[str]

    def __add__(self, diff: Diff):
        state = self.__dict__.copy()
        for key, value in diff.do_log.items():
            state[key] = value
        return GameSnapshot(**state)

    def __sub__(self, diff: Diff):
        state = self.__dict__.copy()
        for key, value in diff.undo_log.items():
            state[key] = value
        return GameSnapshot(**state)


def calculate_diff(snapshot: GameSnapshot, do_log: dict, vnml: str) -> Diff:
    undo_log = {}
    for key, value in do_log.items():
        if value != snapshot.__dict__[key]:
            undo_log[key] = snapshot.__dict__[key]
    return Diff(do_log, undo_log, vnml)


class DisplayState(rx.State):
    background_url: str | None = None  #
    music_url: str | None = None
    character_url: str | None = None  # "https://w7.pngwing.com/pngs/215/579/png-transparent-girl-graphy-portrait-asian-girl-thumbnail.png"
    character_name: str | None = None
    dialogue: str | None = None  # "Hello, world!"
    option_title: str | None
    options: list[str] = []
    diff_history: list[dict] = [
        dict(do_log={
            "background_url": "https://fastly.picsum.photos/id/576/200/300.jpg?hmac=Uf-okGnisfAphCT3N-WTyzaG-e-r9yvOhY3W43DMWwA",
            "option_title": "Choose your destiny",
            "options": ["Option 1", "Option 2"]},
            undo_log={},
            vnml='')
    ]
    diff_pointer: int = -1

    @property
    def last_button_active(self):
        return self.diff_pointer > 0

    @property
    def next_button_active(self):
        not self.diff_history[self.diff_pointer + 1]

    def export_snapshot(self) -> GameSnapshot:
        return GameSnapshot(
            background_url=self.background_url,
            music_url=self.music_url,
            character_url=self.character_url,
            character_name=self.character_name,
            dialogue=self.dialogue,
            option_title=self.option_title,
            options=self.options
        )

    def import_snapshot(self, snapshot: GameSnapshot):
        self.background_url = snapshot.background_url
        self.music_url = snapshot.music_url
        self.character_url = snapshot.character_url
        self.character_name = snapshot.character_name
        self.dialogue = snapshot.dialogue
        self.option_title = snapshot.option_title
        self.options = snapshot.options

    def select_option(self, option: str):
        history_vnml = ''.join([i['vnml'] for i in self.diff_history[:self.diff_pointer]])
        snapshot = self.export_snapshot()
        for vnml in continue_vnml(history_vnml, option):
            do_log = vnml2log(vnml)
            diff = calculate_diff(snapshot, do_log, vnml)
            self.diff_history.append(diff.__dict__)
            snapshot += diff
        self.forward()

    def forward(self):
        diff = self.diff_history[self.diff_pointer + 1]
        self.import_snapshot(self.export_snapshot() + Diff(**diff))
        self.diff_pointer += 1

    def backward(self):
        diff = self.diff_history[self.diff_pointer]
        self.import_snapshot(self.export_snapshot() - Diff(**diff))
        self.diff_pointer -= 1


def display_options() -> rx.Component:
    children = [
        rx.text(DisplayState.option_title, size="6", style={"font-weight": "bold"}),
    ]
    children += [
        rx.foreach(DisplayState.options, lambda i: rx.button(i, on_click=partial(DisplayState.select_option, i)))]
    return rx.box(

        *children,
        background_color="rgba(255, 0, 255, 0.7)",  # half opacity
        justify_content="center",  # center the text horizontally
        align_items="center",  # center the text vertically
        position="absolute",  # position it at the center of its parent
        bottom="0",  # position it at the center
        left="50%",  # position it at the center
        transform="translate(-50%, -50%)"  # ensure it's centered
    )


def display_controller() -> rx.Component:
    return rx.box(
        rx.button("Go", on_click=DisplayState.forward),
        background_color="rgba(255, 0, 255, 0.7)",  # half opacity
        justify_content="center",  # center the text horizontally
        align_items="center",  # center the text vertically
        position="absolute",  # position it at the center of its parent
        bottom="0",  # position it at the center
        left="20%",  # position it at the center
        transform="translate(-50%, -50%)"  # ensure it's centered
    )


def display_character() -> rx.Component:
    """The character image.

    Returns:
        The character image component.
    """
    return rx.image(
        DisplayState.character_url,
        width="100px",
        height="100px",
        border_radius="50%",
        position="absolute",  # position it at the bottom left
        bottom="0",  # position it at the bottom
        left="0",  # position it at the left
    )


def display_dialogue() -> rx.Component:
    """The dialogue box.

    Returns:
        The dialogue box component.
    """
    return rx.box(
        rx.text(DisplayState.dialogue, color_scheme="cyan", size="6", style={"font-weight": "bold"}),
        padding="1em",
        border_radius="1em",
        background_color="rgba(255, 255, 255, 0.7)",  # half opacity
        margin="1em",
        width="fit-content",
        position="absolute",  # position it at the center bottom
        bottom="0",  # position it at the bottom
        left="50%",  # position it at the center
        transform="translate(-50%, -50%)"  # ensure it's centered
    )


def playground() -> rx.Component:
    """The dashboard page.

    Returns:
        The UI for the dashboard page.
    """
    children = []
    if DisplayState.dialogue is not None:
        children.append(display_dialogue())
    if DisplayState.character_url is not None:
        children.append(display_character())
    if DisplayState.option_title is not None:
        children.append(display_options())
    return rx.box(
        *children,
        display_controller(),
        width="1280px",
        height="720px",
        background_image=f"url('{DisplayState.background_url}')",
        background_size="cover",  # Ensures the background image covers the entire parent element
        background_position="center",  # Centers the background image within the parent element
        background_repeat="no-repeat",
        position="relative"
    )
