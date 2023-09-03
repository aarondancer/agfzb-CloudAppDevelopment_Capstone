from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarModel
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
from .restapis import post_request, get_dealers_from_cf, get_dealer_reviews_by_id_from_cf, get_dealer_by_id_from_cf
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/djangoapp')
        else:
            return render(request, 'djangoapp/user_login.html', context)

# Create a `logout_request` view to handle sign out request


def logout_request(request):
    logout(request)
    return redirect('/djangoapp')

# Create a `registration_request` view to handle sign up request


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']

        user = User.objects.create_user(
            username=username, password=password, first_name=first_name, last_name=last_name)
        
        login(request, user)
        return redirect("/djangoapp")


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://aaronadancer-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        dealerships = get_dealers_from_cf(url)
        context = {"dealerships": dealerships}
        return render(request, 'djangoapp/index.html', context)
        

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        context = {}
        dealer_url = "https://aaronadancer-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        dealer = get_dealer_by_id_from_cf(dealer_url, id=dealer_id)
        context["dealer"] = dealer

        url = 'https://aaronadancer-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews'
        context["reviews"] = get_dealer_reviews_by_id_from_cf(url, dealer_id)
    return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    dealer_url = "https://aaronadancer-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
    dealer = get_dealer_by_id_from_cf(dealer_url, id=dealer_id)
    context["dealer"] = dealer
    if request.method == 'GET':
        cars = CarModel.objects.all()
        context["cars"] = cars
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST' and request.user.is_authenticated:
        username = request.user.username
        print(request.POST)
        review = dict()
        car_id = request.POST["car"]
        car = CarModel.objects.get(pk=car_id)
        review["time"] = datetime.utcnow().isoformat()
        review["name"] = username
        review["dealership"] = dealer_id
        review["id"] = dealer_id
        review["review"] = request.POST["content"]
        review["purchase"] = False
        if "purchasecheck" in request.POST:
            if request.POST["purchasecheck"] == 'on':
                review["purchase"] = True
        review["purchase_date"] = request.POST["purchasedate"]
        review["car_make"] = car.carmake.name
        review["car_model"] = car.name
        review["car_year"] = int(car.year.strftime("%Y"))

        json_payload = {}
        json_payload["review"] = review
        review_post_url =  "https://aaronadancer-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"
        post_request(review_post_url, json_payload, id=dealer_id)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)