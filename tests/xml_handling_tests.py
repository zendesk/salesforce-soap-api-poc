import unittest

import sf_soap


class HandlingXmlResults(unittest.TestCase):
    __xml_boilerplate = '<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns="urn:partner.soap.sforce.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:sf="urn:sobject.partner.soap.sforce.com"><soapenv:Header><LimitInfoHeader><limitInfo><current>1032097</current><limit>6597200</limit><type>API REQUESTS</type></limitInfo></LimitInfoHeader></soapenv:Header><soapenv:Body><queryAllResponse><result xsi:type="QueryResult">{}</result></queryAllResponse></soapenv:Body></soapenv:Envelope>'

    def test_done_flag_extraction(self):
        done_flag_final_page = sf_soap.is_final_page(self.__xml_boilerplate.format('<done>true</done>'))
        self.assertTrue(done_flag_final_page)
        done_flag_non_final_page = sf_soap.is_final_page(self.__xml_boilerplate.format('<done>false</done>'))
        self.assertFalse(done_flag_non_final_page)

    def test_total_size_extraction(self):
        size = sf_soap.get_results_size(self.__xml_boilerplate.format('<size>2</size>'))
        self.assertEqual(2, size)

    def test_query_locator_extraction(self):
        xml_string_empty_locator = self.__xml_boilerplate.format('<queryLocator xsi:nil="true"/>')
        query_locator_final_page = sf_soap.get_query_locator(xml_string_empty_locator)
        self.assertEqual('', query_locator_final_page)
        xml_string_non_empty_locator = self.__xml_boilerplate.format('<queryLocator>HWXuZQAX-2000</queryLocator>')
        query_locator_non_final_page = sf_soap.get_query_locator(xml_string_non_empty_locator)
        self.assertEqual('HWXuZQAX-2000', query_locator_non_final_page)

    def test_records_extraction(self):
        fields_map = {
            'Id': 'tns:ID',
            'Name': 'xsd:string',
            'FiscalYear': 'xsd:int',
            'Primary_Quote_OTD_in_months__c': 'xsd:double',
            'IsDeleted': 'xsd:boolean'
        }
        xml_string = self.__xml_boilerplate.format("""
                    <records xsi:type="sf:sObject">
                      <sf:type>Opportunity</sf:type>
                      <sf:Id>00680000016vtCNAAY</sf:Id>
                      <sf:Primary_Quote_OTD_in_months__c>1.5</sf:Primary_Quote_OTD_in_months__c>
                      <sf:FiscalYear>2017</sf:FiscalYear>
                      <sf:IsDeleted>false</sf:IsDeleted>
                      <sf:Name>Autino</sf:Name>
                      <sf:Id>00680000016vtCNAAY</sf:Id>
                    </records>
                    <records xsi:type="sf:sObject">
                      <sf:type>Opportunity</sf:type>
                      <sf:Id>006800000163X3mAAE</sf:Id>
                      <sf:Primary_Quote_OTD_in_months__c>1.0</sf:Primary_Quote_OTD_in_months__c>
                      <sf:FiscalYear>2017</sf:FiscalYear>
                      <sf:IsDeleted>false</sf:IsDeleted>
                      <sf:Name>Vera Security</sf:Name>
                      <sf:Id>006800000163X3mAAE</sf:Id>
                    </records>
        """)
        records = sf_soap.get_records(xml_string, fields_map)
        self.assertEqual(2, len(records))
        self.assertDictEqual(
            {
                'Id': '00680000016vtCNAAY',
                'Primary_Quote_OTD_in_months__c': 1.5,
                'FiscalYear': 2017,
                'IsDeleted': False,
                'Name': 'Autino'
            },
            dict(records[0])
        )

    def test_address_type(self):
        fields_map = {
            'Id': 'tns:ID',
            'BillingAddress': 'urn:address'
        }
        xml_string = self.__xml_boilerplate.format("""
                    <records xsi:type="sf:sObject">
                      <sf:type>Opportunity</sf:type>
                      <sf:BillingAddress xsi:type="address">
                        <latitude>-1.1</latitude>
                        <longitude>14.1</longitude>
                        <city>sydney</city>
                        <country>Australia</country>
                        <countryCode>AU</countryCode>
                        <geocodeAccuracy>Block</geocodeAccuracy>
                        <postalCode>1111</postalCode>
                        <state>Victoria</state>
                        <stateCode>VIC</stateCode>
                        <street>364 st</street>
                      </sf:BillingAddress>
                    </records>
        """)
        records = sf_soap.get_records(xml_string, fields_map)
        self.assertEqual(1, len(records))
        self.assertDictEqual(
            {
                'BillingAddress': {
                    'latitude': -1.1,
                    'longitude': 14.1,
                    'city': 'sydney',
                    'country': 'Australia',
                    'countryCode': 'AU',
                    'geocodeAccuracy': 'Block',
                    'postalCode': '1111',
                    'state': 'Victoria',
                    'stateCode': 'VIC',
                    'street': '364 st'
                }
            },
            dict(records[0])
        )

    def test_incomplete_address_type(self):
        fields_map = {
            'Id': 'tns:ID',
            'BillingAddress': 'urn:address'
        }
        xml_string = self.__xml_boilerplate.format("""
                    <records xsi:type="sf:sObject">
                      <sf:type>Opportunity</sf:type>
                      <sf:BillingAddress xsi:type="address">
                        <longitude>14.1</longitude>
                        <city>sydney</city>
                      </sf:BillingAddress>
                    </records>
        """)
        records = sf_soap.get_records(xml_string, fields_map)
        self.assertEqual(1, len(records))
        self.assertDictEqual(
            {
                'BillingAddress': {
                    'latitude': None,  # missing int defaults to None
                    'longitude': 14.1,
                    'city': 'sydney',
                    'country': '',  # missing strings default to empty strings
                    'countryCode': '',
                    'geocodeAccuracy': '',
                    'postalCode': '',
                    'state': '',
                    'stateCode': '',
                    'street': ''
                }
            },
            dict(records[0])
        )
