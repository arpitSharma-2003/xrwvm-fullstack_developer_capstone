import json
import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import CarMake, CarModel
from .populate import initiate
from .restapis import (
    analyze_review_sentiments,
    get_request,
    post_review,
    searchcars_request,
)

logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]

    user = authenticate(username=username, password=password)

    response_data = {"userName": username}
    if user is not None:
        login(request, user)
        response_data = {
            "userName": username,
            "status": "Authenticated",
        }

    return JsonResponse(response_data)


def logout_request(request):
    logout(request)
    return JsonResponse({"userName": ""})


@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]
    first_name = data["firstName"]
    last_name = data["lastName"]
    email = data["email"]

    try:
        User.objects.get(username=username)
        return JsonResponse(
            {
                "userName": username,
                "error": "Already Registered",
            }
        )
    except User.DoesNotExist:
        logger.debug("%s is new user", username)

    user = User.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password,
        email=email,
    )
    login(request, user)
    return JsonResponse({"userName": username, "status": "Authenticated"})


def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state

    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_reviews(request, dealer_id):
    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Bad Request"})

    endpoint = "/fetchReviews/dealer/" + str(dealer_id)
    reviews = get_request(endpoint)

    for review_detail in reviews:
        sentiment_response = analyze_review_sentiments(review_detail["review"])
        review_detail["sentiment"] = sentiment_response["sentiment"]

    return JsonResponse({"status": 200, "reviews": reviews})


def get_dealer_details(request, dealer_id):
    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Bad Request"})

    endpoint = "/fetchDealer/" + str(dealer_id)
    dealership = get_request(endpoint)
    return JsonResponse({"status": 200, "dealer": dealership})


def add_review(request):
    if request.user.is_anonymous:
        return JsonResponse({"status": 403, "message": "Unauthorized"})

    data = json.loads(request.body)
    try:
        post_review(data)
        return JsonResponse({"status": 200})
    except Exception:
        return JsonResponse(
            {
                "status": 401,
                "message": "Error in posting review",
            }
        )


def get_cars(request):
    if CarMake.objects.count() == 0:
        initiate()

    car_models = CarModel.objects.select_related("car_make")
    cars = [
        {"CarModel": cm.name, "CarMake": cm.car_make.name}
        for cm in car_models
    ]
    return JsonResponse({"CarModels": cars})


def get_inventory(request, dealer_id):
    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Bad Request"})

    data = request.GET
    dealer_id_str = str(dealer_id)

    if "year" in data:
        endpoint = f"/carsbyyear/{dealer_id_str}/{data['year']}"
    elif "make" in data:
        endpoint = f"/carsbymake/{dealer_id_str}/{data['make']}"
    elif "model" in data:
        endpoint = f"/carsbymodel/{dealer_id_str}/{data['model']}"
    elif "mileage" in data:
        endpoint = f"/carsbymaxmileage/{dealer_id_str}/{data['mileage']}"
    elif "price" in data:
        endpoint = f"/carsbyprice/{dealer_id_str}/{data['price']}"
    else:
        endpoint = f"/cars/{dealer_id_str}"

    cars = searchcars_request(endpoint)
    return JsonResponse({"status": 200, "cars": cars})s": cars})
