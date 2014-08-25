"""Process and refund payments through the SecurePay payment gateway.

Both pay_by_cc and refund take a "purchase_order_id". This represents the
business's identifier for the transaction, such as the invoice number. If
you're making a refund, the "purchase_order_id" must be the same as the
original payment.

Both pay_by_cc and refund return a dictionary of:
 - approved: boolean as to whether transaction was approved
 - bank_response_code: numeric bank response code
 - bank_response_text: textual response from bank
 - transaction_id: bank's identifier for transaction

When checking the response, if "approved" is True, you're done. Otherwise,
tell the user their transaction failed and display "bank_response_text".

Store the "transaction_id" of payments so you can make a refund or look up
the transaction later on.

For testing credentials, see the local_settings.py.template.

NOTE: The testing gateway only approves payments amounts ending in 00, 08 or 77
(for ANZ). All other amounts will trigger the bank response code indicated by
that number (see response codes document). This is not documented in the
Integration Guide.

SecurePay support advised:

    Use Visa card number 4444333322221111, and a valid expiry date
    (E.g. 10/08) to initiate test payments.

    The amount processed when testing dictates the transaction
    response:

    Approved: Amounts ending with 00, 08 (and 77 for ANZ).

    For example, $1.00. $12.08 are approved.

    Declined: Amounts ending in all other two digit combinations will
    be declined with the matching bank codes (01-07, 09-76, 78-99).

SecurePay documentation is here:
http://www.securepay.com.au/resources/Secure_XML_API_Integration_Guide.pdf
http://www.securepay.com.au/resources/SecurePay_Response_Codes.pdf

"""
# TODO:
#
# Allow multi-currency, not hard-coded to AUD.
#
# Validate the XML produced.
# http://stackoverflow.com/questions/15798/how-do-i-validate-xml-against-a-dtd-file-in-python
#
# Separate out the custom timestamp code.
#
# Add pre-auth.

import datetime
import logging
import re
import time
import urllib

from lxml import etree
from lxml.builder import E
import pytz

API_URL_TESTING = 'https://test.securepay.com.au/xmlapi/payment'
API_URL_LIVE = 'https://api.securepay.com.au/xmlapi/payment'

TIMEOUT = "60"
APIVERSION = "xml-4.2"
REQUESTTYPE = "Payment"
TXNTYPE_PAYMENT = "0"
TXNTYPE_REFUND = "4"
TXNSOURCE_SECURE_XML = "23"
CURRENCY = "XXX" # amount is specified in cents
GATEWAY_STATUS_CODE_NORMAL = '000'

log = logging.getLogger(__name__)

def pay_by_cc(cents, purchase_order_id, cc_number, cc_expiry,
              merchant_id, password, cc_holder='', live=False):
    """Process a credit card payment through SecurePay.

    Parameter and return value are described in module documentation.

    """
    # TODO: Should probably just take a decimal.Decimal for the payment amount.
    # Cents isn't user-friendly.

    timestamp = datetime.datetime.now(tz=pytz.timezone('UTC'))
    request_xml = _pay_by_cc_xml(
        timestamp, cents, purchase_order_id, cc_number, cc_expiry, merchant_id,
        password, cc_holder)
    api_url = API_URL_LIVE if live else API_URL_TESTING
    response_xml = urllib.urlopen(api_url, request_xml).read()
    response = _parse_response(response_xml)
    log.debug(response)
    return response


