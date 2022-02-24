from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from hub.models import Room, Topic
from .forms import RoomForm


def home(request):
    q = request.GET.get('t') if request.GET.get('t')  !=None else ''
    print(q)
    rooms = Room.objects.filter( Q(topic__name__icontains=q) | 
                                 Q(name__icontains=q) |
                                 Q(description__icontains = q)
                                 )
    topics = Topic.objects.all()
    room_count = rooms.count()
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}
    return render(request, 'hub/home.html', context)

def room(request, pk):
    room = Room.objects.get(pk=pk)
    
    return render(request, 'hub/room.html', {'pk':pk, 'room': room})

def create_room(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'hub/create_room.html', {'form':form})

def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    # print(form)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'hub/create_room.html', {'form': form})

def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    # print(room)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    return render(request, 'hub/delete.html', {'object': room})

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.filter(username=username)
        except:
            messages.error(request, 'User does not exist!')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else: 
            messages.error(request, 'Username Or Password is incorrect!')
    context = {}
    return render(request, 'hub/login_register.html', context)

def log_out(request):
    logout(request)
    return redirect('home')