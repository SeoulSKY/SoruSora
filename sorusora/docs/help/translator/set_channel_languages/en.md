# /translator set_channel_languages

Set or remove the languages to be translated for the selected channels.

For every message sent in the selected channels, SoruSora will translate the message into the selected languages and reply with the translations.

## Usage

* Use the dropdown menu to select the languages you want to translate messages into.
* Select no languages to disable translation for the selected channels.
* Set `this_channel` to `False` to apply the same settings to multiple channels.
* Press the `Submit` button to save the settings.

## Parameters

* `this_channel` (Optional): If set to `False`, it will send a dropdown menu to select multiple channels. Default value is `True`.

This command is only available for server admins.
