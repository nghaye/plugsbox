import requests
import pandas as pd
import json

import sys
import socket

token = "Token 62367705b900816e5dc3ab6c6c4c3b4b2e2b9931"
headers_get = {
    'accept': "application/json",
    'authorization': token
}
headers_post = {
    'user-agent': "vscode-restclient",
    'accept': "application/json",
    'content-type': "application/json",
    'authorization': token
}

def get_plugin(pluginid) :
    url = "http://127.0.0.1:8002/api/plugins/vulnerabilities/knownvulnerability"
    querystring = {"plugin_id": pluginid}

    headers = {
        'accept': "application/json",
        'authorization': token
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    r = response.json()

    if r["count"] == 1 :
        return r["results"][0]
    else :
        return None

def create_plugin(plugindata) :

    url = "http://127.0.0.1:8002/api/plugins/vulnerabilities/knownvulnerability/"

    payload = json.dumps(plugindata)
    headers = {
        'user-agent': "vscode-restclient",
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': token
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    #print(payload)
    #print(response.text)

    try :
        r = response.json()
        return r["id"]
    except :
        #print(plugindata)
        #print(response.text)
        return None

def get_host(hostname) :
    url = "http://127.0.0.1:8002/api/plugins/vulnerabilities/host/"
    querystring = {"name": hostname}

    headers = {
        'accept': "application/json",
        'authorization': token
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    r = response.json()

    if r["count"] == 1 :
        return r["results"][0]
    else :
        return None

def create_host(hostdata) :

    url = "http://127.0.0.1:8002/api/plugins/vulnerabilities/host/"

    payload = json.dumps(hostdata)
    headers = {
        'user-agent': "vscode-restclient",
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': token
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    try :
        r = response.json()
        return r["id"]
    except :
        print("Erreur a la creation du host %s" %hostdata["name"])
        return None

def update_host(id, data) :

    url = f"http://127.0.0.1:8002/api/plugins/vulnerabilities/host/{id}/"

    payload = json.dumps(data)
    headers = {
        'user-agent': "vscode-restclient",
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': token
        }

    response = requests.request("PATCH", url, data=payload, headers=headers)

    try :
        return response.json()
    except :
        print("Erreur a l'update du host %s" %hostdata["name"])

def get_vuln(hostid) :
    url = "http://127.0.0.1:8002/api/plugins/vulnerabilities/vulnerability"
    querystring = {"host_id": hostid, "limit" : 300}

    headers = {
        'accept': "application/json",
        'authorization': token
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    #print(querystring)
    #print(response.text)
    r = response.json()

    if r["count"] != 0 :
        return r["results"]
    else :
        return []

def create_vuln(vulndata) :

    url = "http://127.0.0.1:8002/api/plugins/vulnerabilities/vulnerability/"

    payload = json.dumps(vulndata)
    headers = {
        'user-agent': "vscode-restclient",
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': token
        }

    #print(vulndata)

    response = requests.request("POST", url, data=payload, headers=headers)
    #print(response.text)

    try :
        r = response.json()
        return r["id"]
    except :
        print(payload)
        print(response.text)
        print("Erreur a la creation de la vulnerability %s" %vulndata["host"])
        return None

def update_vuln(id, data) :

    url = f"http://127.0.0.1:8002/api/plugins/vulnerabilities/vulnerability/{id}/"

    payload = json.dumps(data)
    headers = {
        'user-agent': "vscode-restclient",
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': token
        }

    response = requests.request("PATCH", url, data=payload, headers=headers)

    try :
        r = response.json()
        return r["id"]
    except :
        print(payload)
        print(response.text)
        print(f"Erreur a l'update de la vulnerability {id}")
        return None

# def get_ip_id(dnsname) :
#     url = "http://127.0.0.1:8002/api/ipam/ip-addresses/"
#     querystring = {"dns_name": dnsname}

#     headers = {
#         'accept': "application/json",
#         'authorization': token
#     }

#     response = requests.request("GET", url, headers=headers, params=querystring)
#     r = response.json()

#     if r["count"] != 0 :
#         return r["results"][0]["id"]
#     else :
#         return None

# def create_ip(dnsname) :
#     url = "http://127.0.0.1:8002/api/ipam/ip-addresses/"

#     try :
#         ipaddress = socket.gethostbyname(dnsname) + "/32"
#     except :
#         return None
#     ipdata = {"address" : ipaddress, "dns_name" : dnsname}

#     payload = json.dumps(ipdata)
#     headers = {
#         'user-agent': "vscode-restclient",
#         'accept': "application/json",
#         'content-type': "application/json",
#         'authorization': token
#         }

#     response = requests.request("POST", url, data=payload, headers=headers)

#     try :
#         r = response.json()
#         return r["id"]
#     except :
#         print(payload)
#         print(response.text)
#         print("Erreur a la creation de l'ip %s" %ipdata["ip"])
#         return None

def get_create_update_ip(dnsname) :
    try :
        ipaddress = socket.gethostbyname(dnsname) + "/32"
    except :
        ipaddress = None 

    url = "http://127.0.0.1:8002/api/ipam/ip-addresses/"
    querystring = {"dns_name": dnsname}

    response = requests.request("GET", url, headers=headers_get, params=querystring)
    r = response.json()

    # Creation d'un object IP
    if r["count"] == 0 :
        payload = json.dumps({"address" : ipaddress, "dns_name" : dnsname})
        response_post = requests.request("POST", url, data=payload, headers=headers_post)
        try :
            return response_post.json()["id"]
        except :
            print(response_post.text)
            print("Erreur a la creation de l'ip %s" %ipaddress)
            return None
    ip_id = r["results"][0]["id"]
    # Suppression de l'object IP
    if r["count"] > 0 and ipaddress == None :
        print("Suppresion de l'object IP %s" %dnsname)
        url_del = url + str(ip_id) + "/"
        response_del = requests.request("DELETE", url_del, data=payload, headers=headers_post)
    # Update de l'Adresse IP
    elif r["count"] > 0 and ipaddress != r["results"][0]["address"]:
        print("Update de l'adresse IP de %s" %dnsname)
        url_patch = url + str(ip_id) + "/"
        payload = json.dumps({"address" : ipaddress})
        response_post = requests.request("PATCH", url_patch, data=payload, headers=headers_post)

    return ip_id


nessusfile = sys.argv[1]
date = sys.argv[2]

existing = {}
existinghost = {}
#existingvuln = {}

hosts_stack = {}

df = pd.read_excel(nessusfile)

count = 0

#print(df)
for index, row in df.iterrows(): 
    if row["Risk"] == "None" :
        risk = "info"
    else :
        risk = row["Risk"].lower()
    count += 1
    # if count == 10 :
    #     break
    pluginid = row["Plugin ID"]
    hostname = row["Host"]
    cvss = 0
    if "CVSS" in row :
        cvss = row["CVSS"]
    elif "CVSS v2.0 Base Score" in row :
        cvss = row["CVSS v2.0 Base Score"]
    if "Plugin Output" in row and not pd.isna(row["Plugin Output"]):
        output = row["Plugin Output"]
    else :
        output = ""
    if pd.isna(row["Solution"]) :
        row["Solution"] = ""

    # Recuperation du plugin
    if not pluginid in existing :
        r = get_plugin(pluginid)
        if r != None :
            plugin_objectid = r["id"]
            existing[pluginid] = plugin_objectid
        # Creation du plugin si inexistant
        else :
            print("Creation du plugin " + str(pluginid))
            plugindata = {
                "plugin_id" : pluginid,
                "cvss_v2" : cvss,
                "risk" : risk,
                "name" : row["Name"],
                "synopsis" : row["Synopsis"],
                "description" : row["Description"],
                "solution" : row["Solution"],
            }
            if not pd.isna(row["CVE"]) :
                plugindata["cve"] = row["CVE"]
            if not pd.isna(row["See Also"]) :
                plugindata["see_also"] = row["See Also"].split('\n')[0]
            if pd.isna(cvss) :
                plugindata["cvss_v2"] = 0.0
            plugin_objectid = create_plugin(plugindata)
            if plugin_objectid == None :
                print("Erreur à la creation du plugin " + str(pluginid))
                break
            existing[pluginid] = plugin_objectid
    else :
        plugin_objectid = existing[pluginid]

    # Recuperation du host
    if not hostname in existinghost :
        r = get_host(hostname)
        if r!= None :
            print("Host %s existant" %hostname)
            host_objectid = r["id"]
            ip_id = get_create_update_ip(hostname)
            update_host(host_objectid, {"last_scan" : date, "ip" : ip_id})
        # Creation du host si inexistant
        else :
            print("Creation du host " + hostname)
            hostdata = {
                "name": hostname,
                "last_scan": date
            }
            ip_id = get_create_update_ip(hostname)
            hostdata["ip"] = ip_id
            host_objectid = create_host(hostdata)
            #existinghost[row["Host"]] = host_objectid
        
        existinghost[hostname] = {}
        existinghost[hostname]["id"] = host_objectid

        # Recuperation des vulnerabilites pour le host
        vulns = get_vuln(host_objectid)
        hosts_stack[hostname] = set()

        for x in vulns :
            # Creation de la stack
            plugin_id = x["plugin"]["plugin_id"]
            if x["status"] == "Active" :
                hosts_stack[hostname].add(plugin_id)
            existinghost[hostname][plugin_id] = x["id"]

    else : 
        host_objectid = existinghost[hostname]["id"]

    if row["Plugin ID"] in existinghost[hostname] :
        # update de la date, du status et de l'output
        update_vuln(existinghost[hostname][row["Plugin ID"]], {"last_seen" : date, "output" : output, "status" : "Active"})
        # retirer de la pile
        if row["Plugin ID"] in hosts_stack[hostname] :
            hosts_stack[hostname].remove(row["Plugin ID"])
        continue 
    else :
        print("Creation de la vuln " + hostname + ":" + str(row["Plugin ID"]))
        vulndata = {
            "host" : host_objectid,
            "plugin" : plugin_objectid,
            "status" : "Active",
            "first_seen" : date,
            "last_seen" : date,
            "output" : output,
        }
        if not pd.isna(row["Port"]) :
            vulndata["port"] = row["Port"]
            vulndata["protocol"] = row["Protocol"]  
        vuln_id = create_vuln(vulndata)
        existinghost[row["Host"]][row["Plugin ID"]] = vuln_id

print(count)

# Update du status des vulns non vues 
for key, value in hosts_stack.items() :
    for i in value :
        print(f"La vulnerability {i} n'a plus ete vue")
        vuln_id = existinghost[key][i]
        update_vuln(vuln_id, {"status" : "Inactive"})