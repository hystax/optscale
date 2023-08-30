
class ValidatorMixin(object):
    def get_validator(self, key, *args, **kwargs):
        return getattr(type(self), key).type.validator(*args, **kwargs)
