
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AccountEmailaddress(models.Model):
    email = models.CharField(unique=True, max_length=254)
    verified = models.BooleanField()
    primary = models.BooleanField()
    user = models.ForeignKey('UsersUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_emailaddress'


class AccountEmailconfirmation(models.Model):
    created = models.DateTimeField()
    sent = models.DateTimeField(blank=True, null=True)
    key = models.CharField(unique=True, max_length=64)
    email_address = models.ForeignKey(AccountEmailaddress, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_emailconfirmation'


class Address(models.Model):
    address_id = models.AutoField(primary_key=True)
    street = models.CharField(max_length=199)
    complement = models.CharField(max_length=65, blank=True, null=True)
    district = models.CharField(max_length=99)
    number = models.CharField(max_length=65, blank=True, null=True)
    postalcode = models.CharField(max_length=60, blank=True, null=True)
    long = models.CharField(max_length=65, blank=True, null=True)
    lat = models.CharField(max_length=65, blank=True, null=True)
    id_city_location_city_location = models.ForeignKey('CityLocation', models.DO_NOTHING, db_column='id_city_location_city_location', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'address'


class Age(models.Model):
    age_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=99)
    age_status = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'age'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class CategoryFood(models.Model):
    category_food_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=99)
    description = models.TextField(blank=True, null=True)
    category_food_status = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'category_food'


class CityLocation(models.Model):
    id_city_location = models.AutoField(primary_key=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'city_location'


class Company(models.Model):
    id_company = models.AutoField(primary_key=True)
    id_address = models.ForeignKey(Address, models.DO_NOTHING, db_column='id_address')
    name_company = models.CharField(max_length=80)
    cnpj = models.IntegerField()
    contract = models.CharField(max_length=80)
    notice = models.CharField(max_length=80)
    status = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'company'


class Contact(models.Model):
    contact = models.ForeignKey('User', models.DO_NOTHING, primary_key=True)
    number = models.CharField(max_length=20)
    user_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'contact'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('UsersUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DjangoSite(models.Model):
    domain = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'django_site'


class Food(models.Model):
    food_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=99)
    food_details = models.TextField(blank=True, null=True)
    food_status = models.BooleanField()
    category_food = models.ForeignKey(CategoryFood, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'food'


class Log(models.Model):
    log_id = models.AutoField(primary_key=True)
    log_date = models.DateTimeField()
    user = models.ForeignKey('User', models.DO_NOTHING)
    title = models.CharField(max_length=60)
    payload = models.TextField()

    class Meta:
        managed = False
        db_table = 'log'


class ManagementMenu(models.Model):
    management_menu_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=99)
    management_menu_status = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'management_menu'


class ManagementType(models.Model):
    management_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=99)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'management_type'


class Menu(models.Model):
    menu_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    notice = models.ForeignKey('Notice', models.DO_NOTHING)
    type = models.ForeignKey('Type', models.DO_NOTHING)
    title = models.CharField(max_length=99)
    menu_date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    menu_default = models.BooleanField()
    menu_status = models.BooleanField()
    management_menu = models.ForeignKey(ManagementMenu, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'menu'


class MenuAge(models.Model):
    menu = models.ForeignKey(Menu, models.DO_NOTHING, primary_key=True)
    age = models.ForeignKey(Age, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'menu_age'
        unique_together = (('menu', 'age'),)


class MenuFood(models.Model):
    menu = models.ForeignKey(Menu, models.DO_NOTHING, primary_key=True)
    food = models.ForeignKey(Food, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'menu_food'
        unique_together = (('menu', 'food'),)


class Notice(models.Model):
    notice_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=99)
    details = models.TextField(blank=True, null=True)
    start = models.DateField()
    end = models.DateField()

    class Meta:
        managed = False
        db_table = 'notice'


class Profile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=90)
    profile_status = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'profile'


class RegionalDirector(models.Model):
    id_regional_director = models.AutoField(primary_key=True)
    initials = models.CharField(max_length=50)
    name = models.CharField(max_length=80)

    class Meta:
        managed = False
        db_table = 'regional_director'


class RegionalDirectorUser(models.Model):
    id_regional_director = models.ForeignKey(RegionalDirector, models.DO_NOTHING, db_column='id_regional_director', primary_key=True)
    id_user = models.ForeignKey('User', models.DO_NOTHING, db_column='id_user')

    class Meta:
        managed = False
        db_table = 'regional_director_user'
        unique_together = (('id_regional_director', 'id_user'),)


class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=99)
    description = models.TextField(blank=True, null=True)
    role_status = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'role'


class School(models.Model):
    school_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=199)
    email = models.CharField(max_length=199, blank=True, null=True)
    phone = models.CharField(max_length=45)
    phone2 = models.CharField(max_length=45, blank=True, null=True)
    grouping = models.SmallIntegerField()
    is_active = models.BooleanField()
    address = models.ForeignKey(Address, models.DO_NOTHING)
    unit = models.ForeignKey('SchoolUnit', models.DO_NOTHING)
    managerment = models.ForeignKey(ManagementType, models.DO_NOTHING)
    under_prefecture = models.ForeignKey('SubTownHall', models.DO_NOTHING)
    eol_code = models.CharField(max_length=10, blank=True, null=True)
    codae_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'school'


class SchoolAge(models.Model):
    shool = models.ForeignKey(School, models.DO_NOTHING, primary_key=True)
    age = models.ForeignKey(Age, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'school_age'
        unique_together = (('shool', 'age'),)


class SchoolUnit(models.Model):
    unit_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=99)
    unit_status = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'school_unit'


