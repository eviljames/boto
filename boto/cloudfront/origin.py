# Copyright (c) 2006-2010 Mitch Garnaat http://garnaat.org/
# Copyright (c) 2010, Eucalyptus Systems, Inc.
# Copyright (c) 2012, James Purdy <james@eviljames.ca>
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

from identity import OriginAccessIdentity
import uuid

# DEPRECATED
def get_oai_value(origin_access_identity):
    if isinstance(origin_access_identity, OriginAccessIdentity):
        return origin_access_identity.uri()
    else:
        return origin_access_identity
                
class S3Origin(object):
    """
    Origin information to associate with the distribution.
    If your distribution will use an Amazon S3 origin,
    then you use the S3Origin element.
    
    Note: This is for use ONLY with Streaming Distributions. for Download
    Distributions, providing this object will convert it to a CFOrigin object.
    """

    def __init__(self, dns_name=None, origin_access_identity=None):
        """
        :param dns_name: The DNS name of your Amazon S3 bucket to
                         associate with the distribution.
                         For example: mybucket.s3.amazonaws.com.
        :type dns_name: str
        
        :param origin_access_identity: The CloudFront origin access
                                       identity to associate with the
                                       distribution. If you want the
                                       distribution to serve private content,
                                       include this element; if you want the
                                       distribution to serve public content,
                                       remove this element.
        :type origin_access_identity: str
        
        """
        self.dns_name = dns_name
        self.origin_access_identity = origin_access_identity

    def __repr__(self):
        return '<S3Origin: %s>' % self.dns_name

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'DNSName':
            self.dns_name = value
        elif name == 'OriginAccessIdentity':
            self.origin_access_identity = value
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = '  <S3Origin>\n'
        s += '    <DNSName>%s</DNSName>\n' % self.dns_name
        if self.origin_access_identity:
            val = get_oai_value(self.origin_access_identity)
            s += '    <OriginAccessIdentity>%s</OriginAccessIdentity>\n' % val
        s += '  </S3Origin>\n'
        return s
    
    def to_config(self):
        return CFOrigin(self.dns_name, s3_oai=self.origin_access_identity)
    
class CustomOrigin(object):
    """
    Origin information to associate with the distribution.
    If your distribution will use a non-Amazon S3 origin,
    then you use the CustomOrigin element.  DEPRECATED
    """

    def __init__(self, dns_name=None, http_port=80, https_port=443,
                 origin_protocol_policy=None):
        """
        :param dns_name: The DNS name of your Amazon S3 bucket to
                         associate with the distribution.
                         For example: mybucket.s3.amazonaws.com.
        :type dns_name: str
        
        :param http_port: The HTTP port the custom origin listens on.
        :type http_port: int
        
        :param https_port: The HTTPS port the custom origin listens on.
        :type http_port: int
        
        :param origin_protocol_policy: The origin protocol policy to
                                       apply to your origin. If you
                                       specify http-only, CloudFront
                                       will use HTTP only to access the origin.
                                       If you specify match-viewer, CloudFront
                                       will fetch from your origin using HTTP
                                       or HTTPS, based on the protocol of the
                                       viewer request.
        :type origin_protocol_policy: str
        
        """
        self.dns_name = dns_name
        self.http_port = http_port
        self.https_port = https_port
        self.origin_protocol_policy = origin_protocol_policy

    def __repr__(self):
        return '<CustomOrigin: %s>' % self.dns_name

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'DNSName':
            self.dns_name = value
        elif name == 'HTTPPort':
            try:
                self.http_port = int(value)
            except ValueError:
                self.http_port = value
        elif name == 'HTTPSPort':
            try:
                self.https_port = int(value)
            except ValueError:
                self.https_port = value
        elif name == 'OriginProtocolPolicy':
            self.origin_protocol_policy = value
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = '  <CustomOrigin>\n'
        s += '    <DNSName>%s</DNSName>\n' % self.dns_name
        s += '    <HTTPPort>%d</HTTPPort>\n' % self.http_port
        s += '    <HTTPSPort>%d</HTTPSPort>\n' % self.https_port
        s += '    <OriginProtocolPolicy>%s</OriginProtocolPolicy>\n' % self.origin_protocol_policy
        s += '  </CustomOrigin>\n'
        return s
    
    def to_config(self):
        return CFOrigin(self.dns_name, http_port=self.http_port,
                        https_port=self.https_port,
                        origin_protocol_policy=self.origin_protocol_policy)

