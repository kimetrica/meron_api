"""Serializers for the API view.

We need to be able to accept an image either as multipart/form-data value or base64 encoded as part of a JSON object.
"""
import os
from rest_framework import serializers
from malnutrition_detection import analyze_image

from tempfile import TemporaryDirectory
from .fields import Base64ImageField


class FaceDetectionInputSerializer(serializers.Serializer):
    """Serializer that uses Base64ImageField to allow POSTing of image as multipart/form-data or base64 in JSON."""

    image = Base64ImageField()
    score = serializers.BooleanField(required=False)
    classification = serializers.BooleanField(required=False)

    def create(self, validated_data):
        """Call face detection function and return results."""
        # we need a file path that we can pass to analyze_image
        django_content_file = validated_data['image']
        # using a temporary directory to make sure the file is accessible to the malnutrition detection function.
        # The temporary directory will be deleted once the "with" context is completed
        with TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, django_content_file.name)
            with open(file_path, 'wb') as tmp_file:
                tmp_file.write(django_content_file.read())
            result = analyze_image(file_path,
                                   'score' in self.context['request'].query_params or validated_data.get('score'),
                                   'classification' in self.context['request'].query_params or
                                   validated_data.get('classification'))
        return result


class FaceDetectionOutputSerializer(serializers.Serializer):
    """Render all the values the face detection function returns."""

    width = serializers.IntegerField()
    height = serializers.IntegerField()
    score = serializers.FloatField(required=False)
    classification = serializers.FloatField(required=False)