# Commands
chat-name = 聊天
chat-description = AI聊天相關指令

clear-name = 清除
clear-description = 刪除{ $clear-description-name }和你之間的所有聊天記錄。

token-name = 令牌
token-description = 設置用於聊天的代幣
token-value-name = 值
token-value-description = 要配置的令牌

tutorial-name = 用法
tutorial-description = 教你如何與{ $tutorial-description-name }聊天

# Successes
updated = 聊天語言已更新為`{ $language }`
deleted = 成功刪除您跟{ $name }的聊天歷史紀錄
token-set = 令牌已設置
token-removed = 由於未輸入參數`值`，令牌已被刪除

# Errors
token-invalid = 您輸入的令牌無效
token-no-longer-valid = 您設置的代幣不再有效。請重新設置
token-no-permission = 令牌有效，但沒有設置合適的權限。您可以在這裏更新: { $link }
too-many-requests = 已超過可發送短信的次數。您可以等到明天，或者用`/聊天令牌`設置自己的代幣
server-unavailable = 服務器好像暫時癱瘓了。請稍後再試
unknown-error = 發生了未知的錯誤 。可能是聊天記錄中的錯誤信息造成的。請修改後再試一次
