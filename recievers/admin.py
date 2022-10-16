from django.contrib import admin
from .models import Receiver
from import_export import resources
from import_export.fields import Field
# field niepotrzebne bo nie ma w modelu kluczy obcych
from import_export.admin import ExportActionMixin


class ReceiverResource(resources.ModelResource):
    class Meta:
        model = Receiver
        fields = ('id', 'name', 'address', 'website', 'created')
        export_order = ('website', 'created', 'name', 'id')


class ReceiverAdmin(ExportActionMixin, admin.ModelAdmin):
    resource_class = ReceiverResource


admin.site.register(Receiver, ReceiverAdmin)

# Register your models here.
