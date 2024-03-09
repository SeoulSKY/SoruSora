import dotenv from "dotenv";

// eslint-disable-next-line @typescript-eslint/no-var-requires
// const CharacterAI = require("node_characterai");


async function main() {
  dotenv.config({ path: "../.env" });

  console.log("hello world!");

  // const characterAI = new CharacterAI();
  // await characterAI.authenticateWithToken(process.env.CAI_TOKEN);
  //
  // // Place your character's id here
  // const characterId = "8_1NyR8w1dOXmI1uWaieQcd147hecbdIK7CeEAIrdJw";
  //
  // const chat = await characterAI.createOrContinueChat(characterId);
  //
  // // Send a message
  // const response = await chat.sendAndAwaitResponse(
  //     "Hello discord mod!",
  //     true
  // );
  //
  // console.log(response);
}

(async () => {
  await main();
})();
