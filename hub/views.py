from django.shortcuts import render, redirect
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