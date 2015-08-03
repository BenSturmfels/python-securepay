# -*- coding: utf-8; -*-

from __future__ import unicode_literals

import datetime
import textwrap
import unittest

from securepay import pay_by_cc, refund
from securepay.securepay import _pay_by_cc_xml, _refund_xml


class UTCTimezone(datetime.tzinfo):
    """Python 2.7 compatible replacement for datetime.timezone.utc.

    We could just depend on pytz, but I'd prefer not to.

    """
    def dst(self, dt):
        return None

    def utcoffset(self, dt):
        return datetime.timedelta(0)


class PaymentTestCase(unittest.TestCase):
    @unittest.skip("TODO: Mock live gateway for testing.")
    def test_can_make_payment_and_refund(self):
        """Test making a payment for $1 and refunding it.

        Requires valid test gateway API credentials is local_settings.py. If
        you're not connected to the Internet or running against the live gateway
        API, this test will fail. Yes, I realise that's a bit of a pain, but I
        think having some test coverage here trumps the inconvenience caused.

        """
        payment_response = pay_by_cc(
            cents='100',
            purchase_order_id='1234',
            cc_number='4444333322221111',
            cc_expiry='11/22',
            merchant_id='MERCHANT ID',
            password='PASSWORD')
        self.assertEqual(payment_response['approved'], True)

        refund_response = refund(
            cents='100',
            purchase_order_id='1234',
            transaction_id=payment_response['transaction_id'],
            merchant_id='MERCHANT ID',
            password='PASSWORD')
        self.assertEqual(refund_response['approved'], True)


    def test_payment_xml_matches_example(self):
        """Check that the credit card XML output looks correct."""

        # TODO: Given that XML doesn't care about spacing, our test shouldn't
        # either.
        xml = _pay_by_cc_xml(
            timestamp=datetime.datetime(2012, 1, 1, tzinfo=UTCTimezone()),
            cents='100',
            purchase_order_id='1234',
            cc_number='4444333322221111',
            cc_expiry='11/22',
            merchant_id='MERCHANT ID',
            password='PASSWORD',
            cc_holder='Test Person')

        self.assertEqual(
            xml,
            textwrap.dedent("""\
            <?xml version='1.0' encoding='UTF-8'?>
            <SecurePayMessage>
              <MessageInfo>
                <messageID/>
                <messageTimestamp>20120101000000000000+000</messageTimestamp>
                <timeoutValue>60</timeoutValue>
                <apiVersion>xml-4.2</apiVersion>
              </MessageInfo>
              <MerchantInfo>
                <merchantID>MERCHANT ID</merchantID>
                <password>PASSWORD</password>
              </MerchantInfo>
              <RequestType>Payment</RequestType>
              <Payment>
                <TxnList count="1">
                  <Txn ID="1">
                    <txnType>0</txnType>
                    <txnSource>23</txnSource>
                    <amount>100</amount>
                    <currency>AUD</currency>
                    <purchaseOrderNo>1234</purchaseOrderNo>
                    <CreditCardInfo>
                      <cardNumber>4444333322221111</cardNumber>
                      <expiryDate>11/22</expiryDate>
                      <cardHolderName>Test Person</cardHolderName>
                    </CreditCardInfo>
                  </Txn>
                </TxnList>
              </Payment>
            </SecurePayMessage>
            """).encode('utf-8'))

    def test_removes_non_digits_from_cc(self):
        """Check non-digits are stripped from the credit card number."""
        xml = _pay_by_cc_xml(
            timestamp=datetime.datetime(2012, 1, 1, tzinfo=UTCTimezone()),
            cents='100',
            purchase_order_id='1234',
            cc_number='4444 3333x2222-1111',
            cc_expiry='11/22',
            merchant_id='MERCHANT ID',
            password='PASSWORD')

        self.assertIn(b'<cardNumber>4444333322221111</cardNumber>', xml)

    def test_xml_generation_succeeds_when_cc_holder_has_unicode_symbol(self):
        """Check XML is generated when cc_holder contains unicode symbols."""
        xml = _pay_by_cc_xml(
            timestamp=datetime.datetime(2012, 1, 1, tzinfo=UTCTimezone()),
            cents='',
            purchase_order_id='',
            cc_number='',
            cc_expiry='',
            merchant_id='',
            password='',
            cc_holder='♥')
        self.assertIn(b'<cardHolderName>\xe2\x99\xa5</cardHolderName>', xml)


class RefundTestCase(unittest.TestCase):
    def test_refund_xml_matches_example(self):
        """Check that the XML output looks correct."""

        # TODO: Given that XML doesn't care about spacing, our test shouldn't
        # either.
        xml = _refund_xml(
            timestamp=datetime.datetime(2012, 1, 1, tzinfo=UTCTimezone()),
            cents='100',
            purchase_order_id='1234',
            transaction_id=4321,
            merchant_id='MERCHANT ID',
            password='PASSWORD',
        )

        self.assertEqual(
            xml,
            textwrap.dedent("""\
            <?xml version='1.0' encoding='UTF-8'?>
            <SecurePayMessage>
              <MessageInfo>
                <messageID/>
                <messageTimestamp>20120101000000000000+000</messageTimestamp>
                <timeoutValue>60</timeoutValue>
                <apiVersion>xml-4.2</apiVersion>
              </MessageInfo>
              <MerchantInfo>
                <merchantID>MERCHANT ID</merchantID>
                <password>PASSWORD</password>
              </MerchantInfo>
              <RequestType>Payment</RequestType>
              <Payment>
                <TxnList count="1">
                  <Txn ID="1">
                    <txnType>4</txnType>
                    <txnSource>23</txnSource>
                    <amount>100</amount>
                    <purchaseOrderNo>1234</purchaseOrderNo>
                    <txnID>4321</txnID>
                  </Txn>
                </TxnList>
              </Payment>
            </SecurePayMessage>
            """).encode('utf-8'))


if __name__ == '__main__':
    unittest.main()
