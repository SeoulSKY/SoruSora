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

        super().__init__(label="Not initialized. Call init() first")

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

    def __init__(self, placeholder: Coroutine[Any, Any, str], locale: Locale, max_values: int = None, **kwargs):
        """
        Create a language select UI

        :param placeholder: Placeholder for the select UI
        :param locale: Locale of the user
        :param max_values: Maximum number of languages that can be selected
        :param kwargs: Other parameters to pass to the select UI
        """

        super().__init__()

        self._placeholder = placeholder
        self._locale = locale
        self._max_values = max_values
        self._kwargs = kwargs

        self._selects: set[Select] = set()
        self._selected: set[str] = set()

    async def init(self) -> "LanguageSelectView":
        """
        Initialize this select
        """

        loc = Localization(self._locale)

        languages = get_translator().get_supported_languages()
        placeholder = await self._placeholder

        all_options = sorted([SelectOption(label=await loc.format_value_or_translate(lang.code), value=lang.code)
                              for lang in languages], key=lambda x: x.label.lower())

        for i in range(0, len(all_options), int(Limit.SELECT_MAX)):
            options = all_options[i:i + int(Limit.SELECT_MAX)]
            select = Select(
                placeholder=placeholder,
                max_values=min(len(options), int(Limit.SELECT_MAX)) if self._max_values is None else self._max_values,
                options=options,
                **self._kwargs
            )
            select.callback = self.callback
            self.add_item(select)
            self._selects.add(select)

        return self

    async def callback(self, interaction: Interaction):
        """
        Callback for the select
        """

        self._selected.clear()

        for select in self._selects:
            self._selected.update(select.values)

        try:
            await interaction.response.send_message()
        except HTTPException as ex:
            if ex.code == ErrorCode.MESSAGE_EMPTY:
                return

            raise ex

    @property
    def selected(self) -> Iterable[str]:
        """
        Get the selected languages
        """

        return self._selected


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
        super().__init__(placeholder="Not initialized. Call init() method first")

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

        super().__init__(placeholder="Not initialized. Call init() first")

    async def init(self) -> "ChannelSelect":
        """
        Initialize the channel select UI
        """
        super().__init__(placeholder=await self._placeholder if self._placeholder else None,
                         channel_types=[x for x in ChannelType if x != ChannelType.category],
                         max_values=int(Limit.SELECT_MAX))
        return self

    async def callback(self, interaction: Interaction):
        try:
            await interaction.response.send_message()
        except HTTPException as ex:
            if ex.code == ErrorCode.MESSAGE_EMPTY:
                return

            raise ex
