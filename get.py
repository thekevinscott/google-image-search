import os
import json
import requests
import urllib3
import sys
import cv2
import urllib
import shutil
from tqdm import tqdm
from PIL import Image
from pprint import pprint
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# https://gist.github.com/dideler/2395703
"""Collect command-line options in a dictionary"""

def getopts(argv):
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...
        if argv[0][0] == '-':  # Found a "-name value" pair.
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
    return opts

from sys import argv
myargs = getopts(argv)

def checkArg(arg, msg):
    if arg not in myargs:
        pprint(msg)
        exit()

checkArg('-q', 'Please pass a query with -q')
checkArg('-k', 'Please pass a key with -k')
checkArg('-c', 'Please pass a key with -c')

root = 'https://www.googleapis.com/customsearch/v1'

key = myargs['-k']
cx = myargs['-c']
q = (myargs['-q']).split(' ')
pages = myargs['-p'] if '-p' in myargs else 10
ext = myargs['-e'] if '-e' in myargs else 'jpg'
out = myargs['-out'] if '-out' in myargs else 'images'
fileName = myargs['-f'] if '-f' in myargs else q

# Set up .cache directory
# Google limits requests to 100 a day for the free tier,
# so we should cache any json responses we get so as not
# to abuse it

def makeDirectoryIfNotExisting(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

makeDirectoryIfNotExisting('.cache')
makeDirectoryIfNotExisting(out)

def makeAPIRequest(q, page, fileType, imgSize='medium'):
    # Defaults to 10 results per page
    results = 10
    offset = page * results + 1
    url = "{root}?key={key}&cx={cx}&fileType={fileType}&searchType=image&imgSize={imgSize}&num={num}&start={offset}&q={q}".format(root=root, key=key, cx=cx, imgSize=imgSize, num=results, offset=offset, q=q, fileType=fileType)
    response = requests.get(url)
    return response.json()

def getData(q, offset, fileType):
    path = ".cache/{q}-{offset}.json".format(q=q, offset=offset)
    if os.path.exists(path):
        data = json.load(open(path))
        if 'items' in data:
            return data

    data = makeAPIRequest(q, offset, fileType)

    if 'items' in data:
        with open(path, 'w') as outfile:
            json.dump(data, outfile)

        return data

    if 'error' in data:
        pprint(q)
        pprint(offset)
        pprint(data['error'])
        return data

    pprint("You have probably reached the max number of requests")
    pprint(data)

def getListOfImagesFromData(data):
    if 'items' in data:
        return [i['link'] for i in data['items']]

    return []

def getListOfImagesFromAPI(q, ext, page=0):
    data = getData(q, page, ext)
    if 'error' not in data:
        return getListOfImagesFromData(data)

    return data

def getImagesURLs(q, ext, pages):
    images = []

    for i in range(int(pages)):
        newImages = getListOfImagesFromAPI(q, ext, i)
        if 'error' in newImages:
            break

        images = images + newImages

    return images

def saveImageURLs(urls, query, ext):
    invalidImages = list()

    for index in tqdm(range(len(urls))):
        path = "{query}.{index}".format(query=query, index=index + 1)
        isValid = saveImageURL(path, urls[index], ext)
        if isValid is False:
            invalidImages.extend(path)

    if len(invalidImages) > 0:
        pprint("The following images were found to be invalid:")
        for file in invalidImages:
            pprint("{file}".format(file=file))

def saveImageURL(path, url, ext):
    response = requests.get(url, stream=True, verify=False)
    isValid = True

    if response.status_code == 200:
        file = "{out}/{path}.{ext}".format(ext=ext, path=path, out=out)
        with open(file, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

        if isInvalidImage(file):
            isValid = False
            os.remove(file)

    del response
    return isValid

def isInvalidImage(path):
    try:
        image = cv2.imread(path)
        if image is None:
            return True

    except:
        return True

    return False

def getImages(queries, ext, fileName, pages):
    urls = list()
    for q in queries:
        urls.extend(getImagesURLs(q, ext, pages))

    saveImageURLs(urls, fileName, ext)
    return urls

getImages(q, ext, fileName, pages)
