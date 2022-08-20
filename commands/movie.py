"""
Implements a command relate to movie
"""
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import Literal, Optional

import imageio.v2
import numpy as np
from PIL import Image
from discord import app_commands, Interaction, Embed, NotFound
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

MOBILE_MOVIE_RESOLUTION = (11, 8)
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
    @app_commands.describe(original_speed="Play the movie at the original speed by skipping some frames")
    @app_commands.describe(fps="Number of frames to display per second")
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
        message = await interaction.original_response()

        file_name = f"assets/{name}.mp4"
        with VideoFileClip(file_name) as video_clip:
            pass

        text_frames = Queue(maxsize=60)

        def _create_frames():
            movie = imageio.imiter(file_name, format_hint=".mp4")

            for i, frame in enumerate(movie):
                if original_speed and i % (video_clip.fps // fps) != 0:
                    continue

                movie_resolution = MOBILE_MOVIE_RESOLUTION if is_on_mobile else MOVIE_RESOLUTION
                # noinspection PyTypeChecker
                resized_frame = np.asarray(Image.fromarray(frame).resize(movie_resolution))

                text_frames.put(Movie._create_text(resized_frame, is_on_mobile), timeout=300)

            text_frames.task_done()

        executor = ThreadPoolExecutor(max_workers=1)

        current_frame_num = 1
        while not executor.submit(_create_frames).done():
            await self._delay_cycle(fps)

            try:
                embed.description = f"```{text_frames.get(timeout=5)}```"
            except Exception as ex:
                executor.shutdown(wait=False, cancel_futures=True)
                raise ex

            embed.set_footer(text=f"Frame: {current_frame_num}")

            try:
                await message.edit(embed=embed)
            except NotFound:  # message deleted
                executor.shutdown(wait=False, cancel_futures=True)
                return

            if original_speed:
                current_frame_num += int(video_clip.fps) // fps
            else:
                current_frame_num += 1

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
