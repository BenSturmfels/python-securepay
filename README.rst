==================
 Python Securepay
==================

`securepay` is a Python interface to the Securepay credit card payment gateway.

This module doesn't yet provide credit card authorisation transactions (ie.
putting some money on hold for an upcoming payment).

Quickstart
-----------

This package can be used as follows::

    from securepay import pay_by_cc, refund, SecurePayError

    SECUREPAY_API_URL= 'https://test.securepay.com.au/xmlapi/payment'
    SECUREPAY_MERCHANT_ID = '...'
    SECUREPAY_PASSWORD = '...'

    # Take a credit card payment.
    try:
        pay_attempt = pay_by_cc(
            cents, purchase_order_id, cc_number, cc_expiry,
            SECUREPAY_API_URL, SECUREPAY_MERCHANT_ID,
            SECUREPAY_PASSWORD, cc_card_name)
    except SecurePayError as err:
        # Give customers a generic error about service being unavailable.

    if pay_attempt['approved']:
        # Payment successful!
    else:
        # Payment declined. Error message is in pay_attempt['bank_response_text']


    # Refund the payment.
    try:
        refund_attempt = securepay.refund(
            cents, purchase_order_id, transaction_ref, SECUREPAY_API_URL,
            SECUREPAY_MERCHANT_ID, SECUREPAY_PASSWORD)
    except SecurePayError as err:
        # Give staff member a generic error about service being unavailable.

    if pay_attempt['approved']:
        # Refund successful!
    else:
        # Refund declined. Error message is in pay_attempt['bank_response_text']


To Do
-----

* remove dependency on `PyTZ`
* remove dependency on `LXML`
* display warnings for error code payments against debug
* add credit authorisation
* update tests to mock out live gateway
* add detailed logging
* merge in reconciliation tool
* return payment date, usually current day, but if after 10pm AEST is the
  following day - help with reporting and reconciliation

