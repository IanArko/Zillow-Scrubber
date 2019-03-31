from bs4 import BeautifulSoup
import requests
import get
import pandas as pd

#Setup the mining operation
ZWSID = "ENTER_YOUR_ZWSID"

#TODO: Automate the photo collection. NEED A ROTATING IP
photoPath = ["./photos/437-Tune-Dr/", "./photos/211-Elizabeth-St/", "./photos/8005-Potomac-Dr/"]

#Data was just chosen randomly from Zillow. Format:       Address | City,State
#                                                        ---------|-------------
#                                            11037 John Smith Dr. | Springfield, ?
#
propertyList = pd.read_csv("data.csv")

#Get the size of the data input so that the for loop knows when to stop
header = list(propertyList.columns.values)
dimensions = propertyList.shape
height = dimensions[0]
width = dimensions[1]

#for each home in the csv
for i in range(0, height):
    addressData = propertyList[header[0]][i].split(" ")
    houseNumber = str(addressData[0])
    streetName  = str(addressData[1])

    # The following if and for allow the program to be robust enough to handle
    # streets with multiple-word names (eg. "john smith dr.") and to also
    # work with apartments (eg. "15 Jones St APT 4E").
    if len(addressData) > 2:
        for j in range(2, len(addressData)):
            streetName += "-" + addressData[j]

    cityData = propertyList[header[1]][i].split(", ")
    cityName = cityData[0]
    cityName.replace(" ", "-")
    state    = cityData[1]

    url = "http://www.zillow.com/webservice/GetSearchResults.htm?zws-id=" + ZWSID + "&address=" + houseNumber + "+" + streetName + "+St&citystatezip=" + cityName+ "%2C+" + state
    print(url)
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    homeDetailsSoup = get.homeDetailsPage(soup)
    metaSentence = get.metaSentence(soup)

    # The following while loop elminates unexpected returns zillow gives,
    # which are used presumably to make the scaper break
    while "Zillow" not in str(metaSentence[0]):
        url = "http://www.zillow.com/webservice/GetSearchResults.htm?zws-id=" + ZWSID + "&address=" + houseNumber + "+" + streetName + "+St&citystatezip=" + cityName+ "%2C+" + state
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        homeDetailsSoup = get.homeDetailsPage(soup)
        metaSentence = get.metaSentence(soup)

    # Below was how I intended to get the images for the AutoML, but I won't be
    # able to since they are blocking me from pinging for the data I need
    #TODO: Rotating IP
    #--------------------------------------------------------------------------
    #zipCode = get.zipCode(metaSentence)
    #imageUrl = "https://www.zillow.com/homedetails/" + houseNumber + "-" + streetName + "-" + cityName.replace(" ", "-") + "-" + state.replace(" ", "-") + "-" + zipCode + "/" + get.zpid(soup) + "_zpid/?fullpage=true"
    #imagePage = requests.get(imageUrl)
    #imageSoup = BeautifulSoup(imagePage.text, "html.parser")
    #imageSoup.find_all("photo-tile-image")


    sqft = get.sqft(metaSentence)
    print("The hosue you requested data for has " + get.bed(metaSentence) + " bedrooms and " + get.bath(metaSentence) + " bathrooms.")
    print("The house is " + sqft+ " square feet.")
    print("The price is  $" + get.listPrice(metaSentence) + " dollars.")
    print("We suspect it will need "+ get.repair(photoPath[i], sqft) +" dollars of repair")
    print("                                            ")

    #Removing MLS test due to inconsisencies in data availabiliity
    #------------------------------------------------------
    #print("Mls is " + get.mls(metaSentence) + ".")
