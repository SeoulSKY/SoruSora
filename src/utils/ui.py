"""Provides list of ui elements.

classes:
    Confirm
    LanguageSelectView
    CommandSelect
"""

from collections.abc import Coroutine, Iterable
from pathlib import Path
from typing import Any, Never, Self

from discord import (
    ButtonStyle,
    ChannelType,
    HTTPException,
    Interaction,
    Locale,
    SelectOption,
)
from discord.app_commands import Command, Group
from discord.ui import Button, Select, View, button
from discord.ui import ChannelSelect as BaseChannelSelect

from utils import defer_response
from utils.constants import ErrorCode, Limit
from utils.templates import info, success
from utils.translator import DEFAULT_LANGUAGE, Language, Localization, get_translator

resources = [Path("utils") / "ui.ftl"]

NOT_INITIALIZED_MESSAGE = "Not initialized. Call init() first"


class SubmitButton(Button):
    """Button to submit the form."""

    def __init__(self, locale: Locale, style: ButtonStyle = ButtonStyle.green) -> None:
        """Create a submit button
        :param style: Style of the button.
        """
        self.loc = Localization(locale, resources)
        self._style = style

        super().__init__(label=NOT_INITIALIZED_MESSAGE)

    async def init(self) -> Self:
        """Initialize the button."""
        super().__init__(
            label=await self.loc.format_value_or_translate("submit"), style=self._style
        )
        return self


class Confirm(View):
    """Buttons for confirmation."""

    def __init__(
        self,
        confirmed_message: str,
        cancelled_message: str,
        locale: Locale = DEFAULT_LANGUAGE,
    ) -> None:
        """View to get a confirmation from a user. When the confirm button is pressed,
        set the is_confirmed to `True` and stop the View from listening to more input.
        :param confirmed_message: A message to send when the user confirmed
        :param cancelled_message: A message to send when the user cancelled.
        """
        super().__init__()

        self._confirmed_message = success(confirmed_message)
        self._cancelled_message = info(cancelled_message)

        self._locale = locale

        self.confirm.label = NOT_INITIALIZED_MESSAGE
        self.cancel.label = NOT_INITIALIZED_MESSAGE

        self.is_confirmed = None
        """
        None: The user didn't respond\n
        True: The user confirmed\n
        False: The user cancelled
        """

    async def init(self) -> "Confirm":
        """Initialize the view."""
        loc = Localization(self._locale, resources)

        self.confirm.label = await loc.format_value_or_translate("confirm")
        self.cancel.label = await loc.format_value_or_translate("cancel")

        return self

    @button(style=ButtonStyle.green)
    async def confirm(self, interaction: Interaction, _: Button) -> None:
        """Confirm when pressed."""
        send = await defer_response(interaction)

        self.is_confirmed = True
        await send(self._confirmed_message, ephemeral=True)
        self.stop()
        self.clear_items()

    @button(style=ButtonStyle.grey)
    async def cancel(self, interaction: Interaction, _: Button) -> None:
        """Cancel when pressed."""
        send = await defer_response(interaction)

        self.is_confirmed = False
        await send(self._cancelled_message, ephemeral=True)
        self.stop()
        self.clear_items()


class SelectView(View):
    """View that contains multiple selects."""

    def __init__( # noqa: C901
        self,
        *,
        options: list[SelectOption],
        placeholder: str,
        interaction: Interaction,
        min_selections: int = 0,
        max_selections: int | None = None,
    ) -> None:
        """Create a view with multiple selects
        :param options: Options for the selects
        :param placeholder: Placeholder for the selects
        :param interaction: The interaction of the command
        :param min_selections: Minimum number of selections that can be made
        :param max_selections: Maximum number of selections that can be made
        :raises ValueError: If there are too many options
        (more than Limit.SELECT_MAX * Limit.NUM_VIEWS_ITEMS).
        """
        super().__init__()

        self._max_selections = max_selections
        self._selected = set()

        if len(options) > Limit.SELECT_MAX.value * Limit.NUM_VIEWS_ITEMS.value:
            raise ValueError("Too many options")

        async def callback(select_interaction: Interaction, select: Select) -> None:
            self._selected.clear()

            for child in self.children:
                if not isinstance(child, Select):
                    continue

                self._selected.update(child.values)

            for child in self.children:
                if not isinstance(child, Select):
                    continue

                child.disabled = self._is_max_selected() and child is not select

                for option in child.options:
                    option.default = option.value in self._selected

            await interaction.edit_original_response(view=self)

            try:
                await select_interaction.response.send_message()
            except HTTPException as ex:
                if ex.code == ErrorCode.MESSAGE_EMPTY:
                    return

                raise

        for i in range(0, len(options), Limit.SELECT_MAX.value):
            partial_options = options[i : i + Limit.SELECT_MAX.value]
            select = Select(
                placeholder=placeholder,
                min_values=min_selections,
                max_values=min(len(partial_options), int(Limit.SELECT_MAX))
                if self._max_selections is None
                else self._max_selections,
                options=partial_options,
            )
            self.add_item(select)
            select.callback = lambda si, s=select: callback(si, s)

    @property
    def selected(self) -> Iterable[str]:
        """Get the selected values."""
        return self._selected

    def _is_max_selected(self) -> bool:
        """Check if the maximum number of selections is reached."""
        return (
            self._max_selections is not None
            and len(self._selected) >= self._max_selections
        )


