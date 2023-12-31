from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from .models import Room, Topic, Message
from .forms import RoomForm, UserForm


# Create your views here.


def loginPage(request):
    page = "login"

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")

        # try:
        #     user = User.objects.get(username=username)
        # except:
        #     messages.error(request, "User does not exist")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Username or Password does not exist")

    return render(request, "base/login_register.html", {"page": page})


def logoutUser(request):
    logout(request)
    return redirect("login")


def registerPage(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            # ! commit=False means that we don't want to save the user to the database yet.
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An error occurred during registration")

    return render(request, "base/login_register.html", {"form": form})


def home(request):
    q = request.GET.get("q") if request.GET.get("q") is not None else ""

    # ! __ is used to access the field of the model
    # ! icontains is used to perform case-insensitive containment test
    # ! Q is used to combine multiple queries
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )

    # ! [0:5] is used to get the first 5 topics from the database
    topics = Topic.objects.all()[0:5]
    topic_count = topics.count()
    room_count = rooms.count()

    # ! [:5] is used to get the last 5 messages from the database
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)).order_by(
        "-created"
    )[:5]

    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages,
        "topic_count": topic_count,
    }

    return render(request, "base/home.html", context)


def room(request: HttpRequest, room_id: int) -> HttpResponse:
    room = Room.objects.get(id=room_id)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            room=room, user=request.user, body=request.POST.get("body")
        )
        room.participants.add(request.user)

        return redirect("room-url", room_id=room_id)

    return render(
        request,
        "base/room.html",
        {"room": room, "room_messages": room_messages, "participants": participants},
    )


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_message = user.message_set.all()

    topics = Topic.objects.all()
    topic_count = topics.count()
    room_count = rooms.count()

    context = {
        "user": user,
        "rooms": rooms,
        "room_messages": room_message,
        "topics": topics,
        "room_count": room_count,
        "topic_count": topic_count,
    }

    return render(request, "base/profile.html", context)


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        # ! get_or_create() returns a tuple of (object, created),
        # ! where object is the retrieved or created object
        # ! and created is a boolean specifying whether a new object was created.
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )
        return redirect("home")

    return render(request, "base/room_form.html", {"form": form, "topics": topics})


@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    # ! instance is used to pre-populate the form with the data from the database
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed here")

    if request.method == "POST":
        # form = RoomForm(request.POST, instance=room)

        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name = request.POST.get("name")
        room.description = request.POST.get("description")
        room.save()
        # if form.is_valid():
        #     form.save()
        return redirect("home")

    return render(
        request, "base/room_form.html", {"room": room, "form": form, "topics": topics}
    )


@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.method == "POST":
        room.delete()
        return redirect("home")

    return render(request, "base/delete.html", {"obj": room})


@login_required(login_url="login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed here")

    if request.method == "POST":
        message.delete()
        return redirect("home")

    return render(request, "base/delete.html", {"obj": message})


@login_required(login_url="login")
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)
    return render(request, "base/update_user.html", {"form": form})


def topicPage(request):
    q = request.GET.get("q") if request.GET.get("q") is not None else ""

    topics = Topic.objects.filter(name__icontains=q)
    return render(request, "base/topic.html", {"topics": topics})


def activityPage(request):
    room_messages = Message.objects.all().order_by("-created")
    return render(request, "base/activity.html", {"room_messages": room_messages})
