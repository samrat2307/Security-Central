from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user'
        verbose_name_plural = 'Profile'

    def __str__(self):
        return self.user.username


class Solution(models.Model):
    name = models.CharField(max_length=64, null=False)
    last_updated = models.DateTimeField(default=now, null=False)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'solution'
        verbose_name_plural = 'Solution'


class Project(models.Model):
    name = models.CharField(max_length=64, null=False)
    blackduck_project_name = models.CharField(max_length=64, null=False)
    solution = models.ForeignKey(
        'Solution', on_delete=models.CASCADE,related_name='projects', db_column='solution_id')
    auto_monitor = models.BooleanField(default=False, null=False)
    last_updated = models.DateTimeField(default=now, null=False)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'project'
        verbose_name_plural = 'Project'


class Component(models.Model):
    blackduck_component_id = models.CharField(max_length=40, null=False)
    blackduck_version_id = models.CharField(max_length=40, null=False)
    name = models.CharField(max_length=50, null=False)
    version = models.CharField(max_length=20, null=False)
    last_updated = models.DateTimeField(default=now, null=False)

    def __str__(self):
        return self.name+self.version

    class Meta:
        managed = False
        db_table = 'component'
        verbose_name_plural = 'Component'


class Release(models.Model):
    name = models.CharField(max_length=64, null=False)
    release_date = models.DateField(null=False)
    last_updated = models.DateTimeField(default=now, null=False)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'release'
        verbose_name_plural = 'Release'


class Scan(models.Model):
    release = models.ForeignKey('Release',related_name='scans', on_delete=models.CASCADE)
    project = models.ForeignKey('Project',related_name='scans', on_delete=models.CASCADE)
    scan_datetime = models.DateTimeField(default=now, null=False)
    report_file = models.CharField(max_length=256, null=False)

    # def __str__(self):
    #     return self.scan_datetime

    class Meta:
        managed = False
        db_table = 'scan'
        verbose_name_plural = 'Scan'


class ScanDetails(models.Model):
    scan = models.ForeignKey(
        'Scan', on_delete=models.CASCADE, db_column='scan_id')
    component = models.ForeignKey(
        'Component', related_name="scandetails", on_delete=models.CASCADE, db_column='component_id')
    critical_vulnerability_count = models.IntegerField(default=0, null=False)
    high_vulnerability_count = models.IntegerField(default=0, null=False)
    medium_vulnerability_count = models.IntegerField(default=0, null=False)
    low_vulnerability_count = models.IntegerField(default=0, null=False)
    operational_risk = models.CharField(max_length=10, null=False)
    license_name = models.CharField(max_length=100, null=False)

    def __str__(self):
        return f'{self.scan.id , self.component.id }'

    class Meta:
        managed = False
        db_table = 'scan_details'
        verbose_name_plural = 'ScanDetails'
