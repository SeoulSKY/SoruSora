import {ServerUnaryCall, sendUnaryData, UntypedHandleCall} from "@grpc/grpc-js";
import { HelloRequest, HelloResponse } from "./protos/hello_pb";
import { IGreeterServer } from "./protos/hello_grpc_pb";


export class GreeterServer implements IGreeterServer {
    sayHello(call: ServerUnaryCall<HelloRequest, HelloResponse>, callback: sendUnaryData<HelloResponse>): void {
        const response = new HelloResponse();

        response.setMessage(`Hello, ${call.request.getName()}`);
        callback(null, response);
    }

    [name: string]: UntypedHandleCall;
}