def _pay_by_cc_xml(timestamp, cents, purchase_order_id, cc_number,
                   cc_expiry, merchant_id, password, cc_holder=''):
    """Generate XML for a SecurePay payment."""

    timestamp = '%s%+04.f' % (timestamp.strftime("%Y%d%m%H%M%S000000"),
                              timestamp.utcoffset().total_seconds() / 60)

    # Credit card numbers with non-digits are ok; just strip them out.
    cc_number = ''.join([i for i in cc_number if i.isdigit()])

    message = (
        E.SecurePayMessage(
            E.MessageInfo(
                E.messageID(),
                E.messageTimestamp(timestamp),
                E.timeoutValue(TIMEOUT),
                E.apiVersion(APIVERSION)),
            E.MerchantInfo(
                E.merchantID(merchant_id),
                E.password(password)),
            E.RequestType(REQUESTTYPE),
            E.Payment(
                E.TxnList(
                    E.Txn(
                        E.txnType(TXNTYPE_PAYMENT),
                        E.txnSource(TXNSOURCE_SECURE_XML),
                        E.amount(cents),
                        E.currency(CURRENCY),
                        E.purchaseOrderNo(purchase_order_id),
                        E.CreditCardInfo(
                            E.cardNumber(cc_number),
                            E.expiryDate(cc_expiry),
                            E.cardHolderName(cc_holder)),
                        ID="1"),
                    count="1"))))

    xml = etree.tostring(
        message, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    log.debug(
        # Mask out credit card number. Logging the full numbers in a live system
        # would be a security risk.
        re.sub(
            r'<cardNumber>(\d{6})\d{7}(\d{3})</cardNumber>',
            r'<cardNumber>\1...\2</cardNumber>',
            xml))
    return xml


def refund(cents, purchase_order_id, transaction_id,
           merchant_id, password, live=False):
    """Process a credit card payment through SecurePay.

    Parameter and return values are described in module documentation.

    """
    # TODO: Should probably just take a decimal.Decimal for the payment amount.
    # Cents isn't user-friendly.

    timestamp = datetime.datetime.now(tz=pytz.timezone('UTC'))
    request_xml = _refund_xml(
        timestamp, cents, purchase_order_id, transaction_id, merchant_id,
        password)
    api_url = API_URL_LIVE if live else API_URL_TESTING
    response_xml = urllib.urlopen(api_url, request_xml).read()
    response = _parse_response(response_xml)
    log.debug(response)
    return response


def _refund_xml(timestamp, cents, purchase_order_id, transaction_id,
                 merchant_id, password):
    """Generate XML for a SecurePay refund request."""

    # The SecurePay documentation is ambiguous as to whether the timezone is
    # zero padded or not. We'll assume it is.
    timestamp = '%s%+04.f' % (timestamp.strftime("%Y%d%m%H%M%S000000"),
                              timestamp.utcoffset().total_seconds() / 60)

    message = (
        E.SecurePayMessage(
            E.MessageInfo(
                E.messageID(),
                E.messageTimestamp(timestamp),
                E.timeoutValue(TIMEOUT),
                E.apiVersion(APIVERSION)),
            E.MerchantInfo(
                E.merchantID(merchant_id),
                E.password(password)),
            E.RequestType(REQUESTTYPE),
            E.Payment(
                E.TxnList(
                    E.Txn(
                        E.txnType(TXNTYPE_REFUND),
                        E.txnSource(TXNSOURCE_SECURE_XML),
                        E.amount(cents),
                        E.purchaseOrderNo(purchase_order_id),
                        E.txnID(transaction_id),
                        ID="1"),
                    count="1"))))

    xml = etree.tostring(
        message, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    log.debug(xml)
    return xml



def _parse_response(response_xml):
    """Parse the response from SecurePay web service."""
    try:
        response = etree.XML(response_xml)
    except etree.XMLSyntaxError:
        raise Exception(
            "XML syntax error in response from payment gateway. "
            "Here's the first 500 characters:\n%s" % response_xml[:500])
    gateway_status_code = response.xpath('.//statusCode')[0].text
    gateway_status_description = response.xpath('.//statusDescription')[0].text
    if gateway_status_code == GATEWAY_STATUS_CODE_NORMAL:
        response_dict = {
            'approved': response.xpath('.//approved')[0].text == 'Yes',
            'bank_response_code': response.xpath('.//responseCode')[0].text,
            'bank_response_text': response.xpath('.//responseText')[0].text,
            'transaction_id': response.xpath('.//txnID')[0].text}
    else:
        raise Exception("Payment gateway error %s: %s."
                        % (gateway_status_code, gateway_status_description))
    log.debug(etree.tostring(response, pretty_print=True))
    return response_dict
