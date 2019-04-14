import requests
from pyzbar.pyzbar import decode #More info here: https://pypi.org/project/pyzbar/
from PIL import Image #Pillow for image reading

google_books_url = "https://www.googleapis.com/books/v1"

#data = decode(Image.open('.\libbackend\\barcode_example.gif'))
#print(str(data[0].data))

def get_isbn_from_barcode(input_image):
    if input_image:
        data = decode(Image.open(input_image))
        if data:
            isbn = data[0].data.decode('utf-8')
            print("Decoded image. ISBN is " + isbn)
            return isbn
    print("Couldn't decode image.")
    return -1

def get_google_volume_from_isbn(isbn):
    url = google_books_url + "/" + "volumes?q=" + "isbn:" + isbn
    print("Contacting Google books API at URL: " + url)
    response = requests.get(url)
    print("Got response of Google Books API. Status code: " + str(response.status_code))
    return response.text
