# Commands
chat-name = chat
chat-description = Commands related to AI chats

set-language-name = set_language
set-language-description = Set the chat language to the current discord language
set-language-current-language-name = current_language
set-language-current-language-description = Set your chat language to your current discord language. Defaults to { $set-language-current-language-description-default}
set-language-select = Select your chat language

clear-name = clear
clear-description = Clear the entire chat history between you and { $clear-description-name }

token-name = token
token-description = Set the token for chat
token-value-name = value
token-value-description = The token to set

# Successes
updated = The chat history has been updated
deleted = The chat history has been deleted
token-set = The token has been set
token-removed = The token has been removed because the argument `value` wasn't provided

# Errors
token-invalid = Given token is invalid
token-no-longer-valid = The token you set is no longer valid. Please set a new one
token-no-permission = Your token is valid, but you didn't set proper permissions to the token. You can update it here: { $link }
too-many-requests = The limit of sending messages has been reached. You can either wait until tomorrow or set your own token with `/chat token`
server-unavailable = The server might be temporarily down. Please try again later
unknown-error = An unknown error occurred. The cause might be the invalid messages in your chat history. Try modifying them and try again
