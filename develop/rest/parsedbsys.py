import requests
import pandas as pd
import json

token = "Token 62367705b900816e5dc3ab6c6c4c3b4b2e2b9931"
tags_dict = {}

def get_tag(string) :
    if "admc" in string :
        toreturn = "segi-admc"
    elif "segi-systeme" in string :
        toreturn =  "segi-system"
    elif "ati helpdesk" in string :
        toreturn =  "ati-helpdesk"
    elif "segi-tel" in string :
        toreturn =  "segi-tel"
    elif "segi-dev" in string :
        toreturn =  "segi-dev"
    elif "ulis" in string :
        toreturn =  "segi-ulis"
    elif "devops" in string :
        toreturn =  "segi-devops"
    elif "archi" in string :
        toreturn =  "udi-archi"
    elif "network" in string :
        toreturn =  "segi-network"
    elif "biblio" in string :
        toreturn =  "biblio"
    elif "udi-giga" in string or "udi-med" in string :
        toreturn =  "udi-med"
    elif "cipl" in string :
        toreturn =  "udi-cipl"
    elif "udi-fmv" in string :
        toreturn =  "udi-fmv"
    elif "udi-droit" in string :
        toreturn =  "udi-droit"
    elif "oury" in string :
        toreturn =  "udi-oury"
    elif "montef" in string :
        toreturn =  "udi-montef"
    elif "unipc" in string :
        toreturn =  "udi-unipc"
    elif "gembloux" in string :
        toreturn =  "udi-gembloux"
    elif "hec" in string :
        toreturn =  "udi-hec"
    elif "udi-math" in string :
        toreturn =  "udi-math"
    elif "fapse" in string :
        toreturn =  "udi-fapse"
    elif "csl" in string :
        toreturn =  "csl"
    elif "ifres" in string :
        toreturn =  "ifres"
    elif "forem" in string :
        toreturn =  "forem"
    elif "sap" in string or "arf" in string :
        toreturn =  "arf-sap"
    elif "spi" in string or "brocha" in string :
        toreturn =  "spi"
    elif "sai-dmi" in string :
        toreturn =  "sai-dmi"
    elif "sai-dba" in string :
        toreturn =  "sai-dba"
    elif "sai-mtech" in string :
        toreturn =  "sai-mtech"
    elif "sai-adm" in string :
        toreturn =  "sai-adm"
    elif "ari" in string :
        toreturn =  "ari"
    elif "imagerie" in string :
        toreturn =  "chu-imagerie-medicale"
    elif "ceci" in string :
        toreturn =  "ceci"
    elif "foederis" in string :
        toreturn =  "foederis"
    elif "thot" in string :
        toreturn =  "thot"
    elif "sime" in string :
        toreturn =  "chu-sime"
    elif "radiotherapie" in string or "soret" in string or "radiothérapie" in string:
        toreturn =  "chu-rth"
    elif "cardio" in string :
        toreturn =  "chu-cardiologie"

    else :
        return None

    if toreturn not in tags_dict :
        tags_dict[toreturn] = create_netbox_tag(toreturn)

    return tags_dict[toreturn]

def get_tag_from_hostname(hostname) :
    if "forem.socext" in hostname :
        toreturn = "forem"
    elif "spi.be" in hostname :
        toreturn = "spi"
    elif "astro" in hostname :
        toreturn = "unipc"
    elif "rth-" in hostname :
        toreturn = "chu-rth"

    else :
        return None 

    if toreturn not in tags_dict :
        tags_dict[toreturn] = create_netbox_tag(toreturn)

    return tags_dict[toreturn]

def get_netbox_tags():
    url = "http://127.0.0.1:8002/api/extras/tags/"

    headers = {
        'accept': "application/json",
        'authorization': token
    }

    response = requests.request("GET", url, headers=headers)
    r = response.json()
    tags = {}
    for i in r["results"] :
        id = i["id"]
        name = i["name"]
        #print(i)
        tags[name] = id

    return tags

def create_netbox_tag(tagname):
    url = "http://127.0.0.1:8002/api/extras/tags/"

    headers = {
        'user-agent': "vscode-restclient",
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': token
    }

    payload = json.dumps({"name" : tagname, "slug" : tagname, "color" : "ff9933"})

    print("Creation du tag %s" %tagname)
    response = requests.request("POST", url, data=payload, headers=headers)
    r = response.json()
    return r["id"]

