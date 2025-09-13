import pandas as pd
import requests
import json
from parsel import Selector
import time
import random

switch = True

def exporter(row, file_name):
    global switch 
    if switch:
        switch = False
        pd.DataFrame(row, index=[0]).to_csv(file_name, index=False, mode='w')
    else:
        pd.DataFrame(row, index=[0]).to_csv(file_name, index=False, mode='a', header=False)

# Headers for agent links extraction (pagination requests)
headers_links = {
    "authority": "www.realestate.com.au",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.5",
    "accept-encoding": "gzip, deflate, br, zstd",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0",
    "upgrade-insecure-requests": "1",
    "priority": "u=0, i",
    "te": "trailers",
    "cookie": "ew_bkt=61; KP_UIDz-ssn=02nEfggExdcnQTEpP9oichTvp2qrYOx2uHFbCWAMsd4zCvnjbDmE2Z1CPUVZRwM6axSoqGSVAljkPclNdQqvTcR2RfXWDzxXqttZ0P1Paq9KMBFRVz5KsZKnKaQOShww6K0u5CbsGtRlGm8dLEae5VW3s9F3m1EKWM53NtHW8KUyj3qSvjcbrMsM7iQRLUghOLxbUNmQmzeqR; KP_UIDz=02nEfggExdcnQTEpP9oichTvp2qrYOx2uHFbCWAMsd4zCvnjbDmE2Z1CPUVZRwM6axSoqGSVAljkPclNdQqvTcR2RfXWDzxXqttZ0P1Paq9KMBFRVz5KsZKnKaQOShww6K0u5CbsGtRlGm8dLEae5VW3s9F3m1EKWM53NtHW8KUyj3qSvjcbrMsM7iQRLUghOLxbUNmQmzeqR; KP2_UIDz-ssn=028379jalRopbSIWH3WorOPqY2S6isIKJydULxS0SxsDj9QqOraBufAfSZlIgKmu2AIL2cmsFSlBerpoQDmolrGjqpaOqE89qHzmkPUizIFZtnrhIXNTJD61Td68Xhrx1ZyV7PKz8zNMPv6AnKMviGufmEsB4rc4QXpqdUB3YJwQb9gqMNS4ZI5p3eB3w0LjNQlHBWWKZZSFv; KP2_UIDz=028379jalRopbSIWH3WorOPqY2S6isIKJydULxS0SxsDj9QqOraBufAfSZlIgKmu2AIL2cmsFSlBerpoQDmolrGjqpaOqE89qHzmkPUizIFZtnrhIXNTJD61Td68Xhrx1ZyV7PKz8zNMPv6AnKMviGufmEsB4rc4QXpqdUB3YJwQb9gqMNS4ZI5p3eB3w0LjNQlHBWWKZZSFv; reauid=05367c68c4c136009810b8680d010000d4520000; KFC=/HEPdRvkQ8JD7uH6XFaXwr8bwhfHMs6RhLVxXTSBHQw=|1756895272567; utag_main=v_id:01990f01d75200857953bce1eef005050001e00d00978$_sn:1$_se:14$_ss:0$_st:1756897075491$ses_id:1756893402963%3Bexp-session$_pn:11%3Bexp-session$vapi_domain:realestate.com.au$dc_visit:1$dc_event:14%3Bexp-session$_prevpage:rea%3Afind%20agent%3Aagent%3Asearch%20results%3Bexp-1756898877397$dc_region:ap-southeast-2%3Bexp-session$ttd_uuid:987aab05-526f-41f6-9564-101c5d8d4cdc%3Bexp-session$adform_uid:2849165673082987052%3Bexp-session; split_audience=e; AMCV_341225BE55BBF7E17F000101%40AdobeOrg=179643557%7CMCIDTS%7C20335%7CMCMID%7C17373561867500563371638384908789738435%7CMCAAMLH-1757498965%7C12%7CMCAAMB-1757498965%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1756901365s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-20342%7CvVersion%7C5.5.0; _sp_ses.2fe7=*; _sp_id.2fe7=ac3e5dfa-6d84-4a52-a929-cebc51312a25.1756893404.1.1756895277.1756893404.78acc858-2852-432d-87a1-fcc804171abd; s_nr30=1756895277399-New; _gcl_au=1.1.124861295.1756893405; s_ecid=MCMID%7C17373561867500563371638384908789738435; VT_LANG=language%3Den-GB; mid=12384835145773092425; _ga_3J0XCBB972=GS2.1.s1756893405$o1$g1$t1756895282$j53$l0$h0; _ga=GA1.1.475473527.1756893405; _fbp=fb.2.1756893407996.304463756279106298; nol_fpid=lokbqvb86rxipfalq8hilqvqhq2a11756893415|1756893415076|1756895278395|1756895284710; Country=IN; pageview_counter.srs=6; AMCVS_341225BE55BBF7E17F000101%40AdobeOrg=1; s_cc=true; QSI_HistorySession=https%3A%2F%2Fwww.realestate.com.au%2Fagent%2Fettiene-west-82932~1756894206204%7Chttps%3A%2F%2Fwww.realestate.com.au%2Ffind-agent%2Fsydney-cbd-nsw%2F%3Fpid%3Drea%253Ahp%253Asearch-box-search%253Afind-agent~1756895176749%7Chttps%3A%2F%2Fwww.realestate.com.au%2Ffind-agent%2Fsydney-cbd-nsw%2F%3Fpid%3Drea%253Ahp%253Asearch-box-search%253Afind-agent%26page%3D2~1756895216783; DM_SitId1464=1; DM_SitId1464SecId12708=1; legs_sq=%5B%5BB%5D%5D; s_sq=%5B%5BB%5D%5D",
    "if-none-match": "W/\"8d572-tquCNvSSa7KgQz/jNOz1wGYiYgA\""
}

