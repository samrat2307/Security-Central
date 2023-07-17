from rest_framework import serializers
from .models import *


class SolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = ["name"]


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["name", "solution_id"]


class ReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = ["name"]


class ScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scan
        fields = ["name"]


class ScanDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScanDetails
        fields = ["id", "scan_id", "component_id", "critical_vulnerability_count",
                  "high_vulnerability_count", "medium_vulnerability_count", "low_vulnerability_count"]
