import CharacterAI from "node_characterai";
import dotenv from "dotenv";

let chat;

(async () => {
  dotenv.config({ path: "../.env" });

  const characterAI = new CharacterAI();

  characterAI.requester.puppeteerPath = process.env.CHROME_PATH;
  characterAI.requester.puppeteerNoDefaultTimeout = true;

  await characterAI.authenticateWithToken(process.env.CAI_TOKEN);
  chat = await characterAI.createOrContinueChat(process.env.CAI_CHAR_ID);

  if (chat === undefined) {
    throw new Error("Invalid Chat ID");
  }
})();

/**
 * Create a new chat and return the chat ID
 * @param userName {string} name of the user
 * @returns {Promise<string>} chat ID
 */
export async function createChat(userName) {
  await chat.saveAndStartNewChat();
  await chat.sendAndAwaitResponse(`(OCC: Forget about my previous name. My new name is ${userName})`,
    true);

  return chat.externalId;
}

/**
 * Clear the chat history
 * @param id {string} chat ID to clear
 * @returns {Promise<void>}
 * @throws {Error} if the chat ID is invalid
 */
export async function clearChat(id) {
  await chat.changeToConversationId(id);
  let history = await chat.fetchHistory(null);

  if (history === undefined) {
    throw new Error("Invalid Chat ID");
  }

  let messageIds = history.messages.map((message) => message.uuid);
  await chat.deleteMessages(messageIds);
}

/**
 * Send a message to the AI and get the response
 * @param id {string} chat ID
 * @param message {string} message to send
 * @returns {Promise<Reply>} response from the AI
 */
export async function sendMessage(id, message) {
  await chat.changeToConversationId(id);
  return await chat.sendAndAwaitResponse(message, true);
}