# Headers for agent data extraction (agent profile requests)
headers_data = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.5",
    "accept-encoding": "gzip, deflate, br, zstd",
    "referer": "https://www.realestate.com.au/find-agent/sydney-cbd-nsw?pid=rea:hp:search-box-search:find-agent",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0",
    "upgrade-insecure-requests": "1",
    "priority": "u=0, i",
    "te": "trailers",
    "cookie": "ew_bkt=61; KP_UIDz-ssn=01WDGFBvu2lbRz0rHPV2Tsdlt84QiM0wF5PU7tN4VHXp8zKNatHm1ArofGxYDuP7OXsJsWJT5leP3FSeAdoYZ7xwlt1mJw1lE15ib96I5wgfAowDEulrT7fwF4PGfRAPDTQrUYGMn2JFnLPFlO40WwYkZGLYl3wchOb8LbaOEOLm7E93kiqq2PD6KBRhXED7tqo0iow2tnyEd; KP_UIDz=01WDGFBvu2lbRz0rHPV2Tsdlt84QiM0wF5PU7tN4VHXp8zKNatHm1ArofGxYDuP7OXsJsWJT5leP3FSeAdoYZ7xwlt1mJw1lE15ib96I5wgfAowDEulrT7fwF4PGfRAPDTQrUYGMn2JFnLPFlO40WwYkZGLYl3wchOb8LbaOEOLm7E93kiqq2PD6KBRhXED7tqo0iow2tnyEd; KP2_UIDz-ssn=028379jalRopbSIWH3WorOPqY2S6isIKJydULxS0SxsDj9QqOraBufAfSZlIgKmu2AIL2cmsFSlBerpoQDmolrGjqpaOqE89qHzmkPUizIFZtnrhIXNTJD61Td68Xhrx1ZyV7PKz8zNMPv6AnKMviGufmEsB4rc4QXpqdUB3YJwQb9gqMNS4ZI5p3eB3w0LjNQlHBWWKZZSFv; KP2_UIDz=028379jalRopbSIWH3WorOPqY2S6isIKJydULxS0SxsDj9QqOraBufAfSZlIgKmu2AIL2cmsFSlBerpoQDmolrGjqpaOqE89qHzmkPUizIFZtnrhIXNTJD61Td68Xhrx1ZyV7PKz8zNMPv6AnKMviGufmEsB4rc4QXpqdUB3YJwQb9gqMNS4ZI5p3eB3w0LjNQlHBWWKZZSFv; reauid=05367c68c4c136009810b8680d010000d4520000; KFC=2K1zjUeBACjuxxSJWIEHdRA8W/7Z/CwtOOXe2vIiaBI=|1756901102218; utag_main=v_id:01990f01d75200857953bce1eef005050001e00d00978$_sn:3$_se:2$_ss:0$_st:1756902906912$vapi_domain:realestate.com.au$dc_visit:3$_prevpage:rea%3Afind%20agent%3Aagent%3Asearch%20results%3Bexp-1756904706926$ses_id:1756901105106%3Bexp-session$_pn:1%3Bexp-session$dc_event:2%3Bexp-session$dc_region:ap-southeast-2%3Bexp-session$ttd_uuid:987aab05-526f-41f6-9564-101c5d8d4cdc%3Bexp-session$adform_uid:2849165673082987052%3Bexp-session; split_audience=e; AMCV_341225BE55BBF7E17F000101%40AdobeOrg=179643557%7CMCIDTS%7C20335%7CMCMID%7C17373561867500563371638384908789738435%7CMCAAMLH-1757498965%7C12%7CMCAAMB-1757498965%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1756901365s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-20342%7CvVersion%7C5.5.0; _sp_id.2fe7=ac3e5dfa-6d84-4a52-a929-cebc51312a25.1756893404.3.1756901107.1756898829.3edad81b-bbd5-42c6-a5c6-6375dc216f25; s_nr30=1756901106927-Repeat; _gcl_au=1.1.124861295.1756893405; s_ecid=MCMID%7C17373561867500563371638384908789738435; VT_LANG=language%3Den-GB; mid=12384835145773092425; _ga_3J0XCBB972=GS2.1.s1756901104$o3$g1$t1756901107$j57$l0$h0; _ga=GA1.1.475473527.1756893405; _fbp=fb.2.1756893407996.304463756279106298; nol_fpid=lokbqvb86rxipfalq8hilqvqhq2a11756893415|1756893415076|1756901108427|1756901108491; Country=IN; pageview_counter.srs=15; AMCVS_341225BE55BBF7E17F000101%40AdobeOrg=1; s_cc=true; QSI_HistorySession=https%3A%2F%2Fwww.realestate.com.au%2Ffind-agent%2Fsydney-cbd-nsw%2F%3Fpid%3Drea%253Ahp%253Asearch-box-search%253Afind-agent%26page%3D3~1756898604486%7Chttps%3A%2F%2Fwww.realestate.com.au%2Ffind-agent%2Fsydney-cbd-nsw%2F%3Fpid%3Drea%253Ahp%253Asearch-box-search%253Afind-agent%26page%3D2~1756898829934%7Chttps%3A%2F%2Fwww.realestate.com.au%2Ffind-agent%2Fsydney-cbd-nsw%2F%3Fpid%3Drea%253Ahp%253Asearch-box-search%253Afind-agent~1756901108215; DM_SitId1464=1; DM_SitId1464SecId12708=1; legs_sq=rea-live%3D%2526c.%2526a.%2526activitymap.%2526page%253Drea%25253Afind%252520agent%25253Aagent%25253Asearch%252520results%2526link%253DView%252520profile%2526region%253Dargonaut-wrapper%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Drea%25253Afind%252520agent%25253Aagent%25253Asearch%252520results%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Fwww.realestate.com.au%25252Fagent%25252Fettiene-west-82932%2526ot%253DA; s_sq=rea-group-global-live%3D%2526c.%2526a.%2526activitymap.%2526page%253Drea%25253Afind%252520agent%25253Aagent%25253Asearch%252520results%2526link%253DView%252520profile%2526region%253Dargonaut-wrapper%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Drea%25253Afind%252520agent%25253Aagent%25253Asearch%252520results%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Fwww.realestate.com.au%25252Fagent%25252Fettiene-west-82932%2526ot%253DA; myid5_id=ID5*5EsxW5vgWFDEBLRKpCvc_UCQXKl00KkakNZcuGIkZzBFgoYSVM_H3YTUEDS9_IGd; _sp_ses.2fe7=*"
}

