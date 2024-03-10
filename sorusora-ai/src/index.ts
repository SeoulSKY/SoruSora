import dotenv from "dotenv";
import {Server, ServerCredentials} from "@grpc/grpc-js";
import {GreeterService} from "./protos/hello_grpc_pb";
import {GreeterServer} from "./hello";

// eslint-disable-next-line @typescript-eslint/no-var-requires
// const CharacterAI = require("node_characterai");


async function main() {
  dotenv.config({ path: "../.env" });

  const server = new Server();
  server.addService(GreeterService, new GreeterServer());

  server.bindAsync("0.0.0.0:50051", ServerCredentials.createInsecure(), () => {
    console.log("Server running at 0.0.0.0:50051");
  });

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