class S3OriginConfig(object):
    def __init__(self, origin_access_identity=None):
        """
        :param origin_access_identity: The Origin Access Identity for an s3
                                       Origin.
        :type origin_access_identity: :class`boto.cloudfront.identity.OriginAccessIdentity
        """
        self.origin_access_identity = origin_access_identity
    
    def startElement(self, name, attrs, connection):
        return None
    
    def endElement(self, name, value, connection):
        if name == 'OriginAccessIdentity':
            self.origin_access_identity = value
    
    def to_xml(self):
        if self.origin_access_identity:
            s = '  <S3OriginConfig>\n'
            if isinstance(self.origin_access_identity, OriginAccessIdentity):
                oai = self.origin_access_identity.uri()
            else:
                oai = 'origin-access-identity/cloudfront/%s' % self.origin_access_identity
            s += '    <OriginAccessIdentity>%s</OriginAccessIdentity>' % oai
            s += '  </S3OriginConfig>\n'
        else:
            s = '  <S3OriginConfig>\n'
            s += '    <OriginAccessIdentity></OriginAccessIdentity>\n'
            s += '  </S3OriginConfig>\n'
        return s

class CustomOriginConfig(object):
    def __init__(self, http_port=80, https_port=443,
                 origin_protocol_policy='match-viewer'):
        """
        :param http_port: The HTTP Port to use for a Custom Origin
        :type http_port: int
        
        :param https_port: The HTTPS port to use for a Custom Origin
        :type https_port: int
        
        :param origin_protocol_policy: The protocol you want CloudFront to use
                                       when accessing your CustomOrigin server.
                                       Values: 'http-only'|'match-viewer'
        :type origin_protocol_policy: str

        """
        self.http_port = http_port
        self.https_port = https_port
        self.origin_protocol_policy = origin_protocol_policy
    
    def startElement(self, name, attrs, connection):
        return None
    
    def endElement(self, name, value, connection):
        if name == 'HTTPPort':
            try:
                self.http_port = int(value)
            except ValueError:
                self.http_port = value
        elif name == 'HTTPSPort':
            try:
                self.https_port = int(value)
            except ValueError:
                self.https_port = value
        elif name == 'OriginProtocolPolicy':
            self.origin_protocol_policy = value
    
    def to_xml(self):
        s = '<CustomOriginConfig>\n'
        if self.http_port:
            s += '  <HTTPPort>%d</HTTPPort>' % self.http_port
        if self.https_port:
            s += '  <HTTPSPort>%d</HTTPSPort>' % self.https_port
        opp = self.origin_protocol_policy
        s += '  <OriginProtocolPolicy>%s</OriginProtocolPolicy>\n' % opp
        s += '</CustomOriginConfig>\n'
        return s

class CFOrigin(object):
    """
    With CloudFront moving to multiple origins, a generic Origin descriptor is
    required.
    """
    def __init__(self, domain_name='', origin_id=None, config=None,
                 s3_oai=None, http_port=80, https_port=443,
                 origin_protocol_policy='match-viewer'):
        """
        :param domain_name: The domain name of the origin server.  For S3
                            Origins, this should be in the format:
                            bucket.s3.amazonaws.com
        :type domain_name: str
        
        :param origin_id: A unique identifier used to reference this Origin by
                          CacheBehavior objects.
        :type origin_id: str
        
        :param config: A S3OriginConfig or CustomOriginConfig object
                       representing this Origin's configuration.  Named
                       parameters can be used to construct an Origin Config in
                       lieu of this object.
        :type config: :class`boto.cloudfront.origin.S3OriginConfig` or
                      :class`boto.cloudfront.origin.CustomOriginConfig`
        
        :param s3_oai: The Origin Access Identity for an s3 Origin.
        :type s3_oai: :class`boto.cloudfront.identity.OriginAccessIdentity
        
        :param http_port: The HTTP Port to use for a Custom Origin
        :type http_port: int
        
        :param https_port: The HTTPS port to use for a Custom Origin
        :type https_port: int
        
        :param origin_protocol_policy: The protocol you want CloudFront to use
                                       when accessing your CustomOrigin server.
                                       Values: 'http-only'|'match-viewer'
        :type origin_protocol_policy: str
        """
        self.domain_name = domain_name
        if origin_id:
            self.origin_id = origin_id
        else:
            self.origin_id = str(uuid.uuid4())
        if not config:
            if 's3.amazonaws.com' in self.domain_name:
                self.config = S3OriginConfig(s3_oai)
            else:
                self.config = CustomOriginConfig(http_port, https_port,
                                                 origin_protocol_policy)
        else:
            self.config = config
    
    def __repr__(self):
        return "<CFOrigin: %s>" % self.domain_name
    
    def startElement(self, name, attrs, connection):
        if name == 'S3OriginConfig':
            self.config = S3OriginConfig()
            return self.config
        elif name == 'CustomOriginConfig':
            self.config = CustomOriginConfig()
            return self.config
    
    def endElement(self, name, value, connection):
        if name == 'Id':
            self.origin_id = value
        elif name == 'DomainName':
            self.domain_name = value
    
    def to_xml(self):
        s = '<Origin>\n'
        s += '  <Id>%s</Id>\n' % self.origin_id
        s += '  <DomainName>%s</DomainName>\n' % self.domain_name
        s += self.config.to_xml()
        s += '</Origin>\n'
        return s

