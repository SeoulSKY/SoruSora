import CharacterAI from "node_characterai";
import dotenv from "dotenv";
import {Mutex} from "async-mutex";

export class TimeoutError extends Error {
  constructor(message) {
    super(message);
  }
}

export class NotFoundError extends Error {
  constructor(message) {
    super(message);
  }
}

let chat;
const mutex = new Mutex();

/**
 * Create a new chat and return the chat ID
 * @param userName {string} name of the user
 * @returns {Promise<string>} chat ID
 */
export async function createChat(userName) {
  return await mutex.runExclusive(async () => {
    await chat.saveAndStartNewChat();
    await _sendMessage(chat.externalId, `(OCC: Forget about my previous name. My new name is ${userName})`);
    return chat.externalId;
  });
}

/**
 * Clear the chat history
 * @param id {string} chat ID to clear
 * @returns {Promise<void>}
 * @throws {NotFoundError} if the chat ID is invalid
 */
export async function clearChat(id) {
  await mutex.runExclusive(async () => {
    await chat.changeToConversationId(id);
    let history = await chat.fetchHistory(null);

    if (history === undefined) {
      throw new NotFoundError(`Chat ID ${id} not found`);
    }

    let messageIds = history.messages.map((message) => message.uuid);
    await chat.deleteMessages(messageIds);
  });
}

/**
 * Send a message to the AI and get the response
 * @param id {string} chat ID
 * @param message {string} message to send
 * @returns {Promise<Reply>} response from the AI
 * @throws {TimeoutError} if the AI doesn't respond in time
 */
export async function sendMessage(id, message) {
  return await mutex.runExclusive(async () => _sendMessage(id, message));
}

async function _sendMessage(id, message) {
  await chat.changeToConversationId(id);

  try {
    return await chat.sendAndAwaitResponse(message, true);
  } catch (error) {
    if (error instanceof SyntaxError) { // entered the waiting room
      throw new TimeoutError("AI didn't respond in time");
    }
    throw error;
  }
}

(async () => {
  dotenv.config({ path: "../.env" });

  const characterAI = new CharacterAI();

  characterAI.requester.puppeteerPath = process.env.CHROME_PATH;
  characterAI.requester.puppeteerNoDefaultTimeout = true;

  mutex.runExclusive(async () => {
    await characterAI.authenticateWithToken(process.env.CAI_TOKEN);
    chat = await characterAI.createOrContinueChat(process.env.CAI_CHAR_ID);
  });
})();
