from simple_salesforce import Salesforce
from sf_soap import soql
from collections import OrderedDict
sf = Salesforce(security_token=TOKEN, username=USERNAME,
                    password=PASSWORD, sandbox=False)
opp_fields = sf.Opportunity.describe()['fields']
field_types = OrderedDict({f['name']: f['soapType'] for f in opp_fields})
where_clause = 'ORDER BY Id LIMIT 400'
soap_records = soql(sf, 'Opportunity', field_types, where_clause)
rest_records = sf.query_all('SELECT {} FROM Opportunity {}'.format(','.join(field_types.keys()), where_clause))
for r in rest_records['records']:
    r.pop('attributes')
    r.pop('Id')
    r.pop('Next_Step__c')
for r in soap_records['records']:
    r.pop('Id')
    r.pop('Next_Step__c')
print(str(soap_records).replace("\\n", "\\r\\n") == str(rest_records))
~                                                                       
