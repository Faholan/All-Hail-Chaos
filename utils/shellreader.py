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
import re
import subprocess  # nosec
import time
import typing as t


# Adapted from jishaku
def background_reader(
    stream: t.Any,
    loop: asyncio.AbstractEventLoop,
    callback: t.Callable[[bytes], t.Coroutine[t.Any, t.Any, None]],
) -> None:
    """Read a stream and forward each line to an async callback."""
    for line in iter(stream.readline, b""):
        loop.call_soon_threadsafe(loop.create_task, callback(line))


class ShellReader:
    """Passively read from a shell and buffer results for read."""

    def __init__(
        self,
        command: str,
        timeout: int = 120,
        loop: t.Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        """Initialize the shell reader."""
        sequence = ["/bin/bash", "-c", command]

        self.close_code = None

        self.process = subprocess.Popen(  # nosec  # pylint: disable=consider-using-with
            sequence,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.loop = loop or asyncio.get_event_loop()
        self.timeout = timeout

        self.stdout_task = self.make_reader_task(
            self.process.stdout,
            self.stdout_handler,
        )

        self.stderr_task = self.make_reader_task(
            self.process.stderr,
            self.stderr_handler,
        )

        self.queue: asyncio.Queue[str] = asyncio.Queue(maxsize=250)

        self.ps1 = "$"  # Input
        self.highlight = "sh"  # Discord syntax highlighting

    @property
    def closed(self) -> bool:
        """Check if both tasks are done."""
        return self.stdout_task.done() and self.stderr_task.done()

    async def executor_wrapper(
        self,
        func: t.Callable[
            [
                t.Any,
                asyncio.AbstractEventLoop,
                t.Callable[[bytes], t.Coroutine[t.Any, t.Any, None]],
            ],
            None,
        ],
        stream: t.Any,
        callback: t.Callable[[bytes], t.Coroutine[t.Any, t.Any, None]],
    ) -> None:
        """Execute a function in the executor."""
        await self.loop.run_in_executor(None, func, stream, self.loop, callback)

    def make_reader_task(
        self,
        stream: t.Any,
        callback: t.Callable[[bytes], t.Coroutine[t.Any, t.Any, None]],
    ) -> asyncio.Task[None]:
        """Create a reader executor task."""
        return self.loop.create_task(
            self.executor_wrapper(
                background_reader,
                stream,
                callback,
            )
        )

    @staticmethod
    def clean_bytes(line: bytes) -> str:
        """Clean and decode a byte sequence."""
        text = line.decode("utf-8").replace("\r", "").strip("\n")
        return re.sub(r"\x1b[^m]*m", "", text).replace("``", "`\u200b`").strip("\n")

    async def stdout_handler(self, line: bytes) -> None:
        """Handle stdout lines."""
        await self.queue.put(self.clean_bytes(line))

    async def stderr_handler(self, line: bytes) -> None:
        """Handle stderr lines."""
        await self.queue.put("[stderr] " + self.clean_bytes(line))

    def __enter__(self) -> "ShellReader":
        """Enter the context manager."""
        return self

    def __exit__(self, *_: t.Any) -> None:
        """Exit the context manager and cleanup."""
        self.process.kill()
        self.process.terminate()
        self.close_code = self.process.wait(timeout=0.5)

    def __aiter__(self) -> "ShellReader":
        """Return the iterator."""
        return self

    async def __anext__(self) -> str:
        """Read the next line from the queue."""
        last_output = time.perf_counter()

        while not self.closed or not self.queue.empty():
            try:
                item = await asyncio.wait_for(self.queue.get(), timeout=1)
            except asyncio.TimeoutError as exception:
                if time.perf_counter() - last_output >= self.timeout:
                    raise exception
            else:
                last_output = time.perf_counter()
                return item

        raise StopAsyncIteration()
