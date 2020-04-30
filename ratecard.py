import urllib.request
import json
import glob

# OCI Ratecard
# created by Richard Garsthagen - richard@oc-blog.com
# Disclaimer: This is not an official Oracle Tool

# Set to match your accounts currency, like USD or EUR
currency = "EUR"

files =  glob.glob("reports_cost-*.csv")
rates = []

for file in files:
    print ("Processing file: {}".format(file))
    data = open(file, "r")
    c = 0

    first = True
    for line in data:
        if not first:
            #print (line)
            items = line.split(",")
            sku = items[13]
            subscription = items[12]
            service = items[4]
            description = items[14]
            unitcost = items[15]
            unitcostextra = items[16]
            #print ("{} - {} {} - {} {}".format(subscription, sku, service, description, unitcost, unitcostextra))

            found = False
            for r in rates:
                if (r[1] == sku) and (r[0] == subscription):
                    found = True

            if not found:
                listpriceurl = "https://itra.oraclecloud.com/itas/.anon/myservices/api/v1/products?partNumber={}".format(sku)
                hdr = { 'X-Oracle-Accept-CurrencyCode':  currency}
                req = urllib.request.Request(listpriceurl, headers= hdr)
                r = urllib.request.urlopen(req).read()
                cont = json.loads(r.decode('utf-8'))
                prices = cont["items"][0]["prices"]
                PAYG = 0
                MFLEX = 0
                for p in prices:
                    print (p)
                    if float(p["value"]) != 0:
                        if p["model"] == "PAY_AS_YOU_GO":
                            PAYG = float(p["value"])
                        if p["model"] == "MONTHLY_COMMIT":
                            MFLEX = float(p["value"])

                rates.append([subscription, sku, service, description, unitcost, unitcostextra, PAYG, MFLEX])
        else:
            first = False

ratecard = open("ratecard.csv", "w")
ratecard.write("subscription, sku, service, description, unitcost, unitcostextra, PAYG, MFLEX\n")
for r in rates:
    ratecard.write("{},{},{},{},{},{},{},{}\n".format(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7]))

ratecard.close()



