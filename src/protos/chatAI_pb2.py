# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chatAI.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0c\x63hatAI.proto\x1a\x1bgoogle/protobuf/empty.proto\"\x1d\n\rCreateRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\" \n\x0e\x43reateResponse\x12\x0e\n\x06\x63hatId\x18\x01 \x01(\t\"+\n\x0bSendRequest\x12\x0e\n\x06\x63hatId\x18\x01 \x01(\t\x12\x0c\n\x04text\x18\x02 \x01(\t\"\x1c\n\x0cSendResponse\x12\x0c\n\x04text\x18\x01 \x01(\t\"\x1e\n\x0c\x43learRequest\x12\x0e\n\x06\x63hatId\x18\x01 \x01(\t2\x8e\x01\n\x06\x43hatAI\x12+\n\x06\x43reate\x12\x0e.CreateRequest\x1a\x0f.CreateResponse\"\x00\x12%\n\x04Send\x12\x0c.SendRequest\x1a\r.SendResponse\"\x00\x12\x30\n\x05\x43lear\x12\r.ClearRequest\x1a\x16.google.protobuf.Empty\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chatAI_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_CREATEREQUEST']._serialized_start=45
  _globals['_CREATEREQUEST']._serialized_end=74
  _globals['_CREATERESPONSE']._serialized_start=76
  _globals['_CREATERESPONSE']._serialized_end=108
  _globals['_SENDREQUEST']._serialized_start=110
  _globals['_SENDREQUEST']._serialized_end=153
  _globals['_SENDRESPONSE']._serialized_start=155
  _globals['_SENDRESPONSE']._serialized_end=183
  _globals['_CLEARREQUEST']._serialized_start=185
  _globals['_CLEARREQUEST']._serialized_end=215
  _globals['_CHATAI']._serialized_start=218
  _globals['_CHATAI']._serialized_end=360
# @@protoc_insertion_point(module_scope)