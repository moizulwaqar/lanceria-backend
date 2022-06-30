from django.db import models
from treenode.models import TreeNodeModel
from lanceria_backend.soft_delete import SoftDeleteModel
# Create your models here.


class Category(TreeNodeModel, SoftDeleteModel):
    treenode_display_field = 'name'
    name = models.CharField(max_length=50)
    icon = models.FileField(upload_to='category_icon/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TreeNodeModel.Meta):
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'