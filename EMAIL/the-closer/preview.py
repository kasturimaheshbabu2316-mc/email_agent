# preview.py
"""Preview and user confirmation utilities for The Closer.

Provides a rich‑styled display of the generated email and a prompt
that returns the user's decision (send, draft, or skip).  The functions are
used by ``main.py`` but are isolated here for easier testing and future
extension (e.g., a GUI front‑end).
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from typing import Literal

ConsoleInstance = Console()

def preview_email(subject: str, body: str) -> None:
    """Render the email subject and body using ``rich``.

    The subject is displayed in bold cyan, and the body is wrapped inside a
    ``Panel`` to improve readability in a terminal.
    """
    ConsoleInstance.print(f"[bold cyan]Subject:[/bold cyan] {subject}\n")
    ConsoleInstance.print(Panel(body, title="Email Body", border_style="green"))

def prompt_confirmation() -> Literal["send", "draft", "skip"]:
    """Ask the user what to do with the previewed email.

    Returns one of ``"send"``, ``"draft"`` or ``"skip"``. The default is
    ``"skip"`` to keep the demo safe.
    """
    choice = Prompt.ask(
        "Send, Draft, Skip?",
        choices=["send", "draft", "skip"],
        default="skip",
    )
    return choice  # type: ignore[return-value]
