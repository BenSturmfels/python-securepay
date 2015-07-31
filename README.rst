==================
 Python Securepay
==================

`securepay` is a Python interface to the Securepay credit card payment gateway.


Quickstart
-----------

This package can be used as follows:

.. code-block:: python

    import securepay

    SECUREPAY_API_URL= 'https://test.securepay.com.au/xmlapi/payment'
    SECUREPAY_MERCHANT_ID = '...'
    SECUREPAY_PASSWORD = '...'

    # Take a credit card payment.
    try:
        response = securepay.pay_by_cc(
            cents, purchase_order_id, cc_number, cc_expiry,
            SECUREPAY_API_URL, SECUREPAY_MERCHANT_ID,
            SECUREPAY_PASSWORD, cc_card_name)
    except securepay.GatewayError as err:
        # Service unavailable. Give customers a generic error.
    except securepay.PaymentError as err:
        # Payment declined. Error message is in err.
    else:
        # Payment successful! Details in response.


    # Refund the payment.
    try:
        response = securepay.refund(
            cents, purchase_order_id, transaction_ref, SECUREPAY_API_URL,
            SECUREPAY_MERCHANT_ID, SECUREPAY_PASSWORD)
    except securepay.GatewayError as err:
        # Service unavailable. Give customers a generic error.
    except securepay.PaymentError as err:
        # Refund declined. Error message is in err.
    else:
        # Refund successful! Details in response.


This module doesn't yet provide credit card authorisation transactions (ie.
putting some money on hold for an upcoming payment). If you're interesting in
funding some work to add these features, please get in touch.
