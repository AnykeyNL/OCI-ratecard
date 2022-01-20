import argparse
import sys
import requests, json
import csv

# Get Command Line Parser
parser = argparse.ArgumentParser()
parser.add_argument('-f', default="", dest='ratecard_file', help='Ratecard file in csv format to use')

cmd = parser.parse_args()
if cmd.ratecard_file == "":
    parser.print_help()
    sys.exit(0)

print ("Loading ratecard file...")
newfile = []
ratecard = []
with open(cmd.ratecard_file, "r") as csvfile:
    csvreader = csv.reader(csvfile)

    # This skips the first 5 row of the CSV file.
    for x in range(4):
        newfile.append(next(csvreader))
    # Add discount to field list
    fields = next(csvreader)
    fields.append("discount")
    newfile.append(fields)

    for row in csvreader:
        ratecard.append(row)

    currency = ratecard[0][3]

print ("Getting public rates for currency {}".format(currency))
url = requests.get("https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/?currencyCode={}".format(currency))
public_rates_raw = json.loads(url.text)
public_rates = public_rates_raw["items"]

print ("Creating ratecard file with discount specification...")

for rate in ratecard:
    sku = rate[0].split(" ")[0]
    discount = "n/a"
    for public_rate in public_rates:
        if public_rate["partNumber"] == sku:
            price = public_rate["currencyCodeLocalizations"][0]["prices"][0]["value"]
            if float(price) != 0:
                discount =  1-(float(rate[4]) / float(price))
            else:
                discount = 0
    rate.append(str(discount))

filenameparts = cmd.ratecard_file.split(".")
newratefile = filenameparts[0] + "_withDiscount." + filenameparts[1]

with open(newratefile, 'w', newline="") as file:
    csvwriter = csv.writer(file, quoting=csv.QUOTE_ALL)
    for l in newfile:
        csvwriter.writerow(l)
    for r in ratecard:
        csvwriter.writerow(r)

























