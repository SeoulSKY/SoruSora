"""
Implements a commands relate to movie
"""

import itertools
import json
import os
import threading

import numpy as np
from discord import app_commands, Interaction, Embed, HTTPException, Message, NotFound
from discord.app_commands import Choice
from discord.ext import tasks
from discord.ext.commands import Bot
import cv2
from tqdm import tqdm

from utils import templates, constants
from utils.constants import ErrorCode
from utils.translator import Localization, DEFAULT_LANGUAGE

DESKTOP_CACHE_PATH = constants.CACHE_DIR / "movie" / "desktop"
"""
Path to the cache directory for desktop
"""

MOBILE_CACHE_PATH = constants.CACHE_DIR / "movie" / "mobile"
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

default_loc = Localization(DEFAULT_LANGUAGE, [os.path.join("commands", "movie.ftl")])


class Movie(app_commands.Group):
    """
    Commands related to Movie
    """
    # pylint: disable=no-member

    FPS_MIN = 1
    FPS_MAX = 2
    FPS_DEFAULT = 2
    ORIGINAL_SPEED_DEFAULT = True

    _cache: dict[str, list[str]] = {}
    _num_playing = 0
    _lock = threading.Lock()

    def __init__(self, bot: Bot):
        super().__init__(name=default_loc.format_value("movie-name"),
                         description=default_loc.format_value("movie-description"))
        self.bot = bot

        if not os.path.exists(DESKTOP_CACHE_PATH) or not os.path.exists(MOBILE_CACHE_PATH):
            self._cache_movies()

    @classmethod
    def _cache_movies(cls):
        os.makedirs(constants.CACHE_DIR, exist_ok=True)

        movie_names = [file for file in os.listdir(constants.ASSETS_DIR) if file.endswith(".mp4")]
        for is_mobile in (True, False):
            os.makedirs(MOBILE_CACHE_PATH if is_mobile else DESKTOP_CACHE_PATH, exist_ok=True)

            for movie_name in movie_names:
                movie = cv2.VideoCapture(str(constants.ASSETS_DIR / movie_name))

                _, frame = movie.read()
                if frame is None:
                    raise ValueError(f"Movie '{movie_name}' has no frames")

                height, width, _ = frame.shape
                aspect_ratio = width / height

                if abs(aspect_ratio - 4 / 3) < 0.05:
                    if is_mobile:
                        new_resolution = MOBILE_MOVIE_RESOLUTION
                    else:
                        new_resolution = MOVIE_RESOLUTION
                else:
                    if is_mobile:
                        new_resolution = MOBILE_MOVIE_RESOLUTION_16_9
                    else:
                        new_resolution = MOVIE_RESOLUTION_16_9

                qbar = tqdm(desc=f"Caching {movie_name} for {'mobile' if is_mobile else 'desktop'}",
                            total=int(movie.get(cv2.CAP_PROP_FRAME_COUNT)), unit="frame")
                buffer = []
                while frame is not None:
                    frame = cv2.resize(frame, new_resolution)
                    buffer.append(cls._create_text(frame, is_mobile))

                    _, frame = movie.read()
                    qbar.update()

                with (open(cls._get_cache_path(movie_name.removesuffix(".mp4"), is_mobile), "w", encoding="utf-8")
                      as file):
                    file.write(json.dumps(buffer))

                qbar.close()
                movie.release()

    @staticmethod
    def _get_cache_path(name: str, is_on_mobile: bool) -> str:
        return os.path.join(MOBILE_CACHE_PATH if is_on_mobile else DESKTOP_CACHE_PATH, name + ".json")

    @staticmethod
    async def get_frames(name: str, is_on_mobile: bool) -> list[str]:
        """
        Get the frames of the movie
        """

        path = Movie._get_cache_path(name, is_on_mobile)
        if path not in Movie._cache:
            with open(path, "r", encoding="utf-8") as file:
                Movie._cache[path] = json.load(file)

        return Movie._cache[path]

    @app_commands.command(name=default_loc.format_value("play-name"),
                          description=default_loc.format_value("play-description"))
    @app_commands.describe(title=default_loc.format_value("play-title-description"))
    @app_commands.describe(fps=default_loc.format_value("play-fps-description", {
        "play-fps-description-min": FPS_MIN,
        "play-fps-description-max": FPS_MAX,
        "play-fps-description-default": FPS_DEFAULT
    }))
    @app_commands.describe(original_speed=default_loc.format_value("play-original-speed-description", {
        "play-original-speed-description-default": str(ORIGINAL_SPEED_DEFAULT)
    }))
    @app_commands.choices(title=[
        Choice(name="Bad Apple!!", value="bad_apple"),
        Choice(name="ULTRA B+K", value="ultra_bk")
    ])
    @app_commands.choices(fps=[Choice(name=str(i), value=i) for i in range(FPS_MIN, FPS_MAX + 1)])
    async def play(self, interaction: Interaction,
                   title: Choice[str],
                   fps: int = FPS_DEFAULT,
                   original_speed: bool = ORIGINAL_SPEED_DEFAULT):
        """
        Play a movie
        """
        is_on_mobile = interaction.guild.get_member(interaction.user.id).is_on_mobile()
        embed = Embed(color=templates.color, title=title.name, description="Loading...")
        await interaction.response.send_message(embed=embed)

        message: Message = await interaction.original_response()
        counter = itertools.count(start=0, step=FPS // fps if original_speed else 1)
        with Movie._lock:
            Movie._num_playing += 1
            frames = await Movie.get_frames(title.value, is_on_mobile)

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
                if ex.code == ErrorCode.MESSAGE_EXPIRED:
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
    def _create_text(frame: np.ndarray, is_mobile: bool) -> str:
        grayscale_frame = np.dot(frame, (0.2989, 0.5870, 0.1140))
        grayscale_frame: np.ndarray = np.floor(grayscale_frame).astype(int)

        char_length = len(MOBILE_CHARS) if is_mobile else len(CHARS)
        normalized_frame: np.ndarray = grayscale_frame * char_length / PIXEL_VALUE_RANGE
        normalized_frame = np.floor(normalized_frame).astype(int)

        text = ""
        for vector in normalized_frame:
            for brightness in vector:
                text += (MOBILE_CHARS[brightness] if is_mobile else CHARS[brightness]) * 2
            text += "\n"

        return text.removesuffix("\n")

    play.extras["play-fps-description-min"] = FPS_MIN
    play.extras["play-fps-description-max"] = FPS_MAX
    play.extras["play-fps-description-default"] = FPS_DEFAULT
    play.extras["play-original-speed-description-default"] = str(ORIGINAL_SPEED_DEFAULT)
