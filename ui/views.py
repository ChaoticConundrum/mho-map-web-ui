from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# from ui import psbsocket
from ui import mockpsbsocket

# psbsocket = psbsocket.PSBSocket()
psbsocket = mockpsbsocket.MockPSBSocket()


def index(request):
    context = {}
    return render(request, 'ui/index.html', context)


def psb_version(request):
    return JsonResponse(psbsocket.get_psb_version())


def data_range(request, start, end):
    return JsonResponse(psbsocket.get_data_range(
        request.GET.getlist('id'), int(start), int(end)))


def current_data(request, device_id):
    return JsonResponse(psbsocket.get_current_data(device_id))


def topology(request):
    return JsonResponse(psbsocket.get_topology())


def devices(request):
    return JsonResponse(psbsocket.get_devices())


def drivers(request):
    return JsonResponse(psbsocket.get_drivers())


# TODO fix this
@csrf_exempt
def device(request):
    print(request)
    if request.method == "POST":
        return JsonResponse(psbsocket.add_device(request.POST))

    return JsonResponse({})
