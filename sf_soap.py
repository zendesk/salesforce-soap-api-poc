import xml.dom.minidom
import requests
try:
    from collections import OrderedDict
except ImportError:
    # Python < 2.7
    from ordereddict import OrderedDict

def soql(sf, sf_object, field_types, where_clause=''):
    soap_url = 'https://zendesk.my.salesforce.com/services/Soap/u/38.0'
    query = 'select {} FROM {} {}'.format(','.join(field_types.keys()), sf_object, where_clause)
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
    </soapenv:Envelope>""".format(session_id=sf.session_id, query=query)
    soap_request_headers = {
        'content-type': 'text/xml',
        'charset': 'UTF-8',
        'SOAPAction': 'query'
    }
    response = requests.post(soap_url, soap_message_body, headers=soap_request_headers)
    all_records, fetch_more = __handle_query_response(response, field_types)
    while fetch_more != '':
        records, fetch_more = __fetch_more(sf, fetch_more, field_types)
        all_records['records'].extend(records['records'])
        all_records['done'] = records['done']
    return all_records


def __handle_query_response(response, field_types):
    if response.status_code != 200:
        # TODO report failure
        pass
    else:
        xml_string = response.text
        all_results_fetched = is_final_page(xml_string)
        return OrderedDict([
            ('totalSize', get_results_size(xml_string)),
            ('done', all_results_fetched),
            ('records', get_records(xml_string, field_types))
        ]), '' if all_results_fetched else get_query_locator(xml_string)


def __fetch_more(sf, query_locator, field_types):
    soap_message_body_more = """
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
            <urn:queryMore>
                <urn:queryLocator>{query_locator}</urn:queryLocator>
            </urn:queryMore>
        </soapenv:Body>
    </soapenv:Envelope>""".format(session_id=sf.session_id, query_locator=query_locator)
    soap_url = 'https://zendesk.my.salesforce.com/services/Soap/u/38.0'
    soap_request_headers = {
        'content-type': 'text/xml',
        'charset': 'UTF-8',
        'SOAPAction': 'query'
    }
    response = requests.post(soap_url, soap_message_body_more, headers=soap_request_headers)
    return __handle_query_response(response, field_types)


def is_final_page(xml_string):
    result_node = __get_result_node_from_soap_query_response(xml_string)
    return __get_unique_child_value_from_xml(result_node, 'done') == 'true'


def get_results_size(xml_string):
    result_node = __get_result_node_from_soap_query_response(xml_string)
    return int(__get_unique_child_value_from_xml(result_node, 'size'))


def get_query_locator(xml_string):
    result_node = __get_result_node_from_soap_query_response(xml_string)
    return __get_unique_child_value_from_xml(result_node, 'queryLocator')


def get_records(xml_string, field_types):
    result_node = __get_result_node_from_soap_query_response(xml_string)
    all_records = [c for c in result_node.childNodes if c.tagName == 'records']
    all_records_dicts = list()
    for record in all_records:
        attributes_dict = OrderedDict()
        for attribute in record.childNodes:
            if attribute.tagName == 'sf:type':
                pass
            else:
                field_name = attribute.tagName[3:]
                json_attribute_value = __parsers_map[field_types[field_name]](attribute)
                attributes_dict[field_name] = json_attribute_value
        all_records_dicts.append(attributes_dict)
    return all_records_dicts


def __get_result_node_from_soap_query_response(xml_string):
    """

    :param xml_string:
    :return:

    <xml>
      <header>...</header>
      <body>
        <queryAllResponse>
          <result>
            ...
          </result>
        </queryAllResponse>
      </body>
    </xml>
    """
    dom = xml.dom.minidom.parseString(xml_string)
    body_node = dom.firstChild.childNodes[1]
    return body_node.firstChild.firstChild


def __get_unique_child_node_from_xml(xml_dom, element_name):
    elements_by_name = [c for c in xml_dom.childNodes if c.tagName == element_name]
    if len(elements_by_name) > 0:
        return elements_by_name[0]
    return None


def __get_unique_child_value_from_xml(xml_dom, element_name, convert_empty_to_none=False):
    child_node = __get_unique_child_node_from_xml(xml_dom, element_name)
    return '' if child_node is None else __get_text_content(child_node, convert_empty_to_none)


def __get_text_content(node, convert_empty_to_none=False):
    rc = ""
    for node in node.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    if rc == '' and convert_empty_to_none:
        rc = None
    return rc


def __int_parse(node):
    txt_content = __get_text_content(node, convert_empty_to_none=True)
    return None if txt_content is None else int(txt_content)


def __double_parse(node):
    txt_content = __get_text_content(node, convert_empty_to_none=True)
    return None if txt_content is None else float(txt_content)


def __boolean_parse(node):
    return __get_text_content(node).strip() == 'true'


def __string_parse(node):
    return __get_text_content(node, convert_empty_to_none=True)


def __datetime_parse(node):
    txt_content = __get_text_content(node, convert_empty_to_none=True)
    # replace te last Z with +0000  E.g., 2018-10-21T06:57:02.000Z ==> 2018-10-21T06:57:02.000+0000
    return None if txt_content is None else txt_content[:-1] + '+0000'


def __location_parse(node):
    latitude_node = __get_unique_child_node_from_xml(node, 'latitude')
    latitude_value = None if latitude_node is None else __double_parse(latitude_node)
    longitude_node = __get_unique_child_node_from_xml(node, 'longitude')
    longitude_value = None if longitude_node is None else __double_parse(longitude_node)
    return {'latitude': latitude_value, 'longitude': longitude_value}


def __address_parse(node):
    return {
        ** __location_parse(node),
        ** {
            'city':  __get_unique_child_value_from_xml(node, 'city', True),
            'country':  __get_unique_child_value_from_xml(node, 'country', True),
            'countryCode':  __get_unique_child_value_from_xml(node, 'countryCode', True),
            'geocodeAccuracy':  __get_unique_child_value_from_xml(node, 'geocodeAccuracy', True),
            'postalCode':  __get_unique_child_value_from_xml(node, 'postalCode', True),
            'state':  __get_unique_child_value_from_xml(node, 'state', True),
            'stateCode':  __get_unique_child_value_from_xml(node, 'stateCode', True),
            'street':  __get_unique_child_value_from_xml(node, 'street', True)
        }
    }


__parsers_map = {
    'xsd:int': __int_parse,
    'xsd:date': __string_parse,
    'xsd:double': __double_parse,
    'xsd:dateTime': __datetime_parse,
    'xsd:boolean': __boolean_parse,
    'tns:ID': __string_parse,
    'xsd:string': __string_parse,
    'urn:address': __address_parse,
    'urn:location': __location_parse
}
