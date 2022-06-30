from rest_framework.routers import SimpleRouter
from .views import *
from django.urls import path, include


router = SimpleRouter()
router.register("api/bid", BidViewSet, basename="bid")
# router.register("api/milestone", BidMileStoneViewSet, basename="milestone")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "api/user_bid_list",
        BidViewSet.as_view({"get": "user_bid_list"}),
        name="user_bid_list",
    ),
    path(
        "api/bids_on_job",
        BidViewSet.as_view({"post": "bids_on_job"}),
        name="bids_on_job",
    ),
    path(
        "api/mile_stone/<int:id>",
        BidMileStoneViewSet.as_view({"delete": "destroy"}),
        name="mile_stone",
    ),

]
