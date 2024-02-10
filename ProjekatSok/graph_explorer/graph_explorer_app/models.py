from django.db import models

from neomodel import StructuredNode, StringProperty, IntegerProperty, UniqueIdProperty, RelationshipTo


class NodeData(StructuredNode):
    def __init__(self, id1=5, value=None):
        self.id1 = id1
        self.value = value
