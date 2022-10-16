from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, FormView, TemplateView, DetailView, UpdateView, RedirectView, DeleteView
from .models import Invoice
from profiles.models import Profile
from .forms import InvoiceForm
from django.contrib import messages
from positions.forms import PositionForm
from positions.models import Position
from .mixins import InvoiceNotClosedMixin
from django.contrib.auth.mixins import LoginRequiredMixin


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = "invoices/main.html"  # defaultowy adres to main.html
    paginate_by = 2
    context_object_name = 'qs'

    def get_queryset(self):
        # profile = Profile.objects.get(user=self.request.user)
        profile = get_object_or_404(Profile, user=self.request.user)
        # qs = Invoice.objects.filter(profile=profile).order_by('-created')
        # return qs
        return super().get_queryset().filter(profile=profile).order_by('-created')

    # default z ListView to Invoice.objects.all(), więc jeśli mamy wielu userów, i nie chce,y zeby wszystkie faktury sie
    # pojawiały trzeba cos nadpisać


class InvoiceFormView(LoginRequiredMixin, FormView):
    form_class = InvoiceForm
    template_name = 'invoices/create.html'
    # success_url = reverse_lazy('invoices:main')
    i_instance = None

    def get_success_url(self):
        return reverse('invoices:detail', kwargs={'pk': self.i_instance.pk})

    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        instance = form.save(commit=False)
        # żeby profil sie dodawal z automatu do formularza (instance.odwołanie do pola w modelu)
        instance.profile = profile
        form.save()
        self.i_instance = instance
        return super().form_valid(form)


class SimpleTemplateView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'invoices/simple_template.html'


# class SimpleTemplateView(TemplateView):
#     template_name = 'invoices/simple_template.html'

class AddPositionsFormView(LoginRequiredMixin, FormView):
    form_class = PositionForm
    template_name = 'invoices/detail.html'

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        invoice_pk = self.kwargs.get('pk')
        invoice_obj = Invoice.objects.get(pk=invoice_pk)
        instance = form.save(commit=False)
        instance.invoice = invoice_obj
        form.save()
        messages.info(self.request, f'Successfully added position- {instance.title}')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice_obj = Invoice.objects.get(pk=self.kwargs.get('pk'))
        qs = invoice_obj.positions
        context['obj'] = invoice_obj
        context['qs'] = qs
        return context


class InvoiceUpdateView(LoginRequiredMixin, InvoiceNotClosedMixin, UpdateView):
    model = Invoice
    template_name = 'invoices/update.html'
    form_class = InvoiceForm
    success_url = reverse_lazy('invoices:main')

    def form_valid(self, form):
        instance = form.save()
        messages.info(self.request, f'Successfully updated invoice- {instance.number}')
        return super().form_valid(form)


class CloseInvoiceView(LoginRequiredMixin, RedirectView):
    pattern_name = "invoices:detail"

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        obj = Invoice.objects.get(pk=pk)
        obj.closed = True
        obj.save()
        return super().get_redirect_url(*args, **kwargs)


class InvoicePositionDeleteView(LoginRequiredMixin, InvoiceNotClosedMixin, DeleteView):
    model = Position
    template_name = 'invoices/position_confirm_delete.html'

    # /<pk>/delete/<position_pk>/
    def get_object(self):
        pk = self.kwargs.get('position_pk')
        obj = Position.objects.get(pk=pk)
        return obj

    def get_success_url(self):
        messages.info(self.request, f'Deleted position- {self.object.title}')
        return reverse('invoices:detail', kwargs={'pk': self.object.invoice.id})


# converting to pdf:
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders


@login_required
def invoice_pdf_view(request, **kwargs):

    pk = kwargs.get('pk')
    obj = Invoice.objects.get(pk=pk)

    logo_result = finders.find('img/logo.png')
    font_result = finders.find('fonts/Lato-Regular.ttf')
    # show search location reults
    search_locations = finders.searched_locations
    print(search_locations)

    template_path = 'invoices/pdf.html'
    context = {
        'object': obj,
        'static': {
            'font': font_result,
            'logo': logo_result,
        },
    }
    # create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="invoice.pdf"'
    # find template and render it
    template = get_template(template_path)
    html = template.render(context)

    # create pdf
    pisa_status = pisa.CreatePDF(
        html.encode('utf-8'), dest=response, encoding='utf-8')

    # if case error
    if pisa_status.err:
        return HttpResponse('There are some errors <pre>' + html + '</pre>')
    return response
