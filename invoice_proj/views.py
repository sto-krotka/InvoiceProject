from django.http import HttpResponse
from django.shortcuts import render

from invoices.models import Invoice


def test_view(request):
    obj = Invoice.objects.get(id=1)
    qs = Invoice.objects.all()
    print(obj.__dict__)
    print('*****')
    print(qs.query)
    return render(request, 'home.html', {'obj_': obj})



