from django.contrib import admin
from .models import User, Person, PersonToUser, Action, DocumnetType, Document, ActionOnDocument

# Register your models here.
admin.site.register(User)
admin.site.register(Person)
admin.site.register(PersonToUser)
admin.site.register(Action)
admin.site.register(DocumnetType)
admin.site.register(Document)
admin.site.register(ActionOnDocument)