from django.contrib import admin

from blog.models import Post, Category, Location


class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'short_text',
        'pub_date',
        'author',
        'category',
        'location',
        'is_published',
        'created_at'
    ]
    list_editable = [
        'is_published'
    ]
    search_fields = ('title', 'text')
    list_filter = ('is_published', 'pub_date', 'category', 'location')
    list_display_links = ('title',)
    ordering = ['-pub_date', 'author']
    list_per_page = 10

    @admin.display(description='text')
    def short_text(self, post):
        return post.text[:50]


class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'description',
        'slug',
        'is_published',
        'created_at'
    ]
    list_editable = [
        'is_published'
    ]
    search_fields = ('title', 'description', 'slug')
    list_display_links = ('title',)
    list_filter = ('is_published', 'created_at')


class LocationAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'is_published',
        'created_at'
    ]
    list_editable = [
        'is_published'
    ]
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('is_published', 'created_at')


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