class CFOrigins(list):
    """
    A list object to manage many origins, the append_origin method accepts many
    ways to build an Origin.  The origin parameter may be any of: str, S3Origin,
    CustomOrigin, CFOrigin or CFOrigins and may be a list thereof. If the origin
    parameter is None, and domain_name is specified, all the other parameters
    are passed forward into the CFOrigin object.
    """
    def append_origin(self, origin=None, domain_name='', origin_id=None,
                      config=None, s3_oai=None, http_port=80, https_port=443,
                      origin_protocol_policy='match-viewer'):
        """
        :param origin: The origin parameter may be any of: str, S3Origin,
                       CustomOrigin, CFOrigin or CFOrigins and may be a list
                       thereof. If the origin parameter is None, and domain_name
                       is specified, all the other parameters are passed forward
                       into the CFOrigin object.
        :type origin: :class`boto.cloudfront.origin.CFOrigins` or
                      :class`boto.cloudfront.origin.CFOrigin` or
                      :class`boto.cloudfront.origin.CustomOrigin` or
                      :class`boto.cloudfront.origin.S3Origin` or
                      str or
                      list of any combination of the above.
        
        :param domain_name: The domain name of the origin server.  For S3
                            Origins, this should be in the format:
                            bucket.s3.amazonaws.com
        :type domain_name: str
        
        :param origin_id: A unique identifier used to reference this Origin by
                          CacheBehavior objects.
        :type origin_id: str
        
        :param config: A S3OriginConfig or CustomOriginConfig object
                       representing this Origin's configuration.  Named
                       parameters can be used to construct an Origin Config in
                       lieu of this object.
        :type config: :class`boto.cloudfront.origin.S3OriginConfig` or
                      :class`boto.cloudfront.origin.CustomOriginConfig`
        
        :param s3_oai: The Origin Access Identity for an s3 Origin.
        :type s3_oai: :class`boto.cloudfront.identity.OriginAccessIdentity
        
        :param http_port: The HTTP Port to use for a Custom Origin
        :type http_port: int
        
        :param https_port: The HTTPS port to use for a Custom Origin
        :type https_port: int
        
        :param origin_protocol_policy: The protocol you want CloudFront to use
                                       when accessing your CustomOrigin server.
                                       Values: 'http-only'|'match-viewer'
        :type origin_protocol_policy: str
        """
        if isinstance(origin, (S3Origin, CustomOrigin)):
            self.append(origin.to_config())
        elif isinstance(origin, (CFOrigins, list)):
            for o in origin:
                self.append_origin(o)
        elif isinstance(origin, CFOrigin):
            self.append(origin)
        elif isinstance(origin, str):
            self.append(CFOrigin(origin))
        elif domain_name:
            self.append(CFOrigin(domain_name=domain_name, origin_id=origin_id,
                                 config=config, s3_oai=s3_oai,
                                 http_port=http_port, https_port=https_port,
                                 origin_protocol_policy=origin_protocol_policy))
    def to_xml(self):
        s = '<Origins>\n'
        s += '  <Quantity>%d</Quantity>' % len(self)
        s += '  <Items>\n'
        for o in self:
            s += o.to_xml()
        s += '  </Items>\n'
        s += '</Origins>\n'
        return s
    def startElement(self, name, attrs, connection):
        if name == 'Origin':
            o = CFOrigin()
            self.append(o)
            return o
    def endElement(self, name, value, connection):
        pass
    