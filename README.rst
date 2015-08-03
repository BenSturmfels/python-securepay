==================
 Python Securepay
==================

SecurePay in an Australian payment gateway provider. This library can be used to
request and refund payment on demand.

Quickstart
-----------

This package can be used as follows:

.. code-block:: python

    import securepay

    MERCHANT_ID = '...'
    PASSWORD = '...'

    # Take a $2 AUD credit card payment.
    try:
        pay_response = securepay.pay_by_cc(
            200, 'PO-1234', '4444333322221111', '11/18',
            securepay.TEST_API_URL, MERCHANT_ID, PASSWORD, 'J. Citizen')
    except securepay.GatewayError as err:
        # Service unavailable. Log err and give customers a generic error.
    except securepay.PaymentError as err:
        # Payment declined. Error message is in err.
    else:
        # Payment successful! Details in pay_response.


    # Refund the payment above in full.
    try:
        refund_response = securepay.refund(
            200, 'PO-1234', pay_response['transaction_id'],
            securepay.TEST_API_URL, MERCHANT_ID, PASSWORD)
    except securepay.GatewayError as err:
        # Service unavailable. Log err and give customers a generic error.
    except securepay.PaymentError as err:
        # Refund declined. Error message is in err.
    else:
        # Refund successful! Details in refund_response.


To run the tests:

.. code-block:: bash

    $ tox


This module doesn't yet provide credit card authorisation transactions (ie.
putting some money on hold for an upcoming payment). If you're interesting in
funding some work to add these features, please get in touch.
