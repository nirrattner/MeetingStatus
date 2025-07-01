import typing


class BaseModel:
  TYPES = {}

  def __repr__(self):
    classname = self.__class__.__name__
    values = ' '.join([f'{key}={value}' for (key, value) in vars(self).items() if key[0] != '_'])
    return f'<{classname} {values}>'

  @property
  def to_dict(self) -> dict:
    output_dict = {}
    for attribute, value in self.__dict__.items():
      if value is None:
        continue
      output_dict[attribute] = to_dict_value(value)
    return output_dict

  @classmethod
  def from_dict(cls, input_dict):
    instance = cls()
    for attribute, value in input_dict.items():
      if attribute in cls.TYPES:
        value = from_dict_value(cls.TYPES[attribute], value)
      instance.__dict__[attribute] = value
    return instance


def to_dict_value(value):
  if hasattr(value, 'to_dict'):
    return value.to_dict
  if isinstance(value, list):
    return [to_dict_value(element) for element in value]
  return value


def from_dict_value(value_type, value):
  if isinstance(value, list):
    element_value_type = typing.get_args(value_type)[0]
    return [from_dict_value(element_value_type, element) for element in value]
  return value_type.from_dict(value)
