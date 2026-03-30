from rest_framework import serializers
from candidate.models import CandidateProfile



class CandidateProfileSerializer(serializers.ModelSerializer):
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = CandidateProfile
        fields = '__all__'

    def get_profile_photo(self, obj):
        return self.build_url_field(obj.profile_photo)

    def build_url_field(self, field):
        request = self.context.get('request')

        if field and request:
            return request.build_absolute_uri(field.url)

        return None