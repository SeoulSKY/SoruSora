import dotenv from "dotenv";
import log4js from "log4js";
import {Server, ServerCredentials} from "@grpc/grpc-js";
import {ChatAIService} from "./protos/chatAI_grpc_pb";
import {ChatAIServer} from "./chatAI";
import path from "path";

const URL: string = "0.0.0.0:50051";
const logger = log4js.getLogger();

const LOGS_DIR = "logs";

async function main() {
  dotenv.config({ path: "../.env" });

  log4js.configure({
    appenders: {
      console: { type: "console" },
      error: {
        type: "dateFile",
        filename: path.join(LOGS_DIR, "error.log"),
        pattern: ".yyyy-MM-dd",
        keepFileExt: true,
        level: "error"
      },
      warning: {
        type: "dateFile",
        filename: path.join(LOGS_DIR, "warning.log"),
        pattern: ".yyyy-MM-dd",
        keepFileExt: true,
        level: "warn"
      }
    },
    categories: {
      default: {
        appenders: ["console"],
        level: "info"
      },
      error: {
        appenders: ["console", "error"],
        level: "error"
      },
      warning: {
        appenders: ["console", "warning"],
        level: "warn"
      }
    }
  });

  const server = new Server();
  server.addService(ChatAIService, new ChatAIServer());

  server.bindAsync(URL, ServerCredentials.createInsecure(), () => {
    logger.info(`Server running at ${URL}`);
  });
}

(async () => {
  await main();
})();
