"""
Implements a command relate to movie
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import Literal, Optional

import numpy as np
from discord import app_commands, Interaction, Embed, NotFound, HTTPException
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


class Movie(app_commands.Group):
    """
    Commands related to Movie
    """

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @app_commands.command()
    @app_commands.describe(name="Name of the movie to play")
    @app_commands.describe(original_speed="Play the movie at the original speed by skipping some frames. "
                                          "Default value: True")
    @app_commands.describe(fps="Number of frames to display per second. Range from 1 to 4 (inclusive). "
                               "Default value: 4")
    async def play(self, interaction: Interaction,
                   name: Literal["bad_apple"],
                   original_speed: Optional[bool] = True,
                   fps: Optional[app_commands.Range[int, 1, 4]] = 4):
        """
        Play the movie
        """
        is_on_mobile = interaction.guild.get_member(interaction.user.id).is_on_mobile()
        embed = Embed(color=templates.color, title=name.replace("_", " ").title())
        await interaction.response.send_message(embed=embed)

        movie = self._resize(VideoFileClip(f"assets/{name}.mp4", audio=False), is_on_mobile)

        text_frames = Queue(maxsize=60)

        def _create_frames():
            for i, frame in enumerate(movie.iter_frames()):
                if original_speed and i % (movie.fps // fps) != 0:
                    continue

                text_frames.put(Movie._create_text(frame, is_on_mobile), timeout=60)

            text_frames.put(None)
            movie.close()

        async def _display():
            current_frame_num = 1
            message = await interaction.original_response()
            while not creating.done():
                await self._delay_cycle(fps)

                try:
                    text_frame = text_frames.get(timeout=5)
                    if text_frame is None:
                        return

                    embed.description = f"```{text_frame}```"
                except Exception as ex:
                    movie.close()
                    executor.shutdown(wait=False, cancel_futures=True)
                    raise ex

                embed.set_footer(text=f"Frame: {current_frame_num}")

                try:
                    await message.edit(embed=embed)
                except NotFound:  # message deleted
                    movie.close()
                    executor.shutdown(wait=False, cancel_futures=True)
                    return
                except HTTPException as ex:
                    if ex.code == 50027:
                        message = await message.channel.fetch_message(message.id)
                        await message.edit(embed=embed)
                    else:
                        raise ex

                if original_speed:
                    current_frame_num += round(movie.fps) // fps
                else:
                    current_frame_num += 1

        executor = ThreadPoolExecutor(max_workers=1)
        creating = executor.submit(_create_frames)

        await _display()

    @staticmethod
    def _resize(video: VideoFileClip, is_on_mobile: bool) -> VideoFileClip:
        if abs(video.aspect_ratio - 4 / 3) < 0.0005:
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
    async def _delay_cycle(fps):
        clock = time.perf_counter() * fps  # measure time in 1/fps seconds
        sleep = int(clock) + 1 - clock  # time until the next 1/fps
        await asyncio.sleep(sleep / fps + 1 / fps)

    @staticmethod
    def _create_text(frame: ndarray, is_on_mobile: bool) -> str:
        grayscale_frame = np.dot(frame, (0.2989, 0.5870, 0.1140))
        grayscale_frame = np.floor(grayscale_frame).astype(int)

        char_length = len(CHARS) if is_on_mobile else len(MOBILE_CHARS)
        normalized_frame: ndarray = grayscale_frame * char_length / PIXEL_VALUE_RANGE
        normalized_frame = np.floor(normalized_frame).astype(int)

        text = ""
        for arr in normalized_frame:
            for char_idx in arr:
                text += (MOBILE_CHARS[char_idx] if is_on_mobile else CHARS[char_idx]) * 2
            text += "\n"

        return text.removesuffix("\n")