r = requests.Session()
suburb = input('Enter suburb: ')
url = (f'https://www.realestate.com.au/find-agent/{suburb}/?pid=rea:hp:search-box-search:find-agent&page={{page}}')
all_urls = []
for i in range(1, 6):
    url = f'https://www.realestate.com.au/find-agent/{suburb}/?pid=rea:hp:search-box-search:find-agent&page={i}'
    req = r.get(url, headers=headers_links)
    print(url, req.status_code)
    resp = Selector(text=req.text)
    
    links = [
        link if link.startswith("http") 
        else f'https://www.realestate.com.au{link}' 
        for link in resp.xpath('//div[@class="styles__Container-sc-trm1sd-0 cJJBfX"]/a/@href').getall()
    ]
    print(links)
    all_urls.extend(iter(links))
    # next_page = resp.xpath('//a[@class="ButtonBase-sc-1lobkej-0 Link__LinkWithButtonVariant-sc-t5cqk8-0 kfZkJD coEY styles__ArrowButton-sc-1tm2eg4-2 iIlSPf"]/@href').get()
    # if next_page:
    #     next_page = f'https://www.realestate.com.au{next_page}'
    #     url = next_page
    # else:
    #     break

for link in all_urls:
    time.sleep(random.randint(1, 3))  # polite delay
    req = r.get(link, headers=headers_data)  # Use headers_data for agent data extraction
    print(link, req.status_code)
    resp = Selector(text=req.text)

    try:
        js = resp.xpath('//script[contains(text(),"ArgonautExchange")]/text()').get()
        if not js:
            print(f"No JS data found at {link}")
            continue

        raw_json = js.replace('window.ArgonautExchange=', '').rstrip(';')
        parsed_json = json.loads(raw_json)

        profile_raw = parsed_json['resi-agent_customer-profile-experience'].get('AGENT_PROFILE')
        if not profile_raw:
            print(f"No AGENT_PROFILE at {link}")
            continue

        json_data = json.loads(profile_raw)

        name = json_data['agent']['name']
        as_lead = json_data['agentStats']['salesCount']['asLeadAgent']
        as_secondary = json_data['agentStats']['salesCount']['asSecondaryAgent']
        phone = json_data['agent']['mobile']
        job_title = json_data['agent']['jobTitle']
        agency = json_data['agent']['agency']['name']

        agency_location = ''
        if '-' in agency:
            agency_name = agency.split('-')[0]
            agency_location = agency.split('-')[-1]
        else:
            agency_name = agency

        median_sold_price = resp.xpath('//p[contains(text(),"Median sold price")]/preceding::p[1]/text()').get()
        median_days_advertised = resp.xpath('//p[contains(text(),"Median days advertised")]/preceding::p[1]/text()').get()

        data = {
            'url': link,
            'agency_name': agency_name,
            'agency_location': agency_location,
            'job_title': job_title,
            'name': name,
            'phone': phone,
            'properties_sold_as_lead_agent': as_lead,
            'properties_sold_as_secondary_agent': as_secondary,
            'median_sold_price': median_sold_price,
            'median_days_advertised': median_days_advertised
        }

        print(data)
        exporter(data, f'{suburb}.csv')

    except Exception as e:
        print(f"Failed to parse agent at {link}: {e}")
        continue






