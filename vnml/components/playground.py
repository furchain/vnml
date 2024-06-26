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

outputs = ["```vnml\n<vnml lang=\"en\">\n<action>Start!</action>\n<scene>\n<background keywords=\"old town, cobblestone streets, twilight, foggy, mysterious lights\"/>\n<music keywords=\"mysterious, whimsical, soft piano, strings, 19th century\"/>\n</scene>\n<dialogue>\n<narration>\nIn the heart of the old town, where the cobblestone streets whisper tales of the past, a young boy named Eli stumbles upon a shop that seems to have appeared out of nowhere. The sign above the door reads \"The Enchanted Emporium,\" and a faint glow emanates from within, casting eerie shadows on the foggy street.\n</narration>\n<character name=\"Eli\" identifier=\"14 years old, male, brown hair, green eyes, average build\" emotion=\"curious\" clothes=\"jeans, t-shirt\">\nWow, I've never seen this shop before. It looks like something out of a fairy tale.\n</character>\n<narration>\nEli pushes open the creaky door and steps inside. The shop is filled with an array of peculiar items: crystal balls, ancient books, and jars filled with strange powders and liquids. A bell above the door jingles, announcing his arrival.\n</narration>\n<character name=\"Mr. Harrow\" identifier=\"60 years old, male, white hair, piercing blue eyes, tall, thin\" emotion=\"welcoming\" clothes=\"tailored suit, top hat\">\nAh, welcome, young one. I've been expecting you.\n</character>\n<character name=\"Eli\" emotion=\"surprised\">\nExpecting me? I just stumbled upon this place by accident.\n</character>\n<character name=\"Mr. Harrow\" emotion=\"enigmatic\">\nPerhaps, or perhaps not. The universe has a way of guiding us to where we need to be.\n</character>\n<narration>\nEli looks around, his eyes wide with wonder. The air in the shop feels charged, as if magic is a tangible presence.\n</narration>\n<character name=\"Eli\" emotion=\"excited\">\nIs this place really... magical?\n</character>\n<character name=\"Mr. Harrow\" emotion=\"smiling\">\nIndeed, it is. And I sense a spark within you, Eli. A potential for great magic.\n</character>\n<character name=\"Eli\" emotion=\"eager\">\nCan you teach me? I've always dreamed of doing magic!\n</character>\n<character name=\"Mr. Harrow\" emotion=\"serious\">\nLearning magic is no small task. It requires dedication, courage, and a strong heart. Are you prepared for the challenges ahead?\n</character>\n<character name=\"Eli\" emotion=\"determined\">\nI am. I want to learn, no matter what it takes.\n</character>\n<character name=\"Mr. Harrow\" emotion=\"approving\">\nVery well. From this day forth, you shall be my apprentice. Together, we will protect this shop and its secrets from those who seek to misuse them.\n</character>\n<narration>\nAs Eli accepts the offer, the atmosphere in the shop shifts, as if acknowledging the new bond between master and apprentice.\n</narration>\n</dialogue>\n<scene>\n<background keywords=\"magic shop, shelves filled with curiosities, dim lighting, magical aura\"/>\n<music keywords=\"enchanting, mysterious, harp, flute, ethereal\"/>\n</scene>\n<dialogue>\n<narration>\nDays turn into weeks, and Eli begins his training under Mr. Harrow's tutelage. Each day brings new lessons and challenges, from understanding ancient spells to mastering the art of potion-making.\n</narration>\n<character name=\"Eli\" identifier=\"growing confidence, more adept at magic\" emotion=\"focused\" clothes=\"apprentice robe\">\nMr. Harrow, I think I've almost got the hang of this levitation spell.\n</character>\n<character name=\"Mr. Harrow\" emotion=\"encouraging\">\nExcellent, Eli. Remember, the key is concentration and belief in your own abilities.\n</character>\n<narration>\nAs Eli practices, a sudden chill fills the air, and the lights flicker ominously.\n</narration>\n<character name=\"Mr. Harrow\" emotion=\"alert\">\nSomething is amiss. Be on your guard, Eli.\n</character>\n<narration>\nA shadowy figure appears at the window, its eyes glowing red. It seems to be drawn to the magical energies within the shop.\n</narration>\n<character name=\"Eli\" emotion=\"fearful\">\nWhat is that thing?\n</character>\n<character name=\"Mr. Harrow\" emotion=\"resolute\">\nA dark entity, likely drawn by the magic. We must protect the shop.\n</character>\n<character name=\"Eli\" emotion=\"determined\">\nWhat should we do?\n</character>\n<character name=\"Mr. Harrow\" emotion=\"calm\">\nFirst, we fortify the defenses. Then, we prepare to confront it.\n</character>\n<narration>\nTogether, they work quickly, setting up protective wards and gathering magical artifacts. The air crackles with energy as they prepare for the confrontation.\n</narration>\n</dialogue>\n<options>\n<title>What should Eli do next?</title>\n<option>Confront the dark entity directly</option>\n<option>Set a magical trap</option>\n<option>Seek help from other magical beings</option>\n<option>Evacuate the shop and regroup</option>\n</options>\n<action>Set a magical trap</action>\n<!-- Continue with new scene, dialogue, options, and action based on the chosen action -->\n</vnml>\n```", "```vnml\n<vnml lang=\"en\">\n<action>Set a magical trap</action>\n<scene>\n<background keywords=\"magic shop, wards activated, tense atmosphere, magical traps set\"/>\n<music keywords=\"tense, suspenseful, low strings, eerie\"/>\n</scene>\n<dialogue>\n<narration>\nEli and Mr. Harrow work diligently to set a complex magical trap, designed to ensnare the dark entity without causing harm to the shop or themselves. The air is thick with anticipation and the charged energy of their preparations.\n</narration>\n<character name=\"Eli\" identifier=\"focused, determined\" emotion=\"nervous\" clothes=\"apprentice robe\">\nAre you sure this will work, Mr. Harrow?\n</character>\n<character name=\"Mr. Harrow\" emotion=\"confident\">\nTrust in the magic, Eli. It has never failed us before.\n</character>\n<narration>\nAs they finish setting the trap, the shadowy figure outside grows more restless, its red eyes flickering with impatience. It begins to cast dark spells towards the shop, trying to break through the protective wards.\n</narration>\n<character name=\"Eli\" emotion=\"alert\">\nIt's starting to attack the wards!\n</character>\n<character name=\"Mr. Harrow\" emotion=\"resolute\">\nHold steady. The trap will activate once it breaches the wards.\n</character>\n<narration>\nThe wards shimmer and crackle under the assault, but they hold firm. The dark entity, frustrated, intensifies its efforts, and finally, a ward shatters.\n</narration>\n<character name=\"Eli\" emotion=\"fearful\">\nIt's in!\n</character>\n<character name=\"Mr. Harrow\" emotion=\"calm\">\nNow, Eli! Activate the trap!\n</character>\n<narration>\nWith a swift motion, Eli triggers the magical trap. A web of shimmering light envelops the dark entity, binding it tightly. The entity struggles, but the more it fights, the tighter the magical bonds become.\n</narration>\n<character name=\"Eli\" emotion=\"relieved\">\nWe did it! It's trapped!\n</character>\n<character name=\"Mr. Harrow\" emotion=\"satisfied\">\nIndeed, we did. But we must not let our guard down. This entity may have allies.\n</character>\n<narration>\nThey secure the trapped entity, discussing their next steps. The shop, once again, returns to a semblance of peace, though the air still hums with residual magic.\n</narration>\n</dialogue>\n<options>\n<title>What should they do with the trapped entity?</title>\n<option>Interrogate the entity to learn its motives</option>\n<option>Contact the magical council for assistance</option>\n<option>Banish the entity to another realm</option>\n<option>Study the entity to understand its powers</option>\n</options>\n<action>Interrogate the entity to learn its motives</action>\n<!-- Continue with new scene, dialogue, options, and action based on the chosen action -->\n</vnml>\n```"]

