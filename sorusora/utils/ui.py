"""
Provides list of ui elements

classes:
    Confirm
    LanguageSelectView
    CommandSelect
"""

import os
from typing import Union, Optional, Type, Coroutine, Any, Iterable

from discord import SelectOption, Interaction, Locale, ChannelType, ButtonStyle, HTTPException
from discord.app_commands import Command, Group
from discord.ui import Select, View, Button, button, ChannelSelect as ChannelSelectView

from utils import defer_response
from utils.constants import Limit, ErrorCode
from utils.templates import info, success
from utils.translator import Localization, Language, DEFAULT_LANGUAGE, get_translator

resources = [os.path.join("utils", "ui.ftl")]

NOT_INITIALIZED_MESSAGE = "Not initialized. Call init() first"


class SubmitButton(Button):
    """
    Button to submit the form
    """

    def __init__(self, locale: Locale, style: ButtonStyle = ButtonStyle.green):
        """
        Create a submit button
        :param style: Style of the button
        """

        self.loc = Localization(locale, resources)
        self._style = style

        super().__init__(label=NOT_INITIALIZED_MESSAGE)

    async def init(self):
        """
        Initialize the button
        """

        super().__init__(label=await self.loc.format_value_or_translate("submit"), style=self._style)
        return self


class Confirm(View):
    """
    Buttons for confirmation
    """

    def __init__(self, confirmed_message: str, cancelled_message: str, locale: Locale = DEFAULT_LANGUAGE):
        """
        View to get a confirmation from a user. When the confirm button is pressed, set the is_confirmed to `True` and
        stop the View from listening to more input
        :param confirmed_message: A message to send when the user confirmed
        :param cancelled_message: A message to send when the user cancelled
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
        """
        Initialize the view
        """

        loc = Localization(self._locale, resources)

        self.confirm.label = await loc.format_value_or_translate("confirm")
        self.cancel.label = await loc.format_value_or_translate("cancel")

        return self

    @button(style=ButtonStyle.green)
    async def confirm(self, interaction: Interaction, _: Button):
        """
        Confirm when pressed
        """

        send = await defer_response(interaction)

        self.is_confirmed = True
        await send(self._confirmed_message, ephemeral=True)
        self.stop()
        self.clear_items()

    @button(style=ButtonStyle.grey)
    async def cancel(self, interaction: Interaction, _: Button):
        """
        Cancel when pressed
        """

        send = await defer_response(interaction)

        self.is_confirmed = False
        await send(self._cancelled_message, ephemeral=True)
        self.stop()
        self.clear_items()


class LanguageSelectView(View):
    """
    Select UI to select available languages for a user
    """

    def __init__(self,
                 interaction: Interaction,
                 placeholder: Coroutine[Any, Any, str],
                 max_selections: int = None,
                 **kwargs):
        """
        Create a language select UI

        :param interaction: The interaction of the command
        :param placeholder: Placeholder for the select UI
        :param max_selections: Maximum number of languages that can be selected
        :param kwargs: Other parameters to pass to the select UI
        """

        super().__init__()

        self._interaction = interaction
        self._placeholder = placeholder
        self._max_selections = max_selections
        self._kwargs = kwargs

        self._selected: set[str] = set()

    async def init(self) -> "LanguageSelectView":
        """
        Initialize this select
        """

        async def callback(interaction: Interaction, select: Select):
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

            await self._interaction.edit_original_response(view=self)

            try:
                await interaction.response.send_message()
            except HTTPException as ex:
                if ex.code == ErrorCode.MESSAGE_EMPTY:
                    return

                raise ex

        loc = Localization(self._interaction.locale)

        languages = get_translator().get_supported_languages()
        placeholder = await self._placeholder

        all_options = sorted([SelectOption(label=await loc.format_value_or_translate(lang.code), value=lang.code)
                              for lang in languages], key=lambda x: x.label.lower())

        for i in range(0, len(all_options), int(Limit.SELECT_MAX)):
            options = all_options[i:i + int(Limit.SELECT_MAX)]
            select = Select(
                placeholder=placeholder,
                min_values=0,
                max_values=min(len(options), int(Limit.SELECT_MAX))
                if self._max_selections is None else self._max_selections,
                options=options,
                **self._kwargs
            )

            select.callback = lambda interaction, s=select: callback(interaction, s)
            self.add_item(select)

        return self

    @property
    def selected(self) -> Iterable[str]:
        """
        Get the selected languages
        """

        return self._selected

    def _is_max_selected(self) -> bool:
        """
        Check if the maximum number of selections is reached
        """

        return self._max_selections is not None and len(self._selected) >= self._max_selections


class CommandSelect(Select):
    """
    Select UI to select a command
    """

    def __init__(self, interaction: Interaction, hidden: Optional[set[Type[Union[Command, Group]]]] = None,
                 placeholder: Coroutine[Any, Any, str] = None, **kwargs):
        """
        Create a command select UI

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
        """
        Initialize this select
        """

        super().__init__(placeholder=await self._placeholder if self._placeholder else None,
                         options=await self._get_options(self._interaction, self._hidden), **self._kwargs)
        return self

    @staticmethod
    async def _get_options(interaction: Interaction, hidden: Optional[set[Type[Union[Command, Group]]]] = None) \
            -> list[SelectOption]:
        from main import bot  # pylint: disable=import-outside-toplevel

        language = Language(str(interaction.locale))

        if language == DEFAULT_LANGUAGE:
            options = [SelectOption(label=command.qualified_name) for command in bot.tree.walk_commands()
                       if command not in hidden]
        else:
            options = []
            localize = Localization.has(language.code)

            for command in bot.tree.walk_commands():
                if not isinstance(command, Command) or command.root_parent.__class__ in hidden:
                    continue

                if language == DEFAULT_LANGUAGE:
                    options.append(SelectOption(label=command.qualified_name))
                    continue

                translated_name = command.qualified_name.split(" ")
                root_name = translated_name[0]
                for i, name in enumerate(translated_name):
                    if localize:
                        loc = Localization(language, [os.path.join("commands", f"{root_name}.ftl")])
                        translated_name[i] = loc.format_value(f"{name.lower().replace('_', '-')}-name")
                    else:
                        translated_name[i] = await interaction.translate(name)

                options.append(SelectOption(label=" ".join(translated_name), value=command.qualified_name))

        return options

    async def callback(self, interaction: Interaction):
        raise NotImplementedError("This method should be overridden in a subclass")


class ChannelSelect(ChannelSelectView):
    """
    Select UI to select channels
    """

    def __init__(self, placeholder: Coroutine[Any, Any, str] = None):
        """
        Create a channel select UI

        :param placeholder: Placeholder for the select UI
        """
        self._placeholder = placeholder

        super().__init__(placeholder=NOT_INITIALIZED_MESSAGE)

    async def init(self) -> "ChannelSelect":
        """
        Initialize the channel select UI
        """
        super().__init__(placeholder=await self._placeholder if self._placeholder else None,
                         channel_types=[x for x in ChannelType if x != ChannelType.category],
                         min_values=0,
                         max_values=int(Limit.SELECT_MAX))
        return self

    async def callback(self, interaction: Interaction):
        try:
            await interaction.response.send_message()
        except HTTPException as ex:
            if ex.code == ErrorCode.MESSAGE_EMPTY:
                return

            raise ex