# GET https://www.realestate.com.au/find-agent/sydney-cbd-nsw/?pid=rea%3Ahp%3Asearch-box-search%3Afind-agent&page=2 HTTP/2.0
# user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0
# accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
# accept-language: en-GB,en;q=0.5
# accept-encoding: gzip, deflate, br, zstd
# cookie: ew_bkt=61
# cookie: KP_UIDz-ssn=02dY9AQotxIc5DaQK77WAfGzIUddXgpUpLygSfPElPlAeEVLXRy9X6bWz7I8rWWsPljXIkcBB9EPqOOg9vPItBzBU7edsDBkyqAkGhwo6KB8FP674J8j0aXkGuBswWs5vlMhY1SPAOtqVVSeMu9Ir88NjAViAWtTptfCTyzkPA9wv0KrCpOIvkGqqxWiCBMYPlIhm7dE3VWm5
# cookie: KP_UIDz=02dY9AQotxIc5DaQK77WAfGzIUddXgpUpLygSfPElPlAeEVLXRy9X6bWz7I8rWWsPljXIkcBB9EPqOOg9vPItBzBU7edsDBkyqAkGhwo6KB8FP674J8j0aXkGuBswWs5vlMhY1SPAOtqVVSeMu9Ir88NjAViAWtTptfCTyzkPA9wv0KrCpOIvkGqqxWiCBMYPlIhm7dE3VWm5
# cookie: KP2_UIDz-ssn=028379jalRopbSIWH3WorOPqY2S6isIKJydULxS0SxsDj9QqOraBufAfSZlIgKmu2AIL2cmsFSlBerpoQDmolrGjqpaOqE89qHzmkPUizIFZtnrhIXNTJD61Td68Xhrx1ZyV7PKz8zNMPv6AnKMviGufmEsB4rc4QXpqdUB3YJwQb9gqMNS4ZI5p3eB3w0LjNQlHBWWKZZSFv
# cookie: KP2_UIDz=028379jalRopbSIWH3WorOPqY2S6isIKJydULxS0SxsDj9QqOraBufAfSZlIgKmu2AIL2cmsFSlBerpoQDmolrGjqpaOqE89qHzmkPUizIFZtnrhIXNTJD61Td68Xhrx1ZyV7PKz8zNMPv6AnKMviGufmEsB4rc4QXpqdUB3YJwQb9gqMNS4ZI5p3eB3w0LjNQlHBWWKZZSFv
# cookie: reauid=05367c68c4c136009810b8680d010000d4520000
# cookie: KFC=/uBU3pN1KV3oytd3eoULzxfG3cYMBSBOlAhmbx5C1M8=|1756898736009
# cookie: utag_main=v_id:01990f01d75200857953bce1eef005050001e00d00978$_sn:2$_se:5$_ss:0$_st:1756900538630$vapi_domain:realestate.com.au$dc_visit:2$_prevpage:rea%3Afind%20agent%3Aagent%3Asearch%20results%3Bexp-1756902340717$ses_id:1756897479455%3Bexp-session$_pn:4%3Bexp-session$dc_event:5%3Bexp-session$dc_region:ap-southeast-2%3Bexp-session$ttd_uuid:987aab05-526f-41f6-9564-101c5d8d4cdc%3Bexp-session$adform_uid:2849165673082987052%3Bexp-session
# cookie: split_audience=e
# cookie: AMCV_341225BE55BBF7E17F000101%40AdobeOrg=179643557%7CMCIDTS%7C20335%7CMCMID%7C17373561867500563371638384908789738435%7CMCAAMLH-1757498965%7C12%7CMCAAMB-1757498965%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1756901365s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-20342%7CvVersion%7C5.5.0
# cookie: _sp_id.2fe7=ac3e5dfa-6d84-4a52-a929-cebc51312a25.1756893404.2.1756898741.1756895302.ea4dd3bf-efb9-4795-b548-aa74ffd50358
# cookie: s_nr30=1756898740719-Repeat
# cookie: _gcl_au=1.1.124861295.1756893405
# cookie: s_ecid=MCMID%7C17373561867500563371638384908789738435
# cookie: VT_LANG=language%3Den-GB
# cookie: mid=12384835145773092425
# cookie: _ga_3J0XCBB972=GS2.1.s1756897474$o2$g1$t1756898746$j52$l0$h0
# cookie: _ga=GA1.1.475473527.1756893405
# cookie: _fbp=fb.2.1756893407996.304463756279106298
# cookie: nol_fpid=lokbqvb86rxipfalq8hilqvqhq2a11756893415|1756893415076|1756898742568|1756898750192
# cookie: Country=IN
# cookie: pageview_counter.srs=12
# cookie: AMCVS_341225BE55BBF7E17F000101%40AdobeOrg=1
# cookie: s_cc=true
# cookie: QSI_HistorySession=https%3A%2F%2Fwww.realestate.com.au%2Ffind-agent%2Fsydney-cbd-nsw%2F%3Fpid%3Drea%253Ahp%253Asearch-box-search%253Afind-agent%26page%3D4~1756897500190%7Chttps%3A%2F%2Fwww.realestate.com.au%2Ffind-agent%2Fsydney-cbd-nsw%2F%3Fpid%3Drea%253Ahp%253Asearch-box-search%253Afind-agent%26page%3D2~1756897576603%7Chttps%3A%2F%2Fwww.realestate.com.au%2Ffind-agent%2Fsydney-cbd-nsw%2F%3Fpid%3Drea%253Ahp%253Asearch-box-search%253Afind-agent%26page%3D3~1756898604486
# cookie: DM_SitId1464=1
# cookie: DM_SitId1464SecId12708=1
# cookie: legs_sq=%5B%5BB%5D%5D
# cookie: s_sq=%5B%5BB%5D%5D
# cookie: _sp_ses.2fe7=*
# cookie: myid5_id=ID5*5EsxW5vgWFDEBLRKpCvc_UCQXKl00KkakNZcuGIkZzBFgoYSVM_H3YTUEDS9_IGd
# upgrade-insecure-requests: 1
# sec-fetch-dest: document
# sec-fetch-mode: navigate
# sec-fetch-site: none
# sec-fetch-user: ?1
# priority: u=0, i
# te: trailers