def parse_dbsys(filename) :
    df = pd.read_excel(filename)
    #print(df)
    toreturn = {}
    for index, row in df.iterrows(): 
        #print(row["hostname"])
        dnsname = str(row["hostname"]).strip() + "." + str(row["suffixDns"]).strip()
        dnsname = dnsname.lower()
        toreturn[dnsname] = {
            "respappl" : str(row["respAppl"]).lower(), 
            "gestinterne" : str(row["gestionnaireInterne"]).lower(), 
            "etatSysteme" : str(row["etatSysteme"]),
            "tags" : set(), 
            #"tagsid" : [],
            "dbsys" : row["id"]}

        tag1 = get_tag(toreturn[dnsname]["respappl"])
        if tag1 : 
            toreturn[dnsname]["tags"].add(tag1)
            # if tag1 not in tags_dict :
            #     tags_dict[tag1] = create_netbox_tag(tag1)

        tag2 = get_tag(toreturn[dnsname]["gestinterne"])
        if tag2 : 
            toreturn[dnsname]["tags"].add(tag2)
            # if tag2 not in tags_dict :
            #     tags_dict[tag2] = create_netbox_tag(tag2)

        # tag3 = get_tag_from_hostname(dnsname)
        # if tag3 :
        #     toreturn[dnsname]["tags"].add(tag3)
        #     if tag3 not in tags_dict :
        #         tags_dict[tag3] = create_netbox_tag(tag3)

        status =  toreturn[dnsname]["etatSysteme"]
        if status == "déclassé" :
            toreturn[dnsname]["status"] = "demob"
        else : 
            toreturn[dnsname]["status"] = "active"

        # for i in toreturn[dnsname]["tags"] :
        #     toreturn[dnsname]["tagsid"].append(tags_dict[i])

        try :
            ipaddress = row["ipAddress"].split(', ')
            for ip in ipaddress :
                toreturn[ip] = toreturn[dnsname]
        except :
            pass

    return toreturn

def update_netbox_hosts(sysdict) :
    url = "http://127.0.0.1:8002/api/plugins/vulnerabilities/host/"

    headers = {
        'accept': "application/json",
        'authorization': token
    }

    headerspatch = {
        'user-agent': "vscode-restclient",
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': token
    }

    response = requests.request("GET", url + "?limit=2500", headers=headers)
    r = response.json()
    count = 0
    notag = []

    print(len(r["results"]))
    for host in r["results"] :
        hostname = host["name"]
        try :
            ip = host["ip"]["address"].split('/')[0]
        except :
            ip = "aucune"
        #print(hostname)
        if hostname in sysdict :
            tags = sysdict[hostname]["tags"]
            
            payload = {
                "tags" : list(tags),
                "dbsys_id" : sysdict[hostname]["dbsys"]
            }
            if sysdict[hostname]["status"] == "demob" :
                payload["status"] = "Decommissioned"

        elif ip in sysdict :
            tags = sysdict[ip]["tags"]
            payload = {
                "tags" : list(tags),
                "dbsys_id" : sysdict[ip]["dbsys"]
            }
            if sysdict[ip]["status"] == "demob" :
                payload["status"] = "Decommissioned"

        else :
            # La machine n'est pas dans la DB systeme, on essaie de recuperer des tags dans le hostname
            tags = set()
            tagid = get_tag_from_hostname(hostname)
            if tagid : tags.add(tagid)
                
            payload = {
                "tags" : list(tags),
            }

        if len(tags) == 0 :
            notag.append(hostname)

        existingtags = set()
        for tagid in host["tags"] :
            existingtags.add(tagid["id"])
        # Pas de changement dans les tags
        if existingtags == tags and "status" not in payload:
            continue
        # Tags entres manuellement, pas besoin d'update
        if len(tags) == 0 and len(existingtags) > 0 :
            continue
        
        count += 1
        urlhost = url + str(host["id"]) + "/"
        #print(payload)
        payload = json.dumps(payload)
        response = requests.request("PATCH", urlhost, data=payload, headers=headerspatch)

    print("Hosts updates : %i" %count)
    print(f"Les {len(notag)} machines suivantes n'ont aucun tag")
    print(notag)

tags_dict = get_netbox_tags()

sysdict = parse_dbsys("dbsys.xls")
#for cle, valeur in sysdict.items():
#    if "gx" in cle :
#        print("%s : %s (%s) " %(cle, str(valeur["tags"]), str(valeur["tagsid"])))
#print(sysdict)

update_netbox_hosts(sysdict)