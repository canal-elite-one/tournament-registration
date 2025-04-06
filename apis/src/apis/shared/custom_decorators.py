from apis.shared.api_errors import RegistrationCutoffError, RegistrationMessages
from apis.shared.db import is_before_cutoff, is_before_start


def during_registration(endpoint):
    def during_wrapper(*args, **kwargs):
        if not is_before_cutoff():
            raise RegistrationCutoffError(
                origin=endpoint.__name__,
                error_message=RegistrationMessages.ENDED,
            )

        if is_before_start():
            raise RegistrationCutoffError(
                origin=endpoint.__name__,
                error_message=RegistrationMessages.NOT_STARTED,
            )
        return endpoint(*args, **kwargs)

    during_wrapper.__name__ = endpoint.__name__
    return during_wrapper


def after_registration_start(endpoint):
    def after_wrapper(*args, **kwargs):
        if is_before_start():
            raise RegistrationCutoffError(
                origin=endpoint.__name__,
                error_message=RegistrationMessages.NOT_STARTED,
            )
        return endpoint(*args, **kwargs)

    after_wrapper.__name__ = endpoint.__name__
    return after_wrapper


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
