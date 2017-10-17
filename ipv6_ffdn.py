import subprocess

import requests
from jinja2 import Template


result = []

for isp in requests.get("https://db.ffdn.org/api/v1/isp/?per_page=9999").json()["isps"]:
    if not isp["is_ffdn_member"]:
        continue

    name = isp['ispformat']['name']

    if 'website' not in isp['ispformat']:
        print "WARNING: %s doesn't have a website in its isp.json" % name
        result.append({
            "name": name,
            "has_ipv6": None,
            "has_ipv6_mail": None,
            "mx_if_other": "",
        })
        continue

    website = isp['ispformat']['website']

    domain = ".".join(website.split("/")[2].split(".")[-2:])
    print "====", domain, "(%s)" % website, "===="

    # print domain, "has ipv6?", bool(subprocess.check_output(["dig", "AAAA", domain, "+short"]).strip()), subprocess.check_output(["dig", "AAAA", domain, "+short"]).strip()
    print "ipv6", [subprocess.check_output(["dig", "AAAA", domain, "+short"]).strip()]
    has_ipv6 = bool(subprocess.check_output(["dig", "AAAA", domain, "+short"]).strip())

    mail_domains = []
    # (ve) psycojoker@dolgoff ~/code/python/ipv6_ffdn dig MX neutrinet.be +short
    # 50 mail.neutri.net.
    has_ipv6_mail = False
    for i in filter(None, subprocess.check_output(["dig", "MX", domain, "+short"]).split("\n")):
        mail_domain = i.split(" ")[1][:-1]
        mail_domains.append(mail_domain)
        print mail_domain, "has ipv6?", bool(subprocess.check_output(["dig", "AAAA", domain, "+short"]).strip()), subprocess.check_output(["dig", "AAAA", domain, "+short"]).strip()
        if bool(subprocess.check_output(["dig", "AAAA", domain, "+short"]).strip()):
            has_ipv6_mail = True

    # if there is no mail domain that is similar to the isp domain
    if not len([x for x in mail_domains if x.endswith(domain)]) and mail_domains:
        mx_if_other = ".".join([x for x in mail_domains if not x.endswith(domain)][0].split(".")[-2:])
    else:
        mx_if_other = ""

    result.append({
        "name": name,
        "has_ipv6": has_ipv6,
        "has_ipv6_mail": has_ipv6_mail,
        "mx_if_other": mx_if_other,
    })



template = Template(open("template.doku").read().decode("Utf-8"))
print template.render(isps=sorted(result, key=lambda x: x["name"].lower()))
