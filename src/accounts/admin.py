from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(Profile),
admin.site.register(Solution),
admin.site.register(Project),
admin.site.register(Component),
admin.site.register(Scan),
admin.site.register(Release),
admin.site.register(ScanDetails)
