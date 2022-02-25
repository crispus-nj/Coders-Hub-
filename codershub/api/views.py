from django.http import JsonResponse

def get_route(request):

    routes = [
        'GET api/',
        'GET api/rooms',
        'GET api/rooms/:id'
    ]
    return JsonResponse(routes, safe=False)