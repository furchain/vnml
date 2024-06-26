"""The dashboard page."""

import reflex as rx

from vnml.templates import template
from vnml.components.playground import playground
@template(route="/play", title="Play")
def play() -> rx.Component:
    """The dashboard page.

    Returns:
        The UI for the dashboard page.
    """
    return playground()
    # return rx.image(
    #     DisplayState.background_url,
    #     position="absolute",
    #     top="0",
    #     left="0",
    #     # width="100%",
    #     # height="100%",
    #     object_fit="cover",  # Ensures the image covers the entire background
    #     # z_index="-1",
    # )
