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

class Error(Exception):
    pass


class ConfigurationException(Error):
    pass


class ValidationException(Error):
    pass

# define a superclass BeanstreamApiException
# Author: Haggai Liu

class BeanstreamApiException(Error):
   pass

def getMappedException(httpstatuscode):
   code=str(httpstatuscode)
   if code=='302':
      return RedirectionError
   if code[0]=='4':
      code=code[1:]
      if code in ['00','05','15']:
         return InvalidRequestException
      if code[0]=='0':
         code=code[1:]
         error_dict={
            '1':UnAuthorizedException,
            '2':BusinessRuleException,
            '3':ForbiddenException
            }
         if code in error_dict:
            return error_dict[code]
   return InternalServerException



class RedirectionException(Error):#HTTP status code 302
    pass

class InvalidRequestException(Error):#HTTP status code 400,405,415
    pass

class UnAuthorizedException(Error):#HTTP status code 401
    pass

class BusinessRuleException(Error):#HTTP status code 402
    pass

class ForbiddenException(Error):#HTTP status code 403
    pass
 
class InternalServerException(Error):#default
   pass


