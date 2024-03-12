import {ServerUnaryCall, sendUnaryData, UntypedHandleCall, status} from "@grpc/grpc-js";
import {IChatAIServer} from "./protos/chatAI_grpc_pb";
import {ClearRequest, CreateRequest, CreateResponse, SendRequest, SendResponse} from "./protos/chatAI_pb";
import {Empty} from "google-protobuf/google/protobuf/empty_pb";

import {clearChat, createChat, sendMessage} from "./characterAI";
import log4js from "log4js";

const logger = log4js.getLogger();

export class ChatAIServer implements IChatAIServer {
  [name: string]: UntypedHandleCall;

  clear(call: ServerUnaryCall<ClearRequest, Empty>, callback: sendUnaryData<Empty>): void {
    clearChat(call.request.getChatid()
    ).then(() =>
      callback(null, new Empty())
    ).catch(err => {
      logger.error(err);
      callback({
          code: status.NOT_FOUND,
          details: err.message
      }, null);
    });
  }

  create(call: ServerUnaryCall<CreateRequest, CreateResponse>, callback: sendUnaryData<CreateResponse>): void {
    createChat(call.request.getName()
    ).then(chatId => {
      callback(null, new CreateResponse().setChatid(chatId));
    }).catch(err => {
      logger.error(err);
      callback(err, null);
    });
  }

  send(call: ServerUnaryCall<SendRequest, SendResponse>, callback: sendUnaryData<SendResponse>): void {
    sendMessage(call.request.getChatid(), call.request.getText()
    ).then(reply => callback(null, new SendResponse().setText(reply.text))
    ).catch(err => {
      logger.error(err);
      callback({
          code: status.NOT_FOUND,
          details: err.message
      }, null);
    });
  }
}
