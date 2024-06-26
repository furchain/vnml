from dataclasses import dataclass
from functools import partial
from typing import Iterator
from urllib.parse import quote

import reflex as rx
from bs4 import BeautifulSoup
from furchain.text.schema import LlamaCpp, ChatFormat
from pydantic import Field

BASE_URL = "http://127.0.0.1/"

SEED = 42


def background_url(keywords, width, height, seed=SEED):
    return f"{BASE_URL}image/cinematic,{quote(keywords, safe='')}?&width={width}&height={height}&seed={seed}"


def character_url(identifier, emotion, width=1024, height=1024, seed=SEED):
    return f"{BASE_URL}image/upper body,focus on face,{quote(f'{identifier},{emotion}', safe='')}?seed={seed}&rembg=true&height={height}&width={width}"


def music_url(keywords, seed=SEED):
    return f"{BASE_URL}music/{quote(keywords, safe='')}?seed={seed}"


def dialogue_url(text, seed=SEED):
    return f"{BASE_URL}speech/{quote(text)}?seed={seed}"

@dataclass
class Diff:
    do_log: dict
    undo_log: dict
    vnml: str


llm = LlamaCpp(chat_format=ChatFormat.Llama3)


def continue_vnml(vnml: str, ) -> Iterator[str]:
    #     prompt = f'''```vnml
    # <vnml lang="{DisplayState.lang}">
    # {vnml}
    # <!-- Continue with new scene, dialogue, options, and action based on the chosen action -->
    # <scene>
    # '''
    #     result = llm.invoke(prompt, n_predict=50)
    #     yield result
    yield f"<scene><background keywords='magic shop, wards activated, tense atmosphere, magical traps set'/><music keywords='futuristic, electronic, fast-paced, synth, digital sounds, 21st century'/></scene>"
    yield f"<character name='Aria' identifier='magic girl' emotion='happy'>欢迎来到魔法的世界，在这里有新奇的冒险等待着你</character>"
    yield "<options><title>hello</title><option>h1</option><option>h2</option></options>"



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
        do_log.update(
            {"background_url": background_url(background_keywords, 1600, 960),
             "music_url": music_url(music_keywords), "option_title": None,
             "options": []})
        return do_log
    elif vnml.startswith("<character"):
        soup = BeautifulSoup(vnml, 'lxml')
        character_name = soup.find("character")['name']
        character_identifier = soup.find("character").get("identifier")
        if not character_identifier:
            character_identifier = DisplayState._characters[character_name]["identifier"]
        character_emotion = soup.find("character").get("emotion")
        if not character_emotion:
            character_emotion = DisplayState._characters[character_name]["emotion"]
        text = soup.find("character").text.strip()
        do_log.update({
            "character_url": character_url(character_identifier, character_emotion, ),
            "character_name": character_name,
            "dialogue": text,
            "dialogue_url": dialogue_url(text)
        })
        DisplayState._characters["character_name"] = {
            "identifier": character_identifier,
            "emotion": character_emotion
        }
        return do_log
    elif vnml.startswith("<narration"):
        soup = BeautifulSoup(vnml, 'lxml')
        text = soup.find("narration").text.strip()
        do_log.update({"dialogue": text, "dialogue_url": dialogue_url(text)})
        return do_log
    elif vnml.startswith("<options"):
        soup = BeautifulSoup(vnml, 'lxml')
        option_title = soup.find("title").text.strip()
        options = [i.text.strip() for i in soup.find_all("option")]
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
    characters: dict[str, dict] = Field(default_factory=dict)  # {"name": {"identifier": "value"}}

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
    character_url: str | None = None
    character_name: str | None = None
    dialogue: str | None = None  # "Hello, world!"
    dialogue_url: str | None = None
    option_title: str | None
    options: list[str] = []
    diff_history: list[dict] = [
    ]
    diff_pointer: int = -1
    lang: str = 'en'
    _characters: dict[str, dict] = {}

    @rx.var
    def last_button_disabled(self) -> bool:
        return self.diff_pointer <= 0


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
            characters=self._characters
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
        self.diff_history = self.diff_history[:self.diff_pointer]  # clear the future
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
        print(self.export_snapshot())
        diff = self.diff_history[self.diff_pointer]
        self.import_snapshot(self.export_snapshot() - Diff(**diff))
        self.diff_pointer -= 1


def display_options() -> rx.Component:

    return rx.box(
        rx.text(DisplayState.option_title, size="6", style={"font-weight": "bold"}),
        rx.foreach(DisplayState.options, lambda i: rx.button(i, on_click=partial(DisplayState.select_option, i))),
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
        rx.button("<-", on_click=DisplayState.backward, disabled=DisplayState.last_button_disabled),
        rx.button("->", on_click=DisplayState.forward),
        background_color="rgba(255, 0, 255, 0.7)",  # half opacity
        justify_content="center",  # center the text horizontally
        align_items="center",  # center the text vertically
        position="absolute",  # position it at the center of its parent
        bottom="0",  # position it at the center
        left="20%",  # position it at the center
        transform="translate(-50%, -50%)"  # ensure it's centered
    )


def display_dialogue() -> rx.Component:
    """The dialogue box.

    Returns:
        The dialogue box component.
    """
    return rx.box(
        rx.text(DisplayState.dialogue, color_scheme="brown", size="5", style={"font-weight": "bold"},
                justify_content="center",  # center the text horizontally
                align_items="center",  # center the text vertically
                width="100%",  # take the full width of the parent
                display="flex",
                padding="1em",
                border_radius="1em",
                background_color="rgba(255, 0, 255, 0.5)",  # half opacity
                ),
        rx.cond(
            DisplayState.character_url,
            rx.image(
                DisplayState.character_url,
                position="absolute",
                width="512px",
                height="512px",
                bottom="0",  # position it at the bottom
                z_index="-1",  # ensure it's on bottom of the dialogue box
            )
        ),
        rx.audio(
            url=DisplayState.dialogue_url,
            playing=True,
            controls=False,
            width="0",
            height="0",
            position="absolute",  # position it at the bottom left
            bottom="0",  # position it at the bottom
            left="0",  # position it at the left
        ),
        padding="1em",
        border_radius="1em",
        width="fit-content",
        position="absolute",  # position it at the center bottom
        height="fit-content",
        bottom="0",  # position it at the bottom
        left="50%",  # position it at the center
        transform="translate(-50%)"  # ensure it's centered
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
        height="0",
        width="0",
        position="absolute",  # position it at the bottom left
        bottom="0",  # position it at the bottom
        left="0",  # position it at the left
    )

def playground() -> rx.Component:
    """The dashboard page.

    Returns:
        The UI for the dashboard page.
    """

    return rx.box(
        rx.cond(
            DisplayState.dialogue,
            display_dialogue()
        ),
        rx.cond(
            DisplayState.option_title,
            display_options()
        ),
        rx.cond(
            DisplayState.music_url,
            display_audio()
        ),
        display_controller(),
        width="1280px",
        height="720px",
        background_image=f"url('{DisplayState.background_url}')",
        background_size="cover",  # Ensures the background image covers the entire parent element
        background_position="center",  # Centers the background image within the parent element
        background_repeat="no-repeat",
        position="relative"
    )
