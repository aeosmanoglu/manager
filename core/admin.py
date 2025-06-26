from django.contrib import admin
from unfold.admin import ModelAdmin


class DefaultAdmin(ModelAdmin):
    compressed_fields = True
    list_filter_submit = True
    
