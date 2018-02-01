import os
import json
import requests
import sys
import urllib
import shutil
from PIL import Image
from pprint import pprint

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
q = myargs['-q']
pages = myargs['-p'] if '-p' in myargs else 10
fileType = myargs['-f'] if '-f' in myargs else 'jpg'

# Set up .cache directory
# Google limits requests to 100 a day for the free tier,
# so we should cache any json responses we get so as not
# to abuse it

def makeDirectoryIfNotExisting(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

makeDirectoryIfNotExisting('.cache')
makeDirectoryIfNotExisting('images')

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
        return data

    data = makeAPIRequest(q, offset, fileType)

    with open(path, 'w') as outfile:
        json.dump(data, outfile)

    return data

def getListOfImagesFromData(data):
    return [i['link'] for i in data['items']]

def getListOfImagesFromAPI(q, fileType, page=0):
    data = getData(q, page, fileType)
    return getListOfImagesFromData(data)

def getImagesURLs(q, fileType, pages):
    images = []

    for i in range(int(pages)):
        images = images + getListOfImagesFromAPI(q, fileType, i)

    return images

def saveImageURLs(urls, query, fileType):
    for index in range(len(urls)):
        path = "{query}.{index}".format(query=query, index=index + 1)
        saveImageURL(path, urls[index], fileType)

def saveImageURL(path, url, ext):
    response = requests.get(url, stream=True)
    file = "images/{path}.{ext}".format(ext=ext, path=path)
    with open(file, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

def getImages(q, fileType, pages):
    urls = getImagesURLs(q, fileType, pages)
    saveImageURLs(urls, q, fileType)
    return urls

getImages(q, fileType, pages)
