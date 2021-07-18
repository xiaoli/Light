from django.core import serializers


class PropBaseSerializer(serializers.base.Serializer):
    """
    Custom serializer class which enables us to specify a subset
    of model class properties (as well as fields)
    """
    def serialize(self, queryset, **options):
        self.selected_props = options.pop('props')
        return super().serialize(queryset, **options)

    def serialize_property(self, obj):
        model = type(obj)
        for prop in self.selected_props:
            if hasattr(model, prop) and type(getattr(model, prop)) == property:
                self.handle_prop(obj, prop)

    def handle_prop(self, obj, prop):
        self._current[prop] = getattr(obj, prop)

    def end_object(self, obj):
        self.serialize_property(obj)
        super().end_object(obj)


class PropPythonSerializer(PropBaseSerializer, serializers.python.Serializer):
    pass


class PropJsonSerializer(PropPythonSerializer, serializers.json.Serializer):
    pass
    
def json_serialize(qs, fields=(), props=()):
    return PropJsonSerializer().serialize(qs, fields=fields, props=props)