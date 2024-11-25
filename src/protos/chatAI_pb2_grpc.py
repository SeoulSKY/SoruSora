# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

import chatAI_pb2 as chatAI__pb2


class ChatAIStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Create = channel.unary_unary(
                '/ChatAI/Create',
                request_serializer=chatAI__pb2.CreateRequest.SerializeToString,
                response_deserializer=chatAI__pb2.CreateResponse.FromString,
                )
        self.Send = channel.unary_unary(
                '/ChatAI/Send',
                request_serializer=chatAI__pb2.SendRequest.SerializeToString,
                response_deserializer=chatAI__pb2.SendResponse.FromString,
                )
        self.Clear = channel.unary_unary(
                '/ChatAI/Clear',
                request_serializer=chatAI__pb2.ClearRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class ChatAIServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Create(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Send(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Clear(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatAIServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=chatAI__pb2.CreateRequest.FromString,
                    response_serializer=chatAI__pb2.CreateResponse.SerializeToString,
            ),
            'Send': grpc.unary_unary_rpc_method_handler(
                    servicer.Send,
                    request_deserializer=chatAI__pb2.SendRequest.FromString,
                    response_serializer=chatAI__pb2.SendResponse.SerializeToString,
            ),
            'Clear': grpc.unary_unary_rpc_method_handler(
                    servicer.Clear,
                    request_deserializer=chatAI__pb2.ClearRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ChatAI', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ChatAI(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Create(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ChatAI/Create',
            chatAI__pb2.CreateRequest.SerializeToString,
            chatAI__pb2.CreateResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Send(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ChatAI/Send',
            chatAI__pb2.SendRequest.SerializeToString,
            chatAI__pb2.SendResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Clear(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ChatAI/Clear',
            chatAI__pb2.ClearRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
