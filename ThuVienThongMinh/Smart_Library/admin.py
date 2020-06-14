from django.contrib import admin
from .models import DocGia,Book,Category_Book,Cart,Check_book,Contact,ID_Book,ID_DocGia
# Register your models here.
admin.site.register(DocGia)
admin.site.register(Book)
admin.site.register(Category_Book)
admin.site.register(Cart)
admin.site.register(Check_book)
admin.site.register(Contact)
admin.site.register(ID_Book)
admin.site.register(ID_DocGia)