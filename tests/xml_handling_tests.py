import unittest

import sf_soap


class HandlingXmlResults(unittest.TestCase):
    xml_result_final_page = '<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns="urn:partner.soap.sforce.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:sf="urn:sobject.partner.soap.sforce.com"><soapenv:Header><LimitInfoHeader><limitInfo><current>1032097</current><limit>6597200</limit><type>API REQUESTS</type></limitInfo></LimitInfoHeader></soapenv:Header><soapenv:Body><queryAllResponse><result xsi:type="QueryResult"><done>true</done><queryLocator xsi:nil="true"/><records xsi:type="sf:sObject"><sf:type>Opportunity</sf:type><sf:Id>0068000000gP5C3AAK</sf:Id><sf:Id>0068000000gP5C3AAK</sf:Id><sf:Name>Krech Ojard &amp;Associates-4 REG</sf:Name></records><records xsi:type="sf:sObject"><sf:type>Opportunity</sf:type><sf:Id>0068000000gOoDLAA0</sf:Id><sf:Id>0068000000gOoDLAA0</sf:Id><sf:Name>Fiverr - CSS customisation</sf:Name></records><size>2</size></result></queryAllResponse></soapenv:Body></soapenv:Envelope>'
    xml_result_non_final_page = '<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns="urn:partner.soap.sforce.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:sf="urn:sobject.partner.soap.sforce.com"><soapenv:Header><LimitInfoHeader><limitInfo><current>1032097</current><limit>6597200</limit><type>API REQUESTS</type></limitInfo></LimitInfoHeader></soapenv:Header><soapenv:Body><queryAllResponse><result xsi:type="QueryResult"><done>false</done><queryLocator>01g1E00009HWXuZQAX-2000</queryLocator><records xsi:type="sf:sObject"><sf:type>Opportunity</sf:type><sf:Id>0068000000gP5C3AAK</sf:Id><sf:Id>0068000000gP5C3AAK</sf:Id><sf:Name>Krech Ojard &amp;Associates-4 REG</sf:Name></records><records xsi:type="sf:sObject"><sf:type>Opportunity</sf:type><sf:Id>0068000000gOoDLAA0</sf:Id><sf:Id>0068000000gOoDLAA0</sf:Id><sf:Name>Fiverr - CSS customisation</sf:Name></records><size>3000</size></result></queryAllResponse></soapenv:Body></soapenv:Envelope>'
    multiple_types_results = '<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns="urn:partner.soap.sforce.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:sf="urn:sobject.partner.soap.sforce.com"><soapenv:Header><LimitInfoHeader><limitInfo><current>1105872</current><limit>6597200</limit><type>API REQUESTS</type></limitInfo></LimitInfoHeader></soapenv:Header><soapenv:Body><queryResponse><result xsi:type="QueryResult"><done>true</done><queryLocator xsi:nil="true"/><records xsi:type="sf:sObject"><sf:type>Opportunity</sf:type><sf:Id>00680000016vtCNAAY</sf:Id><sf:Primary_Quote_OTD_in_months__c>1.5</sf:Primary_Quote_OTD_in_months__c><sf:FiscalYear>2017</sf:FiscalYear><sf:IsDeleted>false</sf:IsDeleted><sf:Name>Autino - Expansion to Ent, Guide , Talk &amp; Chat</sf:Name><sf:Id>00680000016vtCNAAY</sf:Id></records><records xsi:type="sf:sObject"><sf:type>Opportunity</sf:type><sf:Id>006800000163X3mAAE</sf:Id><sf:Primary_Quote_OTD_in_months__c>1.0</sf:Primary_Quote_OTD_in_months__c><sf:FiscalYear>2017</sf:FiscalYear><sf:IsDeleted>false</sf:IsDeleted><sf:Name>Vera Security - Ent+GuidePro+LightAgents+NPS+Talk/Chat Basic</sf:Name><sf:Id>006800000163X3mAAE</sf:Id></records><records xsi:type="sf:sObject"><sf:type>Opportunity</sf:type><sf:Id>006800000164HFPAA2</sf:Id><sf:Primary_Quote_OTD_in_months__c>0.19</sf:Primary_Quote_OTD_in_months__c><sf:FiscalYear>2017</sf:FiscalYear><sf:IsDeleted>false</sf:IsDeleted><sf:Name>DraftKings | +61E (146) +61 Prem Chat (146)</sf:Name><sf:Id>006800000164HFPAA2</sf:Id></records><records xsi:type="sf:sObject"><sf:type>Opportunity</sf:type><sf:Id>006800000163scIAAQ</sf:Id><sf:Primary_Quote_OTD_in_months__c>1.0</sf:Primary_Quote_OTD_in_months__c><sf:FiscalYear>2017</sf:FiscalYear><sf:IsDeleted>false</sf:IsDeleted><sf:Name>Upwork Advanced Security</sf:Name><sf:Id>006800000163scIAAQ</sf:Id></records><size>4</size></result></queryResponse></soapenv:Body></soapenv:Envelope>'
    xml_reslts_with_address_field = '<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns="urn:partner.soap.sforce.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:sf="urn:sobject.partner.soap.sforce.com"><soapenv:Header><LimitInfoHeader><limitInfo><current>1105872</current><limit>6597200</limit><type>API REQUESTS</type></limitInfo></LimitInfoHeader></soapenv:Header><soapenv:Body><queryResponse><result xsi:type="QueryResult"><done>true</done><queryLocator xsi:nil="true"/><records xsi:type="sf:sObject"><sf:type>Opportunity</sf:type><sf:Id>00680000016vtCNAAY</sf:Id><sf:BillingAddress xsi:type="address"><latitude>-37.98953058101774</latitude><longitude>145.1901729167909</longitude><city>keysborough</city><country>Australia</country><countryCode>AU</countryCode><geocodeAccuracy>Block</geocodeAccuracy><postalCode>3173</postalCode><state>Victoria</state><stateCode>VIC</stateCode><street>364cambriard</street></sf:BillingAddress></records><size>1</size></result></queryResponse></soapenv:Body></soapenv:Envelope>'

    def test_done_flag_extraction(self):
        done_flag_final_page = sf_soap.is_final_page(self.xml_result_final_page)
        self.assertTrue(done_flag_final_page)
        done_flag_non_final_page = sf_soap.is_final_page(self.xml_result_non_final_page)
        self.assertFalse(done_flag_non_final_page)

    def test_total_size_extraction(self):
        size = sf_soap.get_results_size(self.xml_result_final_page)
        self.assertEqual(2, size)

    def test_query_locator_extraction(self):
        query_locator_final_page = sf_soap.get_query_locator(self.xml_result_final_page)
        self.assertEqual('', query_locator_final_page)
        query_locator_non_final_page = sf_soap.get_query_locator(self.xml_result_non_final_page)
        self.assertEqual('01g1E00009HWXuZQAX-2000', query_locator_non_final_page)

    def test_records_extraction(self):
        fields_map = {
            'Id': 'tns:ID',
            'Name': 'xsd:string',
            'FiscalYear': 'xsd:int',
            'Primary_Quote_OTD_in_months__c': 'xsd:double',
            'IsDeleted': 'xsd:boolean'
        }
        records = sf_soap.get_records(self.xml_result_final_page, fields_map)
        print(records)
        records = sf_soap.get_records(self.xml_result_non_final_page, fields_map)
        print(records)
        records = sf_soap.get_records(self.multiple_types_results, fields_map)
        print(records)

    def test_address_type(self):
        fields_map = {
            'Id': 'tns:ID',
            'BillingAddress': 'urn:address'
        }
        records = sf_soap.get_records(self.xml_reslts_with_address_field, fields_map)
        print(records)
