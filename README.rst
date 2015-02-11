==================
 Python Securepay
==================

`securepay` is a Python interface to the Securepay credit card payment gateway.

This module doesn't yet provide credit card authorisation transactions (ie.
putting some money on hold for an upcoming payment).

TODO:

* remove dependency on pytz
* make payments live by default
* display warnings for error code payments against debug
* add credit authorisation
* update tests to mock out live gateway
  public testing account?
* add detailed logging
* merge in reconciliation tool
