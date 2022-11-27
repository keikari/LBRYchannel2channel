import requests
import json

server = "http://localhost:5279"

# Set these values manually
old_channel_id = ""
new_channel_id = ""
preview = True
page_size = 20


claims = []
page = 1
def get_signing_channel_from_stream_update_response(response):
    signing_channel_name = None
    for output in response["result"]["outputs"]:
        try: 
            signing_channel_name = output["signing_channel"]["name"]
            return signing_channel_name 
        except KeyError:
            pass

while True:
    response_result = requests.post(server, json={
        "method": "claim_search",
        "params": {
            "channel_id": old_channel_id,
            "page": page,
            "page_size": page_size}}).json()["result"]

    response_claims = response_result["items"]
    claims = claims + response_claims

    total_items = response_result["total_items"]
    page += 1
    if len(claims) >= total_items:
        break

    
for claim in claims:
    if claim["value_type"] == "stream":
        method = "stream_update"
    elif claim["value_type"] == "collection":
        method = "collection_update"

    response = requests.post(server, json={
        "method": method,
        "params": {
            "claim_id": claim["claim_id"],
            "channel_id": new_channel_id,
            "preview": preview}
    }).json()

    #print(json.dumps(response, indent=2))
    if "error" in response:
        print("Error updating claim: %s" % claim["name"])
        print(response["error"]["message"])
        exit(1)
    else:
        signing_channel_name = get_signing_channel_from_stream_update_response(response)
        print("%s%s MOVED TO %s" % ("PREVIEW " if preview else "", claim["name"], signing_channel_name))


