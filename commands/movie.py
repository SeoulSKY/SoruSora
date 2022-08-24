"""
Implements a command relate to movie
"""
import itertools
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from queue import Queue
from typing import Literal, Optional

import numpy as np
from discord import app_commands, Interaction, Embed, NotFound, HTTPException, Message
from discord.ext import tasks
from discord.ext.commands import Bot
from moviepy.editor import VideoFileClip
from numpy.core.records import ndarray

import templates

CHARS = " ░▒▓█"
"""
Characters to use for movies
"""

MOBILE_CHARS = "┈░▒▓█"
"""
Characters to use for movies on mobile devices
"""

MOVIE_RESOLUTION = (28, 21)
"""
(width, height)
"""

MOVIE_RESOLUTION_16_9 = (28, 17)
"""
(width, height)
"""

MOBILE_MOVIE_RESOLUTION = (11, 8)
"""
(width, height)
"""

MOBILE_MOVIE_RESOLUTION_16_9 = (11, 6)
"""
(width, height)
"""

# DO NOT MODIFY
PIXEL_VALUE_RANGE = 255
"""
Maximum value of RGB for each pixel
"""


class Screen:
    """
    Screen to display movie on Discord
    """

    def __init__(self, message: Message, embed: Embed):
        self._message = message
        self._embed = embed

    @property
    def message(self):
        """
        Get the message
        """
        return self._message

    @message.setter
    def message(self, message: Message):
        self._message = message

    @property
    def embed(self):
        """
        Get the embed
        """
        return self._embed

    @embed.setter
    def embed(self, embed: Embed):
        self._embed = embed

    async def update(self):
        """
        Update the screen on Discord
        """
        try:
            await self.message.edit(embed=self.embed)
        except HTTPException as ex:
            if ex.code == 50027:
                self.message = await self.message.channel.fetch_message(self.message.id)
                await self.message.edit(embed=self.embed)
            else:
                raise ex


class Movie(app_commands.Group):
    """
    Commands related to Movie
    """

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @app_commands.command()
    @app_commands.describe(name="Name of the movie to play")
    @app_commands.describe(fps="Number of frames to display per second. Range from 1 to 2 (inclusive). "
                               "Default value: 2")
    @app_commands.describe(original_speed="Play the movie at the original speed by skipping some frames. "
                                          "Default value: True")
    async def play(self, interaction: Interaction,
                   name: Literal["bad_apple", "ultra_b+k"],
                   fps: Optional[Literal[1, 2]] = 2,
                   original_speed: Optional[bool] = True):
        """
        Play the movie
        """
        is_on_mobile = interaction.guild.get_member(interaction.user.id).is_on_mobile()
        embed = Embed(color=templates.color, title=name.replace("_", " ").title())
        await interaction.response.send_message(embed=embed)

        movie = self._resize(VideoFileClip(f"assets/{name}.mp4", audio=False), is_on_mobile)

        text_frames = Queue(maxsize=movie.fps * fps)
        counter = itertools.count(start=1, step=round(movie.fps) // fps if original_speed else 1)
        screen = Screen(await interaction.original_response(), embed)

        def _create_frames():
            try:
                for i, frame in enumerate(movie.iter_frames()):
                    # ignore some last frames to prevent reading an empty frame
                    if i == movie.reader.nframes - 2:
                        break
                    if original_speed and i % (movie.fps // fps) != 0:
                        continue

                    text_frames.put(Movie._create_text(frame, is_on_mobile),
                                    timeout=timedelta(minutes=3).total_seconds())
            finally:
                text_frames.put(None)

        @tasks.loop(seconds=1 / fps)
        async def _display():
            embed.set_footer(text=f"Frame: {next(counter)}")
            try:
                text_frame = text_frames.get(timeout=5)
                if text_frame is None:
                    text_frames.put(None)
                    _display.cancel()
                    return

                embed.description = f"```{text_frame}```"

                await screen.update()
            except NotFound:  # message deleted
                _display.cancel()
                return

        @_display.after_loop
        async def _clean_up():
            text_frames.task_done()
            movie.close()
            executor.shutdown(wait=False, cancel_futures=True)

        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(_create_frames)

        _display.start()

    @staticmethod
    def _resize(video: VideoFileClip, is_on_mobile: bool) -> VideoFileClip:
        if abs(video.aspect_ratio - 4 / 3) < 0.05:
            if is_on_mobile:
                new_resolution = MOBILE_MOVIE_RESOLUTION
            else:
                new_resolution = MOVIE_RESOLUTION
        else:
            if is_on_mobile:
                new_resolution = MOBILE_MOVIE_RESOLUTION_16_9
            else:
                new_resolution = MOVIE_RESOLUTION_16_9

        # noinspection PyUnresolvedReferences
        return video.resize(new_resolution)  # pylint: disable=no-member

    @staticmethod
    def _create_text(frame: ndarray, is_on_mobile: bool) -> str:
        grayscale_frame = np.dot(frame, (0.2989, 0.5870, 0.1140))
        grayscale_frame = np.floor(grayscale_frame).astype(int)

        char_length = len(MOBILE_CHARS) if is_on_mobile else len(CHARS)
        normalized_frame: ndarray = grayscale_frame * char_length / PIXEL_VALUE_RANGE
        normalized_frame = np.floor(normalized_frame).astype(int)

        text = ""
        for arr in normalized_frame:
            for char_idx in arr:
                text += (MOBILE_CHARS[char_idx] if is_on_mobile else CHARS[char_idx]) * 2
            text += "\n"

        return text.removesuffix("\n")
