import requests
from collections import OrderedDict
from simple_salesforce import Salesforce
import sys
num_conditions = int(sys.argv[1])
sf = Salesforce(security_token=SECURITY_TOKEN , username=USERNAME, password=PASSWORD, sandbox=False)
soap_url = 'https://zendesk.my.salesforce.com/services/Soap/u/38.0'
conds = ['Probability >= {}'.format(i) for i in range(-100,-100 + num_conditions,1)]
where_clause = 'WHERE {} LIMIT 2'.format(' AND '.join(conds))
opp_fields = sf.Opportunity.describe()['fields']
field_types = OrderedDict({f['name']: f['soapType'] for f in opp_fields})
query_str = 'SELECT {} FROM Opportunity {}'.format(','.join(field_types.keys()), where_clause)
soap_url = 'https://zendesk.my.salesforce.com/services/Soap/u/38.0'
soap_message_body = """
<soapenv:Envelope
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:urn="urn:partner.soap.sforce.com"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <soapenv:Header>
        <urn:SessionHeader>
            <urn:sessionId>{session_id}</urn:sessionId>
        </urn:SessionHeader>
    </soapenv:Header>
    <soapenv:Body>
        <urn:query>
            <urn:queryString>{query}</urn:queryString>
        </urn:query>
    </soapenv:Body>
</soapenv:Envelope>""".format(session_id=sf.session_id, query=query_str)
soap_request_headers = {
        'content-type': 'text/xml',
        'charset': 'UTF-8',
        'SOAPAction': 'query'
    }
print("query length is {}".format(len(query_str)))
print("sending SOAP request")
soap_response=requests.post(soap_url, soap_message_body, headers=soap_request_headers)
print("SOAP returned with HTTP status code {} and response text length (XML) of {}".format(soap_response.status_code, len(soap_response.text)))
print("sending REST request")
rest_records = sf.query_all(query_str)
print("REST results returned. Length of results (JSON) is {}".format(len(rest_records['records'])))
