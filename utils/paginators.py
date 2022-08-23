"""MIT License.

Copyright (c) 2022 Faholan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import typing as t

import discord
from discord import ui
from discord.ext import commands


class WrappedPaginator(commands.Paginator):  # type: ignore
    """A paginator with automatic wrapping of lines."""

    def __init__(
        self,
        *args: t.Any,
        wrap_on=("\n", " "),
        include_wrapped: bool = True,
        force_wrap: bool = False,
        **kwargs: t.Any,
    ) -> None:
        """Initialize the paginator."""
        super().__init__(*args, **kwargs)
        self.wrap_on = wrap_on
        self.include_wrapped = include_wrapped
        self.force_wrap = force_wrap

    def add_line(self, line: str = " ", *, empty: bool = False) -> None:
        """Add a line to the paginator."""
        true_max_size = self.max_size - self._prefix_len - self._suffix_len - 2

        original_length = len(line)

        while len(line) > true_max_size:
            search_string = line[: true_max_size - 1]
            wrapped = False

            for delimiter in self.wrap_on:
                position = search_string.rfind(delimiter)

                if position > 0:
                    super().add_line(line[:position], empty=empty)
                    wrapped = True

                    if self.include_wrapped:
                        line = line[position:]
                    else:
                        line = line[position + len(delimiter) :]

                    break

            if not wrapped:
                if self.force_wrap:
                    super().add_line(line[: true_max_size - 1])
                else:
                    raise ValueError(
                        f"Line of length {original_length} "
                        f"had sequence of {len(line)} characters"
                        f" (max is {true_max_size}) that "
                        "WrappedPaginator could not wrap with"
                        f" delimiters: {self.wrap_on}"
                    )

        super().add_line(line, empty=empty)


class TextPaginator:
    """A view-based paginator for basic text."""

    max_page_size = 2000

    def __init__(
        self,
        *args: t.Any,
        max_size: int = 1975,
        **kwargs: t.Any,
    ) -> None:
        """Initialize the interface."""
        self._display_page = 0

        self.paginator = WrappedPaginator(*args, max_size=max_size, **kwargs)

        self.interaction: discord.Interaction = None  # type: ignore

        self.task: t.Optional[asyncio.Task] = None
        self.send_lock: asyncio.Event = asyncio.Event()

        self.sent_view = False

        self.timeout = kwargs.pop("timeout", 7200)

        if self.page_size > self.max_page_size:
            raise ValueError(
                f"Paginator passed has too large of a page size for this interface. "
                f"({self.page_size} > {self.max_page_size})"
            )

    @property
    def pages(self) -> t.List[str]:
        """Get the paginator's pages without prematurely closing the active page."""
        # pylint: disable=protected-access
        paginator_pages = list(self.paginator._pages)
        if len(self.paginator._current_page) > 1:
            paginator_pages.append(
                "\n".join(self.paginator._current_page)
                + "\n"
                + (self.paginator.suffix or "")
            )
        # pylint: enable=protected-access

        return paginator_pages

    @property
    def page_count(self) -> int:
        """Ge the page count of the internal paginator."""
        return len(self.pages)

    @property
    def display_page(self) -> int:
        """Get the current page the paginator interface is on."""
        self._display_page = max(
            0,
            min(self.page_count - 1, self._display_page),
        )
        return self._display_page

    @display_page.setter
    def display_page(self, value: int) -> None:
        """Set the current page the paginator is on."""
        self._display_page = max(0, min(self.page_count - 1, value))

    @property
    def page_size(self) -> int:
        """Get the maximum size of a page."""
        page_count = self.page_count
        return self.paginator.max_size + len(f"\n Page {page_count}/{page_count}")

    @property
    def page_content(self) -> str:
        """Get the content of the current page."""
        display_page = self.display_page
        page_num = f"\nPage {display_page + 1}/{self.page_count}"
        return self.pages[display_page] + page_num

    async def add_line(self, *args: t.Any, **kwargs: t.Any) -> None:
        """Add a line while remaining locked to the last page."""
        display_page = self.display_page
        page_count = self.page_count

        self.paginator.add_line(*args, **kwargs)

        new_page_count = self.page_count

        if display_page + 1 == page_count:
            self._display_page = new_page_count - 1

        # Guarantee a page update
        self.send_lock.set()

    async def send_to(self, interaction: discord.Interaction) -> None:
        """Send a message and automatically update it."""
        if self.interaction is not None:
            raise RuntimeError("Paginator has already been sent.")

        self.interaction = interaction

        if self.page_count > 1:
            await interaction.response.send_message(
                self.page_content, view=TextPaginatorView(self)
            )
            self.sent_view = True
        else:
            await interaction.response.send_message(self.page_content)

        self.task = asyncio.create_task(self.wait_loop())

    @property
    def closed(self) -> bool:
        """Check if this interface is closed."""
        if not self.task:
            return False
        return self.task.done()

    async def send_lock_delayed(self) -> None:
        """Wait until 1 second after the send lock is released."""
        await self.send_lock.wait()
        self.send_lock.clear()
        await asyncio.sleep(1)

    async def wait_loop(self) -> None:
        """Wait on a loop for an event."""
        try:
            last_content = None

            while not self.interaction.client.is_closed():
                await asyncio.wait_for(self.send_lock_delayed(), timeout=self.timeout)

                if self.page_content != last_content:
                    if not self.sent_view and self.page_count > 1:
                        await self.interaction.edit_original_response(
                            content=self.page_content,
                            view=TextPaginatorView(self),
                        )
                        self.sent_view = True
                    else:
                        try:
                            await self.interaction.edit_original_response(
                                content=self.page_content,
                            )
                        except discord.NotFound:
                            return  # No more message :(
                    last_content = self.page_content

        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass


class TextPaginatorView(ui.View):
    """View to navigate the paginator."""

    def __init__(
        self,
        paginator: TextPaginator,
    ) -> None:
        """Initialize the view."""
        self.paginator = paginator
        super().__init__(timeout=7200)

    @ui.button(emoji="\U000023ee\U0000fe0f")
    async def first_page(self, interaction: discord.Interaction, _: t.Any) -> None:
        """Go to the first page."""
        await interaction.response.defer()
        self.paginator.display_page = 0
        self.paginator.send_lock.set()

    @ui.button(emoji="\U000023ea", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, _: t.Any) -> None:
        """Go back one page."""
        await interaction.response.defer()
        self.paginator.display_page -= 1
        self.paginator.send_lock.set()

    @ui.button(emoji="\U000023e9", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, _: t.Any) -> None:
        """Go forward one page."""
        await interaction.response.defer()
        self.paginator.display_page += 1
        self.paginator.send_lock.set()

    @ui.button(emoji="\U000023ed\U0000fe0f")
    async def last_page(self, interaction: discord.Interaction, _: t.Any) -> None:
        """Go to the last page."""
        await interaction.response.defer()
        self.paginator.display_page = self.paginator.page_count - 1
        self.paginator.send_lock.set()
