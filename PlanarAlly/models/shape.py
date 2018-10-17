from peewee import BooleanField, FloatField, ForeignKeyField, IntegerField, TextField
from playhouse.sqlite_ext import JSONField
from playhouse.shortcuts import model_to_dict

from . import get_table
from .base import BaseModel
from .campaign import Layer
from .user import User

class Shape(BaseModel):
    uuid = TextField(primary_key=True)
    layer = ForeignKeyField(Layer, backref='shapes')
    type_ = TextField()
    x = FloatField()
    y = FloatField()
    name = TextField(null=True)
    fill_colour = TextField(default="#000")
    stroke_colour = TextField(default="#fff")
    vision_obstruction = BooleanField(default=False)
    movement_obstruction = BooleanField(default=False)
    is_token = BooleanField(default=False)
    annotation = TextField(default='')
    draw_operator = TextField(default='source-over')
    index = IntegerField()
    options = TextField(null=True)

    def __repr__(self):
        return f"<Shape {self.get_path()}>"
    
    def get_path(self):
        return f"{self.name}@{self.layer.get_path()}"
    
    def as_dict(self, user: User, dm: bool, exclude=None):
        data = model_to_dict(self, recurse=False, exclude=[Shape.layer, Shape.index])
        data['owners'] = [so.user.name for so in self.owners.select(User.name).join(User)]
        owned = dm or (user.name in data['owners'])
        tracker_query = self.trackers
        aura_query = self.auras
        if not owned:
            data['annotation'] = ''
            tracker_query = tracker_query.where(Tracker.visible)
            aura_query = aura_query.where(Aura.visible)
        data['trackers'] = [t.as_dict() for t in tracker_query]
        data['auras'] = [a.as_dict() for a in aura_query]
        type_table = get_table(self.type_)
        data.update(**model_to_dict(type_table.get(uuid=self.uuid), exclude=[type_table.uuid]))

        return data

    class Meta:
        indexes = ((('layer', 'index'), True),)


class Tracker(BaseModel):
    uuid = TextField(primary_key=True)
    shape = ForeignKeyField(Shape, backref='trackers')
    visible = BooleanField()
    name = TextField()
    value = IntegerField()
    maxvalue = IntegerField()

    def __repr__(self):
        return f"<Tracker {self.name} {self.shape.get_path()}>"
    
    def as_dict(self):
        return model_to_dict(self, recurse=False, exclude=[Tracker.shape])


class Aura(BaseModel):
    uuid = TextField(primary_key=True)
    shape = ForeignKeyField(Shape, backref='auras')
    vision_source = BooleanField()
    visible = BooleanField()
    name = TextField()
    value = IntegerField()
    dim = IntegerField()
    colour = TextField()

    def __repr__(self):
        return f"<Aura {self.name} {self.shape.get_path()}>"
    
    def as_dict(self):
        return model_to_dict(self, recurse=False, exclude=[Aura.shape])


class ShapeOwner(BaseModel):
    shape = ForeignKeyField(Shape, backref='owners')
    user = ForeignKeyField(User, backref='shapes')

    def __repr__(self):
        return f"<ShapeOwner {self.user.name} {self.shape.get_path()}>"


class ShapeType(BaseModel):
    uuid = TextField(primary_key=True)


class BaseRect(ShapeType):
    width = FloatField()
    height = FloatField()


class AssetRect(BaseRect):
    src = TextField()


class Circle(ShapeType):
    radius = FloatField()


class CircularToken(Circle):
    text = TextField()
    font = TextField()


class Line(ShapeType):
    x2 = FloatField()
    y2 = FloatField()
    line_width = IntegerField()


class MultiLine(ShapeType):
    line_width = IntegerField()
    points = JSONField()


class Rect(BaseRect):
    pass


class Text(ShapeType):
    text = TextField()
    font = TextField()
    angle = FloatField()