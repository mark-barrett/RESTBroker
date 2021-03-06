from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# Extend the user model to add extra features to it
from django.utils import timezone


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resource_limit = models.IntegerField(default=10)
    demo = models.BooleanField(default=True)
    forgot_password_code = models.IntegerField(null=True, blank=True)
    forgot_password_expiry = models.DateTimeField(default=timezone.now, blank=True, null=True)

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

    TYPE_CHOICES = (
        ('private', 'Private'),
        ('public', 'Public')
    )

    CACHE_EXPIRY = (
        ('1', '1 Hour'),
        ('2', '2 Hours'),
        ('4', '4 Hours'),
        ('8', '8 Hours'),
        ('12', '12 Hours'),
        ('24', '14 Hours'),
    )

    name = models.CharField(max_length=64)
    description = models.TextField(null=True, default='No description')
    user = models.ForeignKey(User)
    database_built = models.BooleanField(default=False)
    type = models.CharField(max_length=25, choices=TYPE_CHOICES, null=True, default='private')
    caching = models.BooleanField(default=False)
    caching_expiry = models.CharField(max_length=2, choices=CACHE_EXPIRY, null=True, blank=True)
    alert_email = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        unique_together = (('name', 'user'))
        verbose_name_plural = 'Projects'

    def __str__(self):
        return 'User: '+self.user.username+' Project:'+self.name


class Database(models.Model):
    name = models.CharField(max_length=64)
    user = models.CharField(max_length=64)
    password = models.CharField(max_length=256)
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


class Resource(models.Model):
    REQUEST_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('DELETE', 'DELETE')
    )

    RESPONSE_CHOICES = (
        ('JSON', 'JSON'),
        ('XML', 'XML')
    )

    name = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    status = models.BooleanField(default=True)

    # The Request
    request_type = models.CharField(max_length=10, choices=REQUEST_CHOICES)

    # The Response
    response_format = models.CharField(max_length=4, choices=RESPONSE_CHOICES)

    project = models.ForeignKey(Project)

    class Meta:
        verbose_name_plural = 'Resources'
        unique_together = ('name', 'project', 'request_type')

    def __str__(self):
        return 'Project: '+self.project.name+' Resource: '+self.name+ ' ('+self.request_type+')'


class ResourceHeader(models.Model):
    # Unique for each resource
    key = models.CharField(max_length=64)
    value = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    resource = models.ForeignKey(Resource)

    class Meta:
        verbose_name_plural = 'Resource Headers'

        # Set that this resource can only have one of this key
        unique_together = ('key', 'resource')

    def __str__(self):
        return 'Resource: '+self.resource.name+' Header Key: '+self.key


class ResourceParameter(models.Model):
    TYPE_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST')
    )
    # Unique for each resource
    key = models.CharField(max_length=64)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    resource = models.ForeignKey(Resource)

    class Meta:
        verbose_name_plural = 'Resource Parameters'

        # Set that this resource can only have one of this key
        unique_together = ('key', 'resource')

    def __str__(self):
        return 'Resource: ' + self.resource.name + ' Parameter Key: ' + self.key


# A data source used in the returning of data from the request
class ResourceDataSource(models.Model):
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
        verbose_name_plural = 'Resource Datasources'

    def __str__(self):
        return 'Resource: ' + self.resource.name + ' Data Source Type: ' + self.type


# A data source used in the returning of data from the request
class ResourceTextSource(models.Model):

    text = models.TextField()
    resource = models.ForeignKey(Resource)

    class Meta:
        verbose_name_plural = 'Resource Text Sources'

    def __str__(self):
        return 'Resource: ' + self.resource.name


# Each instance defines a column that needs to be returned
class ResourceDataSourceColumn(models.Model):
    # In form, the available column names are received when building the table but filtered by the selected table.
    column_id = models.IntegerField()
    resource = models.ForeignKey(Resource)

    class Meta:
        verbose_name_plural = 'Resource Data Source Columns'

    def __str__(self):
        return 'Resource: '+self.resource.name+' Column ID: '+str(self.id)


