import {ServerUnaryCall, sendUnaryData, UntypedHandleCall, status} from "@grpc/grpc-js";
import {Empty} from "google-protobuf/google/protobuf/empty_pb";
import log4js from "log4js";

import {IChatAIServer} from "./protos/chatAI_grpc_pb";
import {ClearRequest, CreateRequest, CreateResponse, SendRequest, SendResponse} from "./protos/chatAI_pb";
import {clearChat, createChat, sendMessage, TimeoutError, NotFoundError} from "./characterAI";

const logger = log4js.getLogger();

export class ChatAIServer implements IChatAIServer {
  [name: string]: UntypedHandleCall;

  clear(call: ServerUnaryCall<ClearRequest, Empty>, callback: sendUnaryData<Empty>): void {
    clearChat(call.request.getChatid())
      .then(() => callback(null, new Empty()))
      .catch(err => handleError(err, callback));
  }

  create(call: ServerUnaryCall<CreateRequest, CreateResponse>, callback: sendUnaryData<CreateResponse>): void {
    createChat(call.request.getName())
      .then(chatId => callback(null, new CreateResponse().setChatid(chatId)))
      .catch(err => handleError(err, callback));
  }

  send(call: ServerUnaryCall<SendRequest, SendResponse>, callback: sendUnaryData<SendResponse>): void {
    sendMessage(call.request.getChatid(), call.request.getText())
      .then(reply => callback(null, new SendResponse().setText(reply.text)))
      .catch(err => handleError(err, callback));
  }
}

function handleError(err: Error, callback: sendUnaryData<never>): void {
  if (err instanceof NotFoundError) {
    callback({
      code: status.NOT_FOUND,
      details: err.message
    }, null);
    return;
  } else if (err instanceof TimeoutError) {
    callback({
      code: status.DEADLINE_EXCEEDED,
      details: err.message
    }, null);
    return;
  }

  if (err && err.stack) {
    logger.error(`${err}\n${err.stack}`);
  } else {
    logger.error(err);
  }
  callback(err, null);
}
