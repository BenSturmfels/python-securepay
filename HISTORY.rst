Release History
---------------

Unreleased
++++++++++

**Improvements**

 - Add GitLab continuous integration script to run tox tests.


0.6.0 (2016-10-29)
++++++++++++++++++

**Improvements**

 - Add the optional ``recurring`` field to payment requests (Greg McCoy). Note:
   This does not automate transaction processing. See the ``pay_by_cc`` function
   docstring and SecurePay docs for details.


0.5.7 (2015-08-03)
++++++++++++++++++

**Improvements**

 - Add ``securepay.LIVE_API_URL`` and ``securepay.TEST_API_URL`` so you don't
   have to define them yourself.


0.5.6 (2015-08-03)
++++++++++++++++++

**Bug fixes**

 - Fixed support for Python 2.7.
 - Enabled tests for Python 2.7, 3.3 and 3.4 with Tox