def stream_vnml_parser(vnml: Iterator[str]) -> Iterator[str]:
    buffer = ''
    for chr in vnml:
        ...

def continue_vnml(vnml: str, ) -> Iterator[str]:
    if vnml == '':
        yield "<action>Start!</action>"
    yield "<scene>\n<background keywords=\"old town, cobblestone streets, twilight, foggy, mysterious lights\"/>\n<music keywords=\"mysterious, whimsical, soft piano, strings, 19th century\"/>\n</scene>"
    yield "<narration>\nIn the heart of the old town, where the cobblestone streets whisper tales of the past, a young boy named Eli stumbles upon a shop that seems to have appeared out of nowhere. The sign above the door reads \"The Enchanted Emporium,\" and a faint glow emanates from within, casting eerie shadows on the foggy street.\n</narration>"
    yield "<character name=\"Eli\" identifier=\"14 years old, male, brown hair, green eyes, average build\" emotion=\"curious\" clothes=\"jeans, t-shirt\">\nWow, I've never seen this shop before. It looks like something out of a fairy tale.\n</character>"
    yield '''<narration>
Eli pushes open the creaky door and steps inside. The shop is filled with an array of peculiar items: crystal balls, ancient books, and jars filled with strange powders and liquids. A bell above the door jingles, announcing his arrival.
</narration>'''
    yield '''<character name="Mr. Harrow" identifier="60 years old, male, white hair, piercing blue eyes, tall, thin" emotion="welcoming" clothes="tailored suit, top hat">
Ah, welcome, young one. I've been expecting you.
</character>'''
    # yield


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
