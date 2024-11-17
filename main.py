import json
import requests
import time
import os
import yaml
import sys

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        ystr = f.read()
        ymllist = yaml.load(ystr, Loader=yaml.FullLoader)
        return ymllist

# Load configuration from file or environment variables
if os.path.exists('config.yml'):
    c = load_config('config.yml')
    CLOUDFLARE_ZONE_IDS = c['CLOUDFLARE_ZONE_IDS']
    CLOUDFLARE_EMAIL = c['CLOUDFLARE_EMAIL']
    CLOUDFLARE_API_KEY = c['CLOUDFLARE_API_KEY']
    ABUSEIPDB_API_KEY = c['ABUSEIPDB_API_KEY']
    WHITELISTED_IPS = c.get('WHITELISTED_IPS', "").split(",")
else:
    if len(sys.argv) < 6:
        print("Error: Missing required arguments")
        print("Usage: python main.py CLOUDFLARE_ZONE_IDS CLOUDFLARE_EMAIL CLOUDFLARE_API_KEY ABUSEIPDB_API_KEY WHITELISTED_IPS")
        sys.exit(1)
    CLOUDFLARE_ZONE_IDS = sys.argv[1].split(",")
    CLOUDFLARE_EMAIL = sys.argv[2]
    CLOUDFLARE_API_KEY = sys.argv[3]
    ABUSEIPDB_API_KEY = sys.argv[4]
    WHITELISTED_IPS = sys.argv[5].split(",")

def get_blocked_ips(zone_id, max_retries=3):
    payload = {
        "query": """query ListFirewallEvents($zoneTag: string, $filter: FirewallEventsAdaptiveFilter_InputObject) {
            viewer {
                zones(filter: { zoneTag: $zoneTag }) {
                    firewallEventsAdaptive(
                        filter: $filter
                        limit: 1000
                        orderBy: [datetime_DESC]
                    ) {
                        action
                        clientASNDescription
                        clientAsn
                        clientCountryName
                        clientIP
                        clientRequestHTTPMethodName
                        clientRequestHTTPProtocol
                        clientRequestPath
                        clientRequestQuery
                        datetime
                        rayName
                        ruleId
                        source
                        userAgent
                    }
                }
            }
        }""",
        "variables": {
            "zoneTag": zone_id,
            "filter": {
                "datetime_geq": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(time.time() - 60*60*10.5)),
                "datetime_leq": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(time.time() - 60*60*8)),
                "action": "block"
            }
        }
    }
    payload = json.dumps(payload)
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Key": CLOUDFLARE_API_KEY,
        "X-Auth-Email": CLOUDFLARE_EMAIL
    }

    for attempt in range(max_retries):
        try:
            r = requests.post("https://api.cloudflare.com/client/v4/graphql/", headers=headers, data=payload, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if attempt == max_retries - 1:
                print("Max retries reached, giving up")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff

def get_comment(it):
    return (f"The IP has triggered Cloudflare WAF. action: {it['action']} source: {it['source']} "
            f"clientAsn: {it['clientAsn']} clientASNDescription: {it['clientASNDescription']} "
            f"clientCountryName: {it['clientCountryName']} clientIP: {it['clientIP']} "
            f"clientRequestHTTPMethodName: {it['clientRequestHTTPMethodName']} "
            f"clientRequestHTTPProtocol: {it['clientRequestHTTPProtocol']} "
            f"clientRequestPath: {it['clientRequestPath']} "
            f"clientRequestQuery: {it['clientRequestQuery']} datetime: {it['datetime']} "
            f"rayName: {it['rayName']} ruleId: {it['ruleId']} userAgent: {it['userAgent']}. "
            f"Report generated by Cloudflare-WAF-to-AbuseIPDB.")

def report_bad_ip(it):
    try:
        url = 'https://api.abuseipdb.com/api/v2/report'
        params = {
            'ip': it['clientIP'],
            'categories': '10,19',
            'comment': get_comment(it)
        }
        headers = {
            'Accept': 'application/json',
            'Key': ABUSEIPDB_API_KEY
        }
        r = requests.post(url=url, headers=headers, params=params)
        if r.status_code == 200:
            print(f"Reported: {it['clientIP']}")
            response_data = r.json()
            print(json.dumps(response_data, sort_keys=True, indent=4))
            return True
        else:
            print(f"Error: HTTP {r.status_code}")
            return False
    except Exception as e:
        print(f"Error reporting IP: {str(e)}")
        return False

excepted_ruleId = ["fa01280809254f82978e827892db4e46"]

def main():
    print("==================== Start ====================")
    print(f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    print(f"Query time range: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 60*60*8))}")
    
    reported_ip_list = []

    for zone_id in CLOUDFLARE_ZONE_IDS:
        print(f"Processing Zone ID: {zone_id}")
        response = get_blocked_ips(zone_id)
        if not response or "data" not in response or "viewer" not in response["data"]:
            print(f"Failed to get blocked IPs for Zone ID: {zone_id}")
            continue

        ip_bad_list = response["data"]["viewer"]["zones"][0]["firewallEventsAdaptive"]
        print(f"Total events found in Zone {zone_id}: {len(ip_bad_list)}")

        for event in ip_bad_list:
            if (event['ruleId'] not in excepted_ruleId and 
                event['clientIP'] not in reported_ip_list and 
                event['clientIP'] not in WHITELISTED_IPS):
                print(f"IP: {event['clientIP']}, Location: {event['clientCountryName']}, Time: {event['datetime']}")
                if report_bad_ip(event):
                    reported_ip_list.append(event['clientIP'])

    print(f"Total unique IPs reported: {len(reported_ip_list)}")
    print("==================== End ====================")

if __name__ == "__main__":
    main()