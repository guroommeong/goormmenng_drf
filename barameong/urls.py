from django.urls import path
from .views import matchingAIAPIView, CompleteReservationAPIView, FindDogAPIView

urlpatterns = [
    path('match/', matchingAIAPIView.as_view(), name='match'),
    path('complete/', CompleteReservationAPIView.as_view(), name='reservation'),
    path('find/', FindDogAPIView.as_view(), name='find'),
]