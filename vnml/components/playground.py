from dataclasses import dataclass
from functools import partial
from typing import Iterator
from urllib.parse import quote

import reflex as rx
from bs4 import BeautifulSoup
from furchain.text.schema import LlamaCpp, ChatFormat

BASE_URL = "http://127.0.0.1/"
BACKGROUND_URL = f"{BASE_URL}image/"
CHARACTER_URL = f"{BASE_URL}character/"
MUSIC_URL = f"{BASE_URL}music/"
dialogue_url = f"{BASE_URL}speech/"
SEED = 42
@dataclass
class Diff:
    do_log: dict
    undo_log: dict
    vnml: str


llm = LlamaCpp(chat_format=ChatFormat.Llama3)


def continue_vnml(vnml: str, ) -> Iterator[str]:
    print("vnml", vnml)
    #     prompt = f'''```vnml
    # <vnml lang="{DisplayState.lang}">
    # {vnml}
    # <!-- Continue with new scene, dialogue, options, and action based on the chosen action -->
    # <scene>
    # '''
    #     result = llm.invoke(prompt, n_predict=50)
    #     yield result
    yield f"<scene><background keywords='magic shop, wards activated, tense atmosphere, magical traps set'/><music keywords='futuristic, electronic, fast-paced, synth, digital sounds, 21st century'/></scene>"



def vnml2log(vnml: str) -> dict:
    do_log = {
        "character_url": None,
        "character_name": None,
        "dialogue": None,
        "dialogue_url": None,
        "option_title": None,
        "options": []
    }
    if vnml.startswith("<scene"):
        soup = BeautifulSoup(vnml, 'lxml')
        background_keywords = soup.find("background")['keywords']
        music_keywords = soup.find("music")['keywords']
        background_keywords_encoded = quote(background_keywords, safe='')
        music_keywords_encoded = quote(music_keywords, safe='')
        do_log.update(
            {"background_url": f"{BACKGROUND_URL}{background_keywords_encoded}?width=1600&height=960&seed={SEED}",
             "music_url": f"{MUSIC_URL}{music_keywords_encoded}&seed={SEED}", "option_title": None,
             "options": []})
        return do_log
    elif vnml.startswith("<character"):
        soup = BeautifulSoup(vnml, 'lxml')
        character_name = soup.find("character")['name']
        character_identifier = soup.find("character").get("identifier",
                                                          DisplayState.characters[character_name]["identifier"])
        character_emotion = soup.find("character").get("emotion", DisplayState.characters[character_name]["emotion"])
        dialogue = soup.find("dialogue").text.strip()
        character_keywords_encoded = quote(f"{character_identifier},{character_emotion}", safe='')
        do_log.update({
            "character_url": f"{CHARACTER_URL}{character_keywords_encoded}&seed={SEED}",
            "character_name": character_name,
            "dialogue": dialogue,
            "dialogue_url": f"{dialogue_url}{dialogue}"
        })
        DisplayState.characters["character_name"] = {
            "identifier": character_identifier,
            "emotion": character_emotion
        }
        return do_log
    elif vnml.startswith("<narration"):
        soup = BeautifulSoup(vnml, 'lxml')
        dialogue = soup.find("narration").text.strip()
        do_log.update({"dialogue": dialogue, "dialogue_url": f"{dialogue_url}{dialogue}"})
        return do_log
    elif vnml.startswith("<options"):
        soup = BeautifulSoup(vnml, 'lxml')
        option_title = soup.find("options")['title']
        options = [i.text for i in soup.find_all("option")]
        do_log.update({"option_title": option_title, "options": options})
        return do_log
    return {"dialogue": vnml, "option_title": None, "options": []}


@dataclass
class GameSnapshot:
    background_url: str
    music_url: str
    character_url: str
    character_name: str
    dialogue: str
    dialogue_url: str
    option_title: str
    options: list[str]
    characters: dict  # {"name": "identifier"}

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
    character_url: str | None = "/test.png"
    character_name: str | None = None
    dialogue: str | None = None  # "Hello, world!"
    dialogue_url: str | None = None
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
    lang: str = 'en'
    characters: dict = {}

    @property
    def last_button_active(self):
        return self.diff_pointer > 0

    @property
    def next_button_active(self):
        return not self.diff_history[self.diff_pointer + 1]

    def export_snapshot(self) -> GameSnapshot:
        return GameSnapshot(
            background_url=self.background_url,
            music_url=self.music_url,
            character_url=self.character_url,
            character_name=self.character_name,
            dialogue=self.dialogue,
            dialogue_url=self.dialogue_url,
            option_title=self.option_title,
            options=self.options,
            characters=self.characters
        )

    def import_snapshot(self, snapshot: GameSnapshot):
        self.background_url = snapshot.background_url
        self.music_url = snapshot.music_url
        self.character_url = snapshot.character_url
        self.character_name = snapshot.character_name
        self.dialogue = snapshot.dialogue
        self.dialogue_url = snapshot.dialogue_url
        self.option_title = snapshot.option_title
        self.options = snapshot.options

    def select_option(self, option: str):
        self.diff_history.append(
            {"do_log": {"dialogue": f"Option {option} selected", "option_title": None, "options": []},
             "undo_log": {"dialogue": None, "option_title": self.option_title, "options": self.options},
             "vnml": f"<action>{option}</action>"}
        )
        self.forward()

    def forward(self):
        if len(self.diff_history) <= self.diff_pointer + 1:
            history_vnml = ''.join([i['vnml'] for i in self.diff_history[:self.diff_pointer]])
            snapshot = self.export_snapshot()
            for vnml in continue_vnml(history_vnml):
                do_log = vnml2log(vnml)
                diff = calculate_diff(snapshot, do_log, vnml)
                self.diff_history.append(diff.__dict__)
                snapshot += diff
        diff = self.diff_history[self.diff_pointer + 1]
        self.import_snapshot(self.export_snapshot() + Diff(**diff))
        self.diff_pointer += 1
        if diff["do_log"].get("background_url"):  # new scene, automatically continue
            self.forward()

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
        rx.button("<-", on_click=DisplayState.backward),
        rx.button("->", on_click=DisplayState.forward),
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


def display_audio() -> rx.Component:
    """The audio player.

    Returns:
        The audio player component.
    """
    return rx.audio(
        url=DisplayState.music_url,
        playing=True,
        loop=True,
        controls=False,
        width="100%",
        position="absolute",  # position it at the bottom left
        bottom="0",  # position it at the bottom
        left="0",  # position it at the left
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
    if DisplayState.music_url is not None:
        children.append(display_audio())
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