class ServiceBatch(models.Model):
    id_service_batch = models.AutoField(primary_key=True)
    initials = models.CharField(max_length=80)
    name = models.CharField(max_length=80)
    id_regional_director = models.ForeignKey(RegionalDirector, models.DO_NOTHING, db_column='id_regional_director')

    class Meta:
        managed = False
        db_table = 'service_batch'


class ServiceBatchCompany(models.Model):
    id_service_batch_service_batch = models.ForeignKey(ServiceBatch, models.DO_NOTHING, db_column='id_service_batch_service_batch', primary_key=True)
    id_company_company = models.ForeignKey(Company, models.DO_NOTHING, db_column='id_company_company')

    class Meta:
        managed = False
        db_table = 'service_batch_company'
        unique_together = (('id_service_batch_service_batch', 'id_company_company'),)


class SocialaccountSocialaccount(models.Model):
    provider = models.CharField(max_length=30)
    uid = models.CharField(max_length=191)
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    extra_data = models.TextField()
    user = models.ForeignKey('UsersUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialaccount'
        unique_together = (('provider', 'uid'),)


class SocialaccountSocialapp(models.Model):
    provider = models.CharField(max_length=30)
    name = models.CharField(max_length=40)
    client_id = models.CharField(max_length=191)
    secret = models.CharField(max_length=191)
    key = models.CharField(max_length=191)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp'


class SocialaccountSocialappSites(models.Model):
    socialapp = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING)
    site = models.ForeignKey(DjangoSite, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp_sites'
        unique_together = (('socialapp', 'site'),)


class SocialaccountSocialtoken(models.Model):
    token = models.TextField()
    token_secret = models.TextField()
    expires_at = models.DateTimeField(blank=True, null=True)
    account = models.ForeignKey(SocialaccountSocialaccount, models.DO_NOTHING)
    app = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialtoken'
        unique_together = (('app', 'account'),)


class SubTownHall(models.Model):
    under_prefecture_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=99)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'sub_town_hall'


class Type(models.Model):
    type_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=99)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'type'


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, models.DO_NOTHING)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=160)
    functional_register = models.CharField(max_length=60, blank=True, null=True)
    password = models.CharField(max_length=99)
    is_staff = models.NullBooleanField()
    date_joined = models.DateTimeField(blank=True, null=True)
    is_trusty = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'user'


class UserCompany(models.Model):
    user_id_user = models.ForeignKey(User, models.DO_NOTHING, db_column='user_id_user', primary_key=True)
    id_company_company = models.ForeignKey(Company, models.DO_NOTHING, db_column='id_company_company')

    class Meta:
        managed = False
        db_table = 'user_company'
        unique_together = (('user_id_user', 'id_company_company'),)


class UserProfilesAlternateprofile(models.Model):
    user_ptr = models.ForeignKey('UsersUser', models.DO_NOTHING, primary_key=True)
    cpf = models.CharField(unique=True, max_length=11, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_profiles_alternateprofile'


class UserProfilesNutritionistprofile(models.Model):
    user_ptr = models.ForeignKey('UsersUser', models.DO_NOTHING, primary_key=True)
    cpf = models.CharField(unique=True, max_length=11, blank=True, null=True)
    regional_director = models.ForeignKey('UserProfilesRegionaldirectorprofile', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_profiles_nutritionistprofile'


class UserProfilesOutsourcedprofile(models.Model):
    user_ptr = models.ForeignKey('UsersUser', models.DO_NOTHING, primary_key=True)
    cnpj = models.CharField(unique=True, max_length=11, blank=True, null=True)
    state_registry = models.CharField(unique=True, max_length=11, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_profiles_outsourcedprofile'


class UserProfilesRegionaldirectorprofile(models.Model):
    abbreviation = models.CharField(max_length=4)
    description = models.TextField()
    alternate = models.ForeignKey(UserProfilesAlternateprofile, models.DO_NOTHING, blank=True, null=True)
    sub_manager = models.ForeignKey('UserProfilesSubmanagerprofile', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_profiles_regionaldirectorprofile'


class UserProfilesSubmanagerprofile(models.Model):
    user_ptr = models.ForeignKey('UsersUser', models.DO_NOTHING, primary_key=True)
    cpf = models.CharField(unique=True, max_length=11, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_profiles_submanagerprofile'


class UserRole(models.Model):
    user_id_user = models.ForeignKey(User, models.DO_NOTHING, db_column='user_id_user', primary_key=True)
    role_id_role = models.ForeignKey(Role, models.DO_NOTHING, db_column='role_id_role')

    class Meta:
        managed = False
        db_table = 'user_role'
        unique_together = (('user_id_user', 'role_id_role'),)


class UsersUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    functional_register = models.CharField(unique=True, max_length=60, blank=True, null=True)
    mobile_phone = models.CharField(max_length=11, blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    is_alternate = models.BooleanField()
    is_nutritionist = models.BooleanField()
    is_outsourced = models.BooleanField()
    is_regional_director = models.BooleanField()
    is_sub_manager = models.BooleanField()
    uuid2 = models.UUIDField()

    class Meta:
        managed = False
        db_table = 'users_user'


class UsersUserGroups(models.Model):
    user = models.ForeignKey(UsersUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_user_groups'
        unique_together = (('user', 'group'),)


class UsersUserUserPermissions(models.Model):
    user = models.ForeignKey(UsersUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_user_user_permissions'
        unique_together = (('user', 'permission'),)
