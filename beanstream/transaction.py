'''
Copyright 2012 Upverter Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import decimal
import hashlib
import logging
import random
import string
import base64
import urllib
from urllib.request import urlopen
from urllib.parse import urlencode
import time

from beanstream import errors
from beanstream.response_codes import response_codes

log = logging.getLogger('beanstream.transaction')


class Transaction(object):

    URLS = {
        'process_transaction'   : 'https://www.beanstream.com/scripts/process_transaction.asp',
        'recurring_billing'     : 'https://www.beanstream.com/scripts/recurring_billing.asp',
        'payment_profile'       : 'https://www.beanstream.com/scripts/payment_profile.asp',
        'report_download'       : 'https://www.beanstream.com/scripts/report_download.asp',
        'report'                : 'https://www.beanstream.com/scripts/report.aspx',
    }

    TRN_TYPES = {
        'preauth': 'PA',
        'preauth_completion': 'PAC',
        'purchase': 'P',
        'return': 'R',
        'void': 'V',
        'void_purchase': 'VP',
        'void_return': 'VR',
    }


    def __init__(self, beanstream):
        self.beanstream = beanstream
        self.response_class = Response

        self.params = {}

        self._generate_order_number()
        self.params['trnOrderNumber'] = self.order_number
        self.response_params = []

    def validate(self):
        pass

    def commit(self):
        self.validate()

        # hashing is applicable only to requests sent to the process
        # transaction API.
        data = urlencode(self.params)
        '''if self.beanstream.HASH_VALIDATION and self.url == self.URLS['process_transaction']:
            if self.beanstream.hash_algorithm == 'MD5':
                hashobj = hashlib.md5()
            elif self.beanstream.hash_algorithm == 'SHA1':
                hashobj = hashlib.sha1()
            else:
                log.error('Hash method %s is not MD5 or SHA1', self.beanstream.hash_algorithm)
                raise errors.ConfigurationException('Hash method must be MD5 or SHA1')
            hashobj.update(data + urlencode({'hashValue' : self.beanstream.hashcode}))
            hash_value = hashobj.hexdigest()
            data += '&hashValue=%s' % hash_value
        '''

        # do switch statement for which passcode to use
        apicode = None
        if (self.url == self.URLS['process_transaction']):
            apicode = self.beanstream.payment_passcode
        elif (self.url == self.URLS['recurring_billing']):
            apicode = self.beanstream.recurring_billing_passcode
        elif (self.url == self.URLS['payment_profile']):
            apicode = self.beanstream.payment_profile_passcode
        else:
            apicode = self.beanstream.reporting_passcode

        if (apicode is None):
            log.error('No API Passcode specified for url %s', self.url)
            return False
        
        auth = base64.b64encode( (str(self.beanstream.merchant_id)+':'+apicode).encode('utf-8') )
        passcode = 'Passcode '+str(auth.decode('utf-8'))
        print("passcode: "+passcode)
        print('Sending.... '+data)
        log.debug('Sending to %s: %s', self.url, data)
        
        request = urllib.request.Request(self.url)
        request.add_header('Authorization', passcode)
        res = urlopen(request, bytes(data, 'utf-8'))
			
        if res.code != 200:
            log.error('response code not OK: %s', res.code)
            return errors.getMappedException(res.code)

        
        body = res.read()
        body = body.decode('utf-8')
		
        if body == 'Empty hash value':
            log.error('hash validation required')
            return False

        response = self.parse_raw_response(body)
        log.debug('Beanstream response: %s', body)
        log.debug(response)

        return self.response_class(response, *self.response_params)

    def parse_raw_response(self, body):
        return urllib.parse.parse_qs(body)

    def _generate_order_number(self):
        """ Generate a random 10-digit alphanumeric string prefixed with a timestamp.
        """
        t = str(time.time())
        n = str(random.randint(0, 1000))
        self.order_number = t+n

    def _process_amount(self, amount):
        decimal_amount = decimal.Decimal(amount)
        return str(decimal_amount.quantize(decimal.Decimal('1.00')))

    def set_card(self, card):
        if self.beanstream.REQUIRE_CVD and not card.has_cvd():
            log.error('CVD required')
            raise errors.ValidationException('CVD required')

        self.params.update(card.params())
        self.has_credit_card = True

    def set_billing_address(self, address):
        self.params.update(address.params('ord'))
        self.has_billing_address = True

    def set_refs(self, refs):
        if len(refs) > 5:
            raise errors.ValidationException('too many ref fields')

        for ref_idx, ref in enumerate(refs, start=1):
            if ref:
                self.params['ref%s' % ref_idx] = ref


class Response(object):

    def __init__(self, resp_dict):
        self.resp = resp_dict

    def __repr__(self):
        return '%s(%s)' % (self.__class__, self.resp)

    def __str__(self):
        return '%s <transaction_id: %s, order_number: %s>' % (self.__class__, self.transaction_id(), self.order_number())

    def order_number(self):
        ''' Order number assigned in the transaction request. '''
        return self.resp.get('trnOrderNumber', [None])[0]

    def transaction_id(self):
        ''' Beanstream transaction identifier '''
        return self.resp.get('trnId', [None])[0]

    def refs(self):
        return [
            self.resp.get('ref1', [None])[0],
            self.resp.get('ref2', [None])[0],
            self.resp.get('ref3', [None])[0],
            self.resp.get('ref4', [None])[0],
            self.resp.get('ref5', [None])[0],
        ]

