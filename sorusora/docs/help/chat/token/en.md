# /chat token

Set the token that will be used to chat with SoruSora.

Each token has a limit of number of messages SoruSora can respond per day. If a token is not set, a default token is used that is shared with all users. Using your own token allows you to chat with SoruSora more freely.

To create a token for free, visit [here](https://makersuite.google.com/app/apikey)

The token is encrypted before saving to the database. To see how it is encrypted, visit [here](https://github.com/SeoulSKY/SoruSora/blob/master/sorusora/src/commands/chat.py)
