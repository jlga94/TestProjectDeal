from bs4 import BeautifulSoup
import csv, string, sys
import requests
import re
import pandas as pd

def getTextColumn(soupTextElement):
	return soupTextElement.text.strip()

def getUrlImageColumn(soupImageElement):
	return soupImageElement["src"]

def getSizesColumn(soupSizesElement):
	#print(soupSizesElement)
	sizes = []
	sizeNumberIndex = 0

	soupSizes = soupSizesElement.find_all("option")
	for indexSize in range(1,len(soupSizes)):
		sizeText = soupSizes[indexSize].text.strip()
		sizeText = sizeText.split("-")[sizeNumberIndex].strip()
		sizes.append(sizeText)

	return sizes


def getDetailsProduct(domainUrl,productUrl,headers,ubicationsColumns):
	html_text = requests.get(domainUrl + productUrl, headers=headers).text
	soup = BeautifulSoup(html_text, 'lxml')

	dataColumns = {}

	for columnName in ubicationsColumns.keys():
		soupColumn = soup.find(ubicationsColumns[columnName]["tag"],ubicationsColumns[columnName]["attributes"])
		#print(soupColumn)
		if ubicationsColumns[columnName]["type"] == 'text':
			dataColumns[columnName] = getTextColumn(soupColumn)

		elif ubicationsColumns[columnName]["type"] == 'urlImage':
			dataColumns[columnName] = domainUrl + getUrlImageColumn(soupColumn)

		elif ubicationsColumns[columnName]["type"] == 'list':
			dataColumns[columnName] = getSizesColumn(soupColumn)

		else:
			#Error Case
			dataColumns[columnName] = None

		#print(dataColumns)


	return dataColumns



def downloadProducts(dfProducts,domainUrl,sectionUrl,headers,ubicationsColumns):
	html_text = requests.get(domainUrl + sectionUrl, headers=headers).text
	soup = BeautifulSoup(html_text, 'lxml')

	#print(len(soup.find_all("div", {"class": "product-grid"})))

	for productSoup in soup.find_all("div", {"class": "product-grid"}):
		productUrl = productSoup.find("a")["href"]
		#print(domainUrl + productUrl)
		dataColumns = getDetailsProduct(domainUrl,productUrl,headers,ubicationsColumns)
		dataColumns["URL"] = domainUrl + productUrl

		print(dataColumns)


	return dfProducts


def main():
	domainUrl = 'https://www.lobstersnowboards.com'
	sectionUrl = '/shop/'
	headers = {
		"Cookie": "some_name=q38nrf2c5jq5f9h9rvvutt6pq7; site_language_id=1; _ga=GA1.2.1763790134.1524064374; _gid=GA1.2.869635978.1524064374; _gat=1; site_country_id=26",
	}

	columnsCSV = ["URL","Name","Image","Price","Sizes"]

	ubicationsColumns = {
		"Name":{
			"tag":"h1",
			"attributes":{
				"class":"product-title"
			},
			"type":"text"
		},
		"Image":{
			"tag":"img",
			"attributes":{
				"class":"img-responsive"
			},
			"type":"urlImage"
		},
		"Price":{
			"tag":"div",
			"attributes":{
				"class":"product_price"
			},
			"type":"text"
		},
		"Sizes":{
			"tag":"select",
			"attributes":{
				"name":"size"
			},
			"type":"list"
		}
	}

	#print(ubicationsColumns)

	dfProducts = pd.DataFrame(columns=columnsCSV)

	dfProducts = downloadProducts(dfProducts,domainUrl,sectionUrl,headers,ubicationsColumns)

	

main()