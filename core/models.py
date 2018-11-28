from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# Extend the user model to add extra features to it
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    endpoint_limit = models.IntegerField(default=10)

    class Meta:
        verbose_name_plural = 'Accounts'

    def __str__(self):
        return self.user.username


# Receivers to handle saving and updating the user model and its extended account model
@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.account.save()


class Project(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    user = models.ForeignKey(User)
    database_built = models.BooleanField(default=False)

    class Meta:
        unique_together = (('name', 'user'))
        verbose_name_plural = 'Projects'

    def __str__(self):
        return 'User: '+self.user.username+' Project:'+self.name


class Database(models.Model):
    name = models.CharField(max_length=64)
    user = models.CharField(max_length=64)
    password = models.CharField(max_length=256)
    ssh_username = models.CharField(max_length=64)
    ssh_password = models.CharField(max_length=256)
    server_address = models.CharField(max_length=32)
    project = models.ForeignKey(Project)

    class Meta:
        verbose_name_plural = 'Databases'

    def __str__(self):
        return 'Project: '+self.project.name +' Database: '+self.name


class DatabaseTable(models.Model):
    name = models.CharField(max_length=64)
    database = models.ForeignKey(Database)

    class Meta:
        verbose_name_plural = 'Database Tables'

    def __str__(self):
        return 'Database: '+self.database.name+' Table: '+self.name


class DatabaseColumn(models.Model):
    name = models.CharField(max_length=64)
    type = models.CharField(max_length=64)
    table = models.ForeignKey(DatabaseTable)

    class Meta:
        verbose_name_plural = 'Database Columns'

    def __str__(self):
        return 'Database Column: '+self.name+ ' Table: '+self.table.name


class Endpoint(models.Model):
    REQUEST_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST')
    )

    RESPONSE_CHOICES = (
        ('JSON', 'JSON'),
        ('XML', 'XML')
    )

    name = models.CharField(max_length=64)
    description = models.CharField(max_length=64)

    # The Request
    request_type = models.CharField(max_length=4, choices=REQUEST_CHOICES)
    endpoint_url = models.CharField(max_length=64, unique=True)

    # The Response
    response_format = models.CharField(max_length=4, choices=RESPONSE_CHOICES)

    project = models.ForeignKey(Project)

    class Meta:
        verbose_name_plural = 'Endpoints'

    def __str__(self):
        return 'Project: '+self.project.name+' Endpoint: '+self.name


class EndpointHeader(models.Model):
    # Unique for each endpoint
    key = models.CharField(max_length=64)
    value = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    endpoint = models.ForeignKey(Endpoint)

    class Meta:
        verbose_name_plural = 'Endpoint Headers'

    def __str__(self):
        return 'Endpoint: '+self.endpoint.name+' Header Key: '+self.key


class EndpointParameter(models.Model):
    TYPE_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST')
    )
    # Unique for each endpoint
    key = models.CharField(max_length=64)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    endpoint = models.ForeignKey(Endpoint)

    class Meta:
        verbose_name_plural = 'Endpoint Parameters'


    def __str__(self):
        return 'Endpoint: ' + self.database.name + ' Parameter Key: ' + self.key


# A data source used in the returning of data from the request
class EndpointDataSource(models.Model):
    TYPE_CHOICES = (
        ('D', 'Database'),
        ('T', 'Text')
    )

    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    # In form, set database tables as choices
    table_name = models.CharField(max_length=64, null=True, blank=True)

    # If text was chosen then this will be filled out
    text = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Endpoint Datasources'


    def __str__(self):
        return 'Endpoint: ' + self.endpoint.name + ' Data Source Type: ' + self.type


# Each instance defines a column that needs to be returned
class EndpointDataSourceColumn(models.Model):
    # In form, the available column names are received when building the table but filtered by the selected table.
    name = models.CharField(max_length=64)
    endpoint = models.ForeignKey(Endpoint)

    class Meta:
        verbose_name_plural = 'Endpoint Data Source Columns'

    def __str__(self):
        return 'Endpoint: '+self.database.name+' Column Name: '+self.name
