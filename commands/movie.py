"""
Implements a command relate to movie
"""

import itertools
import json
import os
import threading
from typing import Literal, Optional

import numpy as np
from discord import app_commands, Interaction, Embed, HTTPException, Message, NotFound
from discord.ext import tasks
from discord.ext.commands import Bot
from moviepy.editor import VideoFileClip
from moviepy.video.fx import resize as resizer
from tqdm import tqdm

from utils import templates, constants

DESKTOP_CACHE_PATH = os.path.join(constants.CACHE_DIR, "movie", "desktop")
"""
Path to the cache directory for desktop
"""

MOBILE_CACHE_PATH = os.path.join(constants.CACHE_DIR, "movie", "mobile")
"""
Path to the cache directory for mobile
"""

FPS = 30
"""
Frames per second
"""

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

PIXEL_VALUE_RANGE = 255
"""
Maximum value of RGB for each pixel
"""


class Movie(app_commands.Group):
    """
    Commands related to Movie
    """

    _cache: dict[str, list[str]] = {}
    _num_playing = 0
    _lock = threading.Lock()

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

        if not os.path.exists(DESKTOP_CACHE_PATH) or not os.path.exists(MOBILE_CACHE_PATH):
            self._cache_movies()

    @staticmethod
    def _cache_movies():
        os.makedirs(constants.CACHE_DIR, exist_ok=True)

        movie_names = [file for file in os.listdir(constants.ASSETS_DIR) if file.endswith(".mp4")]
        for is_on_mobile in (True, False):
            os.makedirs(MOBILE_CACHE_PATH if is_on_mobile else DESKTOP_CACHE_PATH, exist_ok=True)

            for movie_name in movie_names:
                movie = Movie._resize(VideoFileClip(os.path.join(constants.ASSETS_DIR, movie_name),
                                                    audio=False), is_on_mobile)

                buffer = []
                with open(Movie._get_cache_path(movie_name.removesuffix(".mp4"), is_on_mobile), "w") as f:
                    for frame in tqdm(movie.iter_frames(), desc=f"Caching {movie_name} for "
                                                                f"{'mobile' if is_on_mobile else 'desktop'}",
                                      total=movie.reader.nframes, unit="frame"):
                        buffer.append(Movie._create_text(frame, is_on_mobile))

                    f.write(json.dumps(buffer))

    @staticmethod
    def _get_cache_path(name: str, is_on_mobile: bool) -> str:
        return os.path.join(MOBILE_CACHE_PATH if is_on_mobile else DESKTOP_CACHE_PATH, name + ".json")

    @staticmethod
    async def get_frames(name: str, is_on_mobile: bool) -> list[str]:
        path = Movie._get_cache_path(name, is_on_mobile)
        if path not in Movie._cache:
            with open(path, "r") as f:
                Movie._cache[path] = json.load(f)

        return Movie._cache[path]

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
        embed = Embed(color=templates.color, title=name.replace("_", " ").title(),
                      description="Loading...")
        await interaction.response.send_message(embed=embed)

        message: Message = await interaction.original_response()
        counter = itertools.count(start=0, step=FPS // fps if original_speed else 1)
        with Movie._lock:
            Movie._num_playing += 1
            frames = await Movie.get_frames(name, is_on_mobile)

        @tasks.loop(seconds=1 / fps)
        async def display():
            """
            Play the movie
            """

            index = next(counter)
            if index >= len(frames):
                display.cancel()
                return

            embed.set_footer(text=f"Frame: {index + 1}")
            embed.description = f"```{frames[index]}```"

            nonlocal message

            try:
                await message.edit(embed=embed)
            except NotFound:  # Message is deleted
                display.cancel()
            except HTTPException as ex:
                if ex.code == 50027:
                    message = await message.channel.fetch_message(message.id)
                    await message.edit(embed=embed)
                else:
                    raise ex

        @display.after_loop
        async def clean_up():
            """
            Clean up after the movie is finished playing
            """

            with Movie._lock:
                Movie._num_playing = max(0, Movie._num_playing - 1)

                if Movie._num_playing <= 0:
                    Movie._cache.clear()

        display.start()

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

        return resizer.resize(video, new_resolution)

    @staticmethod
    def _create_text(frame: np.ndarray, is_on_mobile: bool) -> str:
        grayscale_frame = np.dot(frame, (0.2989, 0.5870, 0.1140))
        grayscale_frame: np.ndarray = np.floor(grayscale_frame).astype(int)

        char_length = len(MOBILE_CHARS) if is_on_mobile else len(CHARS)
        normalized_frame: np.ndarray = grayscale_frame * char_length / PIXEL_VALUE_RANGE
        normalized_frame = np.floor(normalized_frame).astype(int)

        text = ""
        for vector in normalized_frame:
            for brightness in vector:
                text += (MOBILE_CHARS[brightness] if is_on_mobile else CHARS[brightness]) * 2
            text += "\n"

        return text.removesuffix("\n")
