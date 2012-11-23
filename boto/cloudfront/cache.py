# Copyright (c) 2012 James Purdy <james@eviljames.ca>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from boto.cloudfront.signers import TrustedSigners

class CacheBehavior(object):
    """
    An object to lay out cache behaviors.
    """
    
    def __init__(self, pattern=None, target_origin_id=None,
                 forwarded_values=None, trusted_signers=None,
                 viewer_protocol_policy='allow-all', min_ttl=3600):
        """
        :param pattern: The pattern that specifies which requests you want this
                        cache behavior to apply to.  When CloudFront receives an
                        end-user request, the requested path is compared with
                        path patterns in the order in which cache behaviors are
                        listed in the distribution.  Leave blank to specify the default
                        cache behavior, otherwise specify a pattern
                        ie: '/images/*.jpg'
        :type pattern: str
        
        :param target_origin_id: Which origin of the distribution's defined
                                 origins should the Behavior apply to.  Required
        :type target_origin_id: str
        
        :param trusted_signers: A TrustedSigners object that defines what AWS
                                account numbers may sign against this
                                distribution
        :type trusted_signers: :class`boto.cloudfront.signers.TrustedSigners`
        
        :param viewer_protocol_policy: Used to specify the protocol that users
                                       can use to access the files in the origin
                                       and path pattern match.
                                       Values: 'allow-all' | 'https'
        :type viewer_protocol_policy: str
        
        :param min_ttl: The minimum amount of time that you want objects to stay
                        in CloudFront before the origin is checked for an update
        :type min_ttl: int
        """
        self.pattern = pattern
        self.target_origin_id = target_origin_id
        if forwarded_values:
            self.forwarded_values = forwarded_values
        else:
            self.forwarded_values = ForwardedValues()
        
        if trusted_signers:
            self.trusted_signers = trusted_signers
        else:
            self.trusted_signers = TrustedSigners()
        self.viewer_protocol_policy = viewer_protocol_policy
        self.min_ttl = min_ttl
    
    def startElement(self, name, attrs, connection):
        if name == 'TrustedSigners':
            self.trusted_signers = TrustedSigners()
            return self.trusted_signers
        if name == 'ForwardedValues':
            self.forwarded_values = ForwardedValues()
            return self.forwarded_values
    
    def endElement(self, name, value, connection):
        if name == 'PathPattern' and self.pattern != 'Default':
            self.pattern = value
        elif name == 'TargetOriginId':
            self.target_origin_id = value
        elif name == 'ViewerProtocolPolicy':
            self.viewer_protocol_policy = value
        elif name == 'MinTTL':
            self.min_ttl = value
    
    def to_xml(self):
        if not self.pattern:
            s = '  <DefaultCacheBehavior>'
        else:
            s = '  <CacheBehavior>\n'
            s += '    <PathPattern>%s</PathPattern>' % self.pattern
        if self.target_origin_id:
            s += '    <TargetOriginId>%s</TargetOriginId>\n' % self.target_origin_id
        if self.forwarded_values:
            s += self.forwarded_values.to_xml()
        s += '    <TrustedSigners>\n'
        if self.trusted_signers:
            s += '      <Enabled>true</Enabled>\n'
            s += '      <Quantity>%d</Quantity>\n' % len(self.trusted_signers)
            s += '      <Items>\n'
            for signer in self.trusted_signers:
                s += '        <AWSAccountNumber>%s</AWSAccountNumber>\n' % signer
            s += '      </Items>\n'
        else:
            s += '      <Enabled>false</Enabled>\n'
            s+=  '      <Quantity>0</Quantity>\n'
        s += '    </TrustedSigners>\n'
        s += '<ViewerProtocolPolicy>%s</ViewerProtocolPolicy>\n' % self.viewer_protocol_policy
        s += '<MinTTL>%d</MinTTL>\n' % self.min_ttl
        if not self.pattern:
            s += '  </DefaultCacheBehavior>\n'
        else:
            s += '</CacheBehavior>\n'
        return s

class ForwardedValues(object):
    """
    Forwarded Values as a part of the CacheBehavior definition
    """
    
    def __init__(self, query_string=False, cookies='none',
                 whitelisted_names=None):
        """
        :param query_string: Whether or not query string should be passed to the
                             origin server.
        :type query_string: boolean
        
        :param cookies: Whether or not cookies should be passed forward to the
                        origin server.  Optionally, you may specify a whitelist
                        of cookies to pass forward, while denying all others.
                        Valid values: 'all' | 'none' | 'whitelist'
        :type cookies: str
        
        :param whitelisted_names: Required when cookies is 'whitelist', a list
                                  of cookies that get passed forward to the
                                  origin server
        :type whitelisted_names: :class`boto.cloudfront.cache.WhitelistedNames
        """
        self.query_string = query_string
        self.cookies = cookies
        if whitelisted_names:
            self.whitelisted_names = whitelisted_names
        
    def startElement(self, name, attrs, connection):
        if name == 'WhitelistedNames':
            self.whitelisted_names = WhitelistedNames()
            return self.whitelisted_names
    
    def endElement(self, name, value, connection):
        if name == 'QueryString':
            if value.lower() == 'true':
                self.query_string = True
            else:
                self.query_string = False
        elif name == 'Forward':
            self.cookies = value
    
    def to_xml(self):
        s = '  <ForwardedValues>\n'
        s += '    <QueryString>'
        if self.query_string:
            s += 'true'
        else:
            s += 'false'
        s += '</QueryString>\n'
        s += '    <Cookies>\n'
        s += '      <Forward>%s</Forward>\n' % self.cookies
        if self.cookies is 'whitelist':
            self.whitelisted_names.to_xml()
        s += '    </Cookies>\n'
        s += '  </ForwardedValues>\n'
        return s

class WhitelistedNames(list):
    def startElement(self, name, attrs, connection):
        return None
    
    def endElement(self, name, value, connection):
        if name == 'Name':
            self.append(value)
    
    def to_xml():
        s += '      <WhitelistedNames>\n'
        s += '        <Quantity>%d</Quantity>\n' % len(self)
        s += '        <Items>\n'
        for name in self:
            s += '          <Name>%s</Name>\n' % name
        s += '        </Items>\n'
        s += '      </WhitelistedNames>\n'