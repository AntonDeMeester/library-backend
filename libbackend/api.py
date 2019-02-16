from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import json
import ast

from .analyse import get_isbn_from_barcode, get_google_volume_from_isbn
from .models import Book
from .serializers import GoogleVolumeSerializer

@csrf_exempt
def register(request):
    photo = request.FILES.get('image')
    isbn = get_isbn_from_barcode(request.FILES.get('image', False))
    if isbn != -1:
        google_volume = get_google_volume_from_isbn(isbn)
        google_volume = json.loads(google_volume)
        if google_volume.get("totalItems", 0) == 0:
                return HttpResponse("Book not found in Google Books API")
        #print("Google volume data is " + str(google_volume.get("items", [])))
        for volume in google_volume.get("items", []):
            volume_serialiser = GoogleVolumeSerializer(data=volume)
            if volume_serialiser.is_valid(raise_exception=True):
                book = volume_serialiser.save()
                return HttpResponse("Book found: " + str(book))
    return HttpResponse("Not found")