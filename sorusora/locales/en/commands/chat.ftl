# Commands
chat-name = chat
chat-description = Commands related to AI chats

set-language-name = set_language
set-language-description = Set the chat language to the current discord language
set-language-current-language-name = current_language
set-language-current-language-description = Set your chat language to your current discord language. Defaults to { $set-language-current-language-description-default}
set-language-select = Select your chat language

clear-name = clear
clear-description = Clear the chat history between you and { $clear-description-name }

# Successes
updated = The chat language has been updated to `{ $language }`
deleted = Deleted!

# Errors
no-history = You don't have any conversations with { $name }
timeout = Looks like { $name } has turned on the Do Not Disturb mode. Let's talk to her later
