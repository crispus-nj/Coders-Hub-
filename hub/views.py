from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from django.db.models import Q
from hub.models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, UserCreationForm


def home(request):
    q = request.GET.get('t') if request.GET.get('t')  !=None else ''
    print(q)
    rooms = Room.objects.filter( Q(topic__name__icontains=q) | 
                                 Q(name__icontains=q) |
                                 Q(description__icontains = q)
                                 )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    topic_count = topics.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)).order_by('-date_created')
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages':room_messages, 'topic_count':topic_count}
    return render(request, 'hub/home.html', context)

def room(request, pk):
    room = Room.objects.get(pk=pk)
    room_messages = room.message_set.all().order_by('-date_created')
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('rooms', pk=room.id)


    context = {'pk':pk, 'room': room,'room_messages':room_messages, 'participants':participants}
    return render(request, 'hub/room.html', context)

@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(pk=pk)
    # print("this is a message", message)
    if request.user != message.user:
        return HttpResponse('You can not delete that message! Check your account and try again')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request,'hub/delete.html', {'object': message})

@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic , created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     form = form.save(commit=False)
        #     form.host = request.user 
        #     form.save()
        return redirect('home')
    context = {'topics':topics, 'form':form}
    return render(request, 'hub/create_room.html', context)

@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    # print(form)
    if request.user != room.host:
        return HttpResponse("You can not edit this room!. Please check your account name and try again!")
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic , created = Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()

        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        return redirect('home')
    context = {'topics':topics,'form':form, 'room':room}
    return render(request, 'hub/create_room.html', context)

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    # print(room)
    if request.user != room.host:
        return HttpResponse("You can not delete this room! Check your account status and try again!")

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    return render(request, 'hub/delete.html', {'object': room})

def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.filter(email=email)
        except:
            messages.error(request, 'User does not exist!')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else: 
            messages.error(request, 'Email Or Password is incorrect!')
    context = { 'page':page} 
    return render(request, 'hub/login_register.html', context)

def register_page(request):
    page = 'register'
    form = UserCreationForm()
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # print("user majina", user.username)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else: 
            messages.error(request, 'An error Occured!')

    context = {'page': page, 'form': form}
    return render(request, 'hub/login_register.html', context)

def log_out(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    topic_count = topics.count()
    context = {'user':user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics, 'topic_count':topic_count}
    return render(request, 'hub/profile.html', context)

@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES ,instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)

    context = {'form': form}
    return render(request, 'hub/update_user.html', context)

def topics(request):
    t = request.GET.get('t') if request.GET.get('t') != None else ''
    topics = Topic.objects.filter(name__icontains = t)
    # for topic in topics:
    #     print(type(topic))
    context = {'topics': topics}
    return render(request, 'hub/topics.html', context)

def activity(request):
    room_messages = Message.objects.all()
    context = {'room_messages':room_messages}
    return render(request, 'hub/activity.html', context)