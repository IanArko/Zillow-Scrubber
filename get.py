from bs4 import BeautifulSoup
import requests
import sys
from google.cloud import automl_v1beta1
from google.cloud.automl_v1beta1.proto import service_pb2
import os



headers = requests.utils.default_headers()
headers.update({
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.149 Safari/537.36',
})

def zpid(soup):
    zpidSearch = soup.find_all("zpid")
    zpidSearch = str(zpidSearch)
    zpid = ""
    for letter in zpidSearch:
        if letter.isdigit():
            zpid += letter
    return zpid

def metaSentence(soup):
    homeDetailsSoup = homeDetailsPage(soup)
    metaSearch = homeDetailsSoup.find_all("meta")
    metaData = str(metaSearch[2]) #
    metaSentence = metaData.split('.')
    return metaSentence

def homeDetailsPage(soup):
    detailsUrl = homeDetailsUrl(soup)
    page = requests.get(detailsUrl, headers = headers)
    homeDetailsSoup = BeautifulSoup(page.text, "html.parser")
    return homeDetailsSoup

def homeDetailsUrl(soup):
    details = soup.find_all("homedetails")
    #parse out the webaddress by splitting on the brackets -- Does anybody know a better way to do this?
    detailsUrl = str(details).split(">")[1].split("<")[0]
    return detailsUrl

#Returns the listed price of the property
def listPrice(metaSentence):
    return metaSentence[0].split("$")[1].split(" ")[0]

#Returns the number of sqare feet. Beware, it leaves commas: "1,900"
def sqft(metaSentence):
    sqft = metaSentence[1].split(" ")[2].split(",")
    realSqft = 0
    #sqft returned as a list of 1 to 2 elements, so we'll reduce it to just 1 nubmer
    if len(sqft) > 1:
        realSqft = sqft[0] + sqft[1]
    else :
        realSqft = sqft[0]
    return realSqft

#Returns the number of bedrooms
def bed(metaSentence):
    bed = metaSentence[0].split("$")[1].split(" ")[1]
    return bed

def zipCode(metaSentence):
    zipCode = metaSentence[1].split(",")[4].split(" ")[2]
    return zipCode

#Returns the number of bathrooms
def bath(metaSentence):
    return metaSentence[0].split("$")[1].split(" ")[3]

#Returns the MLS listing number. Beware, not ever house has an MLS listing. Consider not using unless needed.
def mls(metaSentence):
    mls = metaSentence[2].split("MLS # ")[1]
    return mls

# Sends photo to Google Cloud AutoML API and Returns the ranking of how much work the house needs from 1 to 5 from 
# 1 Total gut, 5 perfect
def ranking(file_path):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'auth.json'
    project_id = "YOUR_PROJECT_ID"
    model_id = "YOUR_MODEL_ID"

    with open(file_path, 'rb') as ff:
        content = ff.read()

    prediction_client = automl_v1beta1.PredictionServiceClient()

    name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
    payload = {'image': {'image_bytes': content }}
    params = {}
    request = prediction_client.predict(name, payload, params)
    request = str(request)
    if ("display_name" in request):
        score = request.split("display_name: \"")[1][0]
        return score
    else:
        #if the model returns no score, return a 5 since we're unsure if we'll add to
        # the repair cost
        return "3"


def repair(photoPath, sqft):
    sum = 0
    for i in range(1, 11):
        wholePath = photoPath + str(i) + ".jpg"
        rank = int(ranking(wholePath))
        sum = sum + rank
        #Below are previous test Statements
        #print("The " + str(i) + " sum is " + str(sum))
        #print(sum)

    average = sum / 10
    #print(average)

    #Repair cost numbers are just round estimates from a real estate blog
    repairCost = 0
    if   0 <= average < 2:
        repairCost = 40
    elif 2 <= average < 3:
        repairCost = 30
    elif 3 <= average < 4:
        repairCost = 20
    elif 4 <= average <= 5:
        repairCost = 0

    return str(repairCost * int(sqft))


#retrieve the link used to download images. Will be used to send images to image classifier.
def houseImages(homeDetailsSoup):
    htmlClass  =  "hdp-photo-carousel"
    imageHTML  = homeDetailsSoup.find_all("div", {"class": htmlClass})
    imageLinks = imageHTML[0].find("div", {"class": "photo-tile-image"})
    return imageLinks


#Method synonyms to make the package more user friendly
#--------------------------------------------------------------------
def price(metaSentence):
    return listPrice(metaSentence)
def housePrice(metaSentence):
    return listPrice(metaSentence)
def homePrice(metaSentence):
    return listPrice(metaSentence)
def numberOfBed(metaSentence):
    return bed(metaSentence)
def bedroom(metaSentence):
    return bed(metaSentence)
def bedroomCount(metaSentence):
    return bed(metaSentence)
def numBed(metaSentence):
    return bed(metaSentence)
def numBeds(metaSentence):
    return bed(metaSentence)
def mlsNubmer(metaSentence):
    return mls(metaSentence)
