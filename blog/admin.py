from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Post, Category, Tag, Comment

# Register your models here.
admin.site.register(Post, MarkdownxModelAdmin)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Comment)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug":("name",)}

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}

