# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: amazon_client.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='amazon_client.proto',
  package='',
  syntax='proto2',
  serialized_pb=_b('\n\x13\x61mazon_client.proto\"9\n\x07Product\x12\n\n\x02id\x18\x01 \x02(\x03\x12\x13\n\x0b\x64\x65scription\x18\x02 \x02(\t\x12\r\n\x05\x63ount\x18\x03 \x02(\x05\"Y\n\x06\x41Order\x12\x0f\n\x07orderid\x18\x01 \x02(\x05\x12\x0e\n\x06userid\x18\x02 \x02(\x05\x12\x18\n\x06things\x18\x03 \x03(\x0b\x32\x08.Product\x12\t\n\x01x\x18\x04 \x02(\x05\x12\t\n\x01y\x18\x05 \x02(\x05')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_PRODUCT = _descriptor.Descriptor(
  name='Product',
  full_name='Product',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Product.id', index=0,
      number=1, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='description', full_name='Product.description', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='count', full_name='Product.count', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=23,
  serialized_end=80,
)


_AORDER = _descriptor.Descriptor(
  name='AOrder',
  full_name='AOrder',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='orderid', full_name='AOrder.orderid', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='userid', full_name='AOrder.userid', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='things', full_name='AOrder.things', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='x', full_name='AOrder.x', index=3,
      number=4, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='y', full_name='AOrder.y', index=4,
      number=5, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=82,
  serialized_end=171,
)

_AORDER.fields_by_name['things'].message_type = _PRODUCT
DESCRIPTOR.message_types_by_name['Product'] = _PRODUCT
DESCRIPTOR.message_types_by_name['AOrder'] = _AORDER

Product = _reflection.GeneratedProtocolMessageType('Product', (_message.Message,), dict(
  DESCRIPTOR = _PRODUCT,
  __module__ = 'amazon_client_pb2'
  # @@protoc_insertion_point(class_scope:Product)
  ))
_sym_db.RegisterMessage(Product)

AOrder = _reflection.GeneratedProtocolMessageType('AOrder', (_message.Message,), dict(
  DESCRIPTOR = _AORDER,
  __module__ = 'amazon_client_pb2'
  # @@protoc_insertion_point(class_scope:AOrder)
  ))
_sym_db.RegisterMessage(AOrder)


# @@protoc_insertion_point(module_scope)