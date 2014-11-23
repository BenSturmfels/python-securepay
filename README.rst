==================
 Python Securepay
==================

`securepay` is a Python interface to the Securepay credit card payment gateway.

This module doesn't yet provide credit card authorisation transactions (ie.
putting some money on hold for an upcoming payment).

TODO:

* remove dependency on pytz
* may payments live by default
* display warnings for error code payments against debug
* add credit authorisation
* decide whether to test against live or mock it, separate integration tests?
  public testing account?
* Python 3 support
* add awesome logging
* merge in reconciliation tool
