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



class RedirectionException(Error):
    pass

class InvalidRequestException(Error):
    pass

class UnAuthorizedException(Error):
    pass

class BusinessRuleException(Error):
    pass

class ForbiddenException(Error):
    pass

class InvalidRequestException(Error):
    pass
 
class InternalServerException(Error):
   pass


