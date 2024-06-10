# /translator set_channel_main_language

Set or remove the main language of the channels. The translator will set the selected language as the source language for all messages in the channels.

If the main language of a channel is not set, the translator will detect the language of each message and use it as the source language.

## Usage

* Use the dropdown menu to select the main language for the channels.
* Select no languages to remove the main language from the channels.
* Set `this_channel` to `False` to apply the same settings to multiple channels.
* Press the `Submit` button to save the settings.

## Parameters

* `this_channel` (Optional): If set to `False`, it will send a dropdown menu to select multiple channels. Default value is `True`.

This command is only available for server admins.
