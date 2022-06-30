from django.contrib import admin
from .models import Category
from treenode.admin import TreeNodeModelAdmin
from treenode.forms import TreeNodeForm
# Register your models here.


class CategoryAdmin(TreeNodeModelAdmin):
    treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_ACCORDION
    form = TreeNodeForm


admin.site.register(Category, CategoryAdmin)