from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer


@api_view(["GET"])
def getRoutes(request):
    routes = [
        "GET /api",
        "GET /api/rooms/",
        "GET /api/rooms/<str:pk>/",
        "POST /api/rooms/",
        "PUT /api/rooms/<str:pk>/",
        "DELETE /api/rooms/<str:pk>/",
        "GET /api/messages/",
        "GET /api/messages/<str:pk>/",
        "POST /api/messages/",
        "PUT /api/messages/<str:pk>/",
        "DELETE /api/messages/<str:pk>/",
        "GET /api/users/",
        "GET /api/users/<str:pk>/",
        "POST /api/users/",
        "PUT /api/users/<str:pk>/",
        "DELETE /api/users/<str:pk>/",
    ]

    return Response(routes)


@api_view(["GET"])
def getRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def getRoom(request, pk):
    rooms = Room.objects.get(id=pk)
    serializer = RoomSerializer(rooms, many=False)
    return Response(serializer.data)
