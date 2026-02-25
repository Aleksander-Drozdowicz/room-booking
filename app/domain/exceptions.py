class BookingValidationException(ValueError):
    pass


class HolidayBookingForbiddenException(BookingValidationException):
    pass


class ReservationConflictException(BookingValidationException):
    pass


class TooManyReservationsException(BookingValidationException):
    pass


class TooLateToCancelException(BookingValidationException):
    pass


class ReservationNotFoundException(LookupError):
    pass