# cookie: ew_bkt=61
# cookie: KP_UIDz-ssn=01WDGFBvu2lbRz0rHPV2Tsdlt84QiM0wF5PU7tN4VHXp8zKNatHm1ArofGxYDuP7OXsJsWJT5leP3FSeAdoYZ7xwlt1mJw1lE15ib96I5wgfAowDEulrT7fwF4PGfRAPDTQrUYGMn2JFnLPFlO40WwYkZGLYl3wchOb8LbaOEOLm7E93kiqq2PD6KBRhXED7tqo0iow2tnyEd
# cookie: KP_UIDz=01WDGFBvu2lbRz0rHPV2Tsdlt84QiM0wF5PU7tN4VHXp8zKNatHm1ArofGxYDuP7OXsJsWJT5leP3FSeAdoYZ7xwlt1mJw1lE15ib96I5wgfAowDEulrT7fwF4PGfRAPDTQrUYGMn2JFnLPFlO40WwYkZGLYl3wchOb8LbaOEOLm7E93kiqq2PD6KBRhXED7tqo0iow2tnyEd
# cookie: KP2_UIDz-ssn=028379jalRopbSIWH3WorOPqY2S6isIKJydULxS0SxsDj9QqOraBufAfSZlIgKmu2AIL2cmsFSlBerpoQDmolrGjqpaOqE89qHzmkPUizIFZtnrhIXNTJD61Td68Xhrx1ZyV7PKz8zNMPv6AnKMviGufmEsB4rc4QXpqdUB3YJwQb9gqMNS4ZI5p3eB3w0LjNQlHBWWKZZSFv
# cookie: KP2_UIDz=028379jalRopbSIWH3WorOPqY2S6isIKJydULxS0SxsDj9QqOraBufAfSZlIgKmu2AIL2cmsFSlBerpoQDmolrGjqpaOqE89qHzmkPUizIFZtnrhIXNTJD61Td68Xhrx1ZyV7PKz8zNMPv6AnKMviGufmEsB4rc4QXpqdUB3YJwQb9gqMNS4ZI5p3eB3w0LjNQlHBWWKZZSFv
# cookie: reauid=05367c68c4c136009810b8680d010000d4520000
# cookie: KFC=2K1zjUeBACjuxxSJWIEHdRA8W/7Z/CwtOOXe2vIiaBI=|1756901102218
# cookie: utag_main=v_id:01990f01d75200857953bce1eef005050001e00d00978$_sn:3$_se:2$_ss:0$_st:1756902906912$vapi_domain:realestate.com.au$dc_visit:3$_prevpage:rea%3Afind%20agent%3Aagent%3Asearch%20results%3Bexp-1756904706926$ses_id:1756901105106%3Bexp-session$_pn:1%3Bexp-session$dc_event:2%3Bexp-session$dc_region:ap-southeast-2%3Bexp-session$ttd_uuid:987aab05-526f-41f6-9564-101c5d8d4cdc%3Bexp-session$adform_uid:2849165673082987052%3Bexp-session
# cookie: split_audience=e
# cookie: AMCV_341225BE55BBF7E17F000101%40AdobeOrg=179643557%7CMCIDTS%7C20335%7CMCMID%7C17373561867500563371638384908789738435%7CMCAAMLH-1757498965%7C12%7CMCAAMB-1757498965%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1756901365s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-20342%7CvVersion%7C5.5.0
# cookie: _sp_id.2fe7=ac3e5dfa-6d84-4a52-a929-cebc51312a25.1756893404.3.1756901107.1756898829.3edad81b-bbd5-42c6-a5c6-6375dc216f25
# cookie: s_nr30=1756901106927-Repeat
# cookie: _gcl_au=1.1.124861295.1756893405
# cookie: s_ecid=MCMID%7C17373561867500563371638384908789738435
# cookie: VT_LANG=language%3Den-GB
# cookie: mid=12384835145773092425
# cookie: _ga_3J0XCBB972=GS2.1.s1756901104$o3$g1$t1756901107$j57$l0$h0
# cookie: _ga=GA1.1.475473527.1756893405
# cookie: _fbp=fb.2.1756893407996.304463756279106298
# cookie: nol_fpid=lokbqvb86rxipfalq8hilqvqhq2a11756893415|1756893415076|1756901108427|1756901108491
# cookie: Country=IN
# cookie: pageview_counter.srs=15
# cookie: AMCVS_341225BE55BBF7E17F000101%40AdobeOrg=1
# cookie: s_cc=true
# cookie: QSI_HistorySession=https%3A%2F%2Fwww.realestate.com.au%2Ffind-agent%2Fsydney-cbd-nsw%2F%3Fpid%3Drea%253Ahp%253Asearch-box-search%253Afind-agent%26page%3D3~1756898604486%7Chttps%3A%2F%2Fwww.realestate.com.au%2Ffind-agent%2Fsydney-cbd-nsw%2F%3Fpid%3Drea%253Ahp%253Asearch-box-search%253Afind-agent%26page%3D2~1756898829934%7Chttps%3A%2F%2Fwww.realestate.com.au%2Ffind-agent%2Fsydney-cbd-nsw%2F%3Fpid%3Drea%253Ahp%253Asearch-box-search%253Afind-agent~1756901108215
# cookie: DM_SitId1464=1
# cookie: DM_SitId1464SecId12708=1
# cookie: legs_sq=rea-live%3D%2526c.%2526a.%2526activitymap.%2526page%253Drea%25253Afind%252520agent%25253Aagent%25253Asearch%252520results%2526link%253DView%252520profile%2526region%253Dargonaut-wrapper%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Drea%25253Afind%252520agent%25253Aagent%25253Asearch%252520results%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Fwww.realestate.com.au%25252Fagent%25252Fettiene-west-82932%2526ot%253DA
# cookie: s_sq=rea-group-global-live%3D%2526c.%2526a.%2526activitymap.%2526page%253Drea%25253Afind%252520agent%25253Aagent%25253Asearch%252520results%2526link%253DView%252520profile%2526region%253Dargonaut-wrapper%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Drea%25253Afind%252520agent%25253Aagent%25253Asearch%252520results%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Fwww.realestate.com.au%25252Fagent%25252Fettiene-west-82932%2526ot%253DA
# cookie: myid5_id=ID5*5EsxW5vgWFDEBLRKpCvc_UCQXKl00KkakNZcuGIkZzBFgoYSVM_H3YTUEDS9_IGd
# cookie: _sp_ses.2fe7=*






