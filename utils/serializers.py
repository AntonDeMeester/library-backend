from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rest_framework import serializers

class GetOrCreateSerializer(serializers.ModelSerializer):

    #Source: https://stackoverflow.com/a/48310365/10570965
    def run_validation(self, initial_data):
        if hasattr(self, 'initial_data'):
            # If we are instantiating with data={something}
            try:
                # Try to get the object in question
                obj = self.Meta.model.objects.get(**initial_data)
            except (ObjectDoesNotExist, MultipleObjectsReturned):
                # Except not finding the object or the data being ambiguous
                # for defining it. Then validate the data as usual
                return super().run_validation(initial_data)
            else:
                # If the object is found add it to the serializer. Then
                # validate the data as usual
                self.instance = obj
                return super().run_validation(initial_data)
        else:
            # If the Serializer was instantiated with just an object, and no
            # data={something} proceed as usual 
            return super().run_validation(initial_data)

    def create(self, validated_data):
        """
        Because a list serializer doesn't know if the individual items already exist,
        we overwrite create to check for self.instance.
        """
        if self.instance is None:
            return super().create(validated_data)
        else:
            self.instance = self.update(self.instance, validated_data)
            assert self.instance is not None, (
                '`update()` did not return an object instance.'
            )
            return self.instance
