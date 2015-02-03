from django.contrib import admin

from . import models


class ThingAdmin(admin.ModelAdmin):
    fields = ('name', 'approved', 'behavior', 'verb', 'creator', 'created', 'modified',)
    list_display = ('behavior', 'verb', 'name', 'approved',)
    readonly_fields = ('slug', 'creator', 'created', 'modified',)


class InlineMotivePeriod(admin.TabularInline):
    model = models.MotivePeriod
    extra = 0


class UserMotiveAdmin(admin.ModelAdmin):
    inlines = (InlineMotivePeriod,)
    fields = ('user', 'thing', 'amount', 'duration', 'created', 'modified',)
    readonly_fields = ('user', 'thing', 'created', 'modified',)


class IncidentAdmin(admin.ModelAdmin):
    fields = ('motive',)
    list_display = ('motive',)
    readonly_fields = ('motive',)


admin.site.register(models.Thing, ThingAdmin)
admin.site.register(models.UserMotive, UserMotiveAdmin)
admin.site.register(models.Incident, IncidentAdmin)