# Defines a filter that must be applied to the above column
class ResourceDataSourceFilter(models.Model):
    TYPE_CHOICES = (
        ('REQUEST', 'Parameter sent in request, either GET or POST'),
        ('COLUMN', 'Parameter from another column.')
        # Add previous column as parameter filter
    )

    type = models.CharField(max_length=6, choices=TYPE_CHOICES)
    request_parameter = models.ForeignKey(ResourceParameter, blank=True, null=True)
    # Foreign Key is Database Column not ResourceDataSourceColumn as that is used to represent what is being returned
    column_parameter = models.ForeignKey(DatabaseColumn, blank=True, null=True, related_name='column_to_act_as_filter')
    resource = models.ForeignKey(Resource)
    column_to_filter = models.ForeignKey(DatabaseColumn, related_name='column_to_filter_with_this_filter')

    class Meta:
        verbose_name_plural = 'Resource Data Source Filters'

    def __str__(self):
        if self.type == 'REQUEST':
            return 'Resource: '+str(self.resource.id)+' Type: '+str(self.type)+ ' Parameter to Filter by: '+str(self.request_parameter)
        else:
            return 'Resource: ' + str(self.resource.id) + ' Type: ' + str(
                self.type) + ' Parameter to Filter by: ' + str(self.column_parameter)


# This model defines for a given child, its parent table. This allows nesting of results
class ResourceParentChildRelationship(models.Model):

    parent_table = models.ForeignKey(DatabaseTable, related_name='the_parent_table')
    child_table = models.ForeignKey(DatabaseTable, related_name='the_child_table')
    parent_table_column = models.ForeignKey(DatabaseColumn, related_name='the_column_in_the_parent_table_to_match_to_the_child_table')
    child_table_column = models.ForeignKey(DatabaseColumn, related_name='the_column_in_the_child_table_to_match_to_the_parent_table')
    resource = models.ForeignKey(Resource)

    class Meta:
        verbose_name_plural = 'Resource Parent of Relationships'

    def __str__(self):
        return self.parent_table.name + ' is the parent of child '+self.child_table.name+ ' through the field '+\
               self.parent_table_column.name + ' on the parent table matched to '+\
               self.child_table_column.name + ' on the child table'


class ResourceDataBind(models.Model):

    TYPE_CHOICES = (
        ('Integer', 'Integer'),
        ('Decimal', 'Decimal'),
        ('String', 'String'),
        ('Boolean', 'Boolean')
    )

    column = models.ForeignKey(DatabaseColumn)
    key = models.CharField(max_length=256)
    resource = models.ForeignKey(Resource)
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    description = models.CharField(max_length=256)

    class Meta:
        verbose_name_plural = 'Resource Data Binds'

        # Make that key and the resource unique together
        unique_together = ('key', 'resource')

    def __str__(self):
        return 'Bind between: '+self.column.name+' and key: '+self.key+' in resource: '+self.resource.name


class UserGroup(models.Model):
    name = models.CharField(max_length=128)
    project = models.ForeignKey(Project)

    class Meta:
        unique_together = (('name'), ('project'))
        verbose_name_plural = 'User Groups'

    def __str__(self):
        return self.name + ' ' + self.project.name


# Will hold relationships between the resource and user groups. If there are none then it means anybody can access it
class ResourceUserGroup(models.Model):
    user_group = models.ForeignKey(UserGroup)
    resource = models.ForeignKey(Resource)

    class Meta:
        verbose_name_plural = 'Resource User Groups'

    def __str__(self):
        return self.user_group.name + ' ' + self.resource.name


class BlockedIP(models.Model):

    ip_address = models.GenericIPAddressField()
    project = models.ForeignKey(Project)

    class Meta:
        unique_together = (('ip_address'), ('project'))
        verbose_name_plural = 'Blocked IPs'

    def __str__(self):
        return self.project.name + ': ' + self.ip_address


class Alert(models.Model):

    PERIOD_OPTIONS = (
        ('day', 'In one day'),
        ('week', 'In one week'),
        ('month', 'In one month'),
        ('year', 'In one year'),
        ('forever', 'In all time')
    )

    resource = models.ForeignKey(Resource)
    limit = models.IntegerField()
    period = models.CharField(max_length=10, choices=PERIOD_OPTIONS)
    notification_sent_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Alerts'

    def __str__(self):
        return self.resource.name + ' ' + self.resource.project.name + ' ' + str(self.limit)