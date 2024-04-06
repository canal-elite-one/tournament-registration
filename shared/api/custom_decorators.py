from shared.api.api_errors import RegistrationCutoffError, RegistrationMessages
from shared.api.db import is_before_cutoff


def before_cutoff(endpoint):
    def before_wrapper(*args, **kwargs):
        if not is_before_cutoff():
            raise RegistrationCutoffError(
                origin=endpoint.__name__,
                error_message=RegistrationMessages.ENDED,
            )
        return endpoint(*args, **kwargs)

    before_wrapper.__name__ = endpoint.__name__
    return before_wrapper


def after_cutoff(endpoint):
    def after_wrapper(*args, **kwargs):
        if is_before_cutoff():
            raise RegistrationCutoffError(
                origin=endpoint.__name__,
                error_message=RegistrationMessages.NOT_ENDED,
            )
        return endpoint(*args, **kwargs)

    after_wrapper.__name__ = endpoint.__name__
    return after_wrapper
