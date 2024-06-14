# /channel translator

Set or remove a translator for channels.

For every message sent in the selected channels, SoruSora will translate the message into the selected languages and reply with the translations.

If the main language of the channels is not selected using `/channel language`, the language used in the message will be detected automatically.

## Usage

* Use the dropdown menu to select the languages you want to translate messages into.
* Select no languages to remove the translator.
* Set `this` to `False` to set the translator to multiple channels.
* Press the `Submit` button to save the settings.

## Parameters

* `this` (Optional): If set to `False`, it will send a dropdown menu to select multiple channels. Default value is `True`.

This command is only available to the users who have the permission to manage the channels.