class LanguageSelectView(SelectView):
    """Select UI to select available languages for a user."""

    def __init__(
        self,
        interaction: Interaction,
        placeholder: Coroutine[Any, Any, str],
        max_selections: int | None = None,
    ) -> None:
        """Create a language select UI.

        :param interaction: The interaction of the command
        :param placeholder: Placeholder for the select UI
        :param max_selections: Maximum number of languages that can be selected
        """
        super().__init__(
            options=[], placeholder=NOT_INITIALIZED_MESSAGE, interaction=interaction
        )

        self._interaction = interaction
        self._placeholder = placeholder
        self._max_selections = max_selections

    async def init(self) -> "LanguageSelectView":
        """Initialize this select."""
        loc = Localization(self._interaction.locale)

        languages = get_translator().get_supported_languages()

        options = sorted(
            [
                SelectOption(
                    label=await loc.format_value_or_translate(lang.code),
                    value=lang.code,
                )
                for lang in languages
            ],
            key=lambda x: x.label.lower(),
        )

        super().__init__(
            options=options,
            placeholder=await self._placeholder,
            interaction=self._interaction,
            max_selections=self._max_selections,
        )

        return self


class CommandSelect(Select):
    """Select UI to select a command."""

    def __init__(
        self,
        interaction: Interaction,
        hidden: set[type[Command | Group]] | None = None,
        placeholder: Coroutine[Any, Any, str] | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Create a command select UI.

        :param interaction: The interaction to get the locale from
        :param hidden: Set of commands to hide
        :param placeholder: Placeholder for the select UI
        :param kwargs: Other parameters to pass to the select UI
        """
        self._interaction = interaction
        self._hidden = hidden
        self._placeholder = placeholder
        self._kwargs = kwargs

        super().__init__(placeholder=NOT_INITIALIZED_MESSAGE)

    async def init(self) -> "CommandSelect":
        """Initialize this select."""
        super().__init__(
            placeholder=await self._placeholder if self._placeholder else None,
            options=await self._get_options(self._interaction, self._hidden),
            **self._kwargs,
        )
        return self

    @staticmethod
    async def _get_options(
        interaction: Interaction,
        hidden: set[type[Command | Group]] | None = None,
    ) -> list[SelectOption]:
        from main import bot

        language = Language(str(interaction.locale))

        if language == DEFAULT_LANGUAGE:
            options = [
                SelectOption(label=command.qualified_name)
                for command in bot.tree.walk_commands()
                if command not in hidden
            ]
        else:
            options = []
            localize = Localization.has(language.code)

            for command in bot.tree.walk_commands():
                if (
                    not isinstance(command, Command)
                    or command.root_parent.__class__ in hidden
                ):
                    continue

                if language == DEFAULT_LANGUAGE:
                    options.append(SelectOption(label=command.qualified_name))
                    continue

                translated_name = command.qualified_name.split(" ")
                root_name = translated_name[0]
                for i, name in enumerate(translated_name):
                    if localize:
                        loc = Localization(
                            language, [Path("commands") / f"{root_name}.ftl"]
                        )
                        translated_name[i] = loc.format_value(
                            f"{name.lower().replace('_', '-')}-name"
                        )
                    else:
                        translated_name[i] = await interaction.translate(name)

                options.append(
                    SelectOption(
                        label=" ".join(translated_name), value=command.qualified_name
                    )
                )

        return options

    async def callback(self, interaction: Interaction) -> Never:
        """Call when an option is selected."""
        raise NotImplementedError("This method should be overridden in a subclass")


class ChannelSelect(BaseChannelSelect):
    """Select UI to select channels."""

    def __init__(
        self,
        *,
        placeholder: Coroutine[Any, Any, str] | None = None,
        min_selections: int = 0,
        max_selections: int = Limit.SELECT_MAX.value,
    ) -> None:
        """Create a channel select UI.

        :param placeholder: Placeholder for the select UI
        :param min_selections: Minimum number of channels that can be selected
        :param max_selections: Maximum number of channels that can be selected
        """
        self._placeholder = placeholder
        self._min_selections = min_selections
        self._max_selections = max_selections

        super().__init__(placeholder=NOT_INITIALIZED_MESSAGE)

    async def init(self) -> "ChannelSelect":
        """Initialize the channel select UI."""
        super().__init__(
            placeholder=await self._placeholder if self._placeholder else None,
            channel_types=[x for x in ChannelType if x != ChannelType.category],
            min_values=self._min_selections,
            max_values=self._max_selections,
        )
        return self

    async def callback(self, interaction: Interaction) -> None:
        """Call when a channel is selected."""
        try:
            await interaction.response.send_message()
        except HTTPException as ex:
            if ex.code == ErrorCode.MESSAGE_EMPTY:
                return

            raise
        finally:
            await self.on_select(interaction)

    async def on_select(self, interaction: Interaction) -> None:
        """Call when a channel is selected.

        :param interaction: The interaction
        """
