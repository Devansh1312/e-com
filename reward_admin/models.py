# ================================
# Python Standard Library Imports
# ================================
from sre_parse import State

# ===============================
# Django Authentication Imports
# ===============================
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin

# ============================
# Django ORM & Utilities
# ============================
from django.db import models
from django.utils import timezone


# gender Model
class UserGender(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True) 
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'e_com_gender'

# Role Model
class Role(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True) 

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'e_com_role'

class Country(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=2)
    name = models.CharField(max_length=100)
    flag = models.ImageField(upload_to="Country_Flag/", null=True, blank=True)
    zone_id = models.IntegerField(default=0)
    country_code = models.IntegerField(null=True, blank=True)
    status = models.BooleanField(default=True, help_text='0 = InActive | 1 = Active')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True) 

    class Meta:
        db_table = 'e_com_country'

    def __str__(self):
        return self.name
    
class State(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')
    status = models.BooleanField(default=True, help_text='0 = InActive | 1 = Active')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True) 

    class Meta:
        db_table = 'e_com_state'

    def __str__(self):
        return self.name


class City(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')
    status = models.BooleanField(default=True, help_text='0 = InActive | 1 = Active')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True) 

    class Meta:
        db_table = 'e_com_city'

    def __str__(self):
        return self.name

# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, email, password, **extra_fields)

class OTPSave(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=100,blank=True,null=True)
    OTP = models.IntegerField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True) 

    def __str__(self):
        return self.email
    class Meta:
        db_table = 'e_com_otpsave'
              
class User(AbstractBaseUser, PermissionsMixin):
    
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    username = models.CharField(max_length=150, unique=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", null=True, blank=True)
    card_header = models.ImageField(upload_to="card_header/", null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    phone = models.CharField(max_length=20)
    name = models.CharField(max_length=150, null=True, blank=True)
    gender = models.ForeignKey('UserGender', null=True, blank=True, on_delete=models.CASCADE)
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey('State', null=True, blank=True, on_delete=models.CASCADE)
    cities = models.ManyToManyField('City', blank=True)
    otp = models.IntegerField(null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    device_type = models.IntegerField(null=True, blank=True,default=0)  # Assuming 0 for web, 1 for Android, 2 for iOS, etc.
    device_token = models.CharField(max_length=255, null=True, blank=True)
    register_type = models.CharField(max_length=10, null=True, blank=True)
    password = models.CharField(max_length=255)
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, blank=True)
    remember_token = models.CharField(max_length=255, null=True, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'e_com_user'


class SystemSettings(models.Model):
    website_name = models.CharField(max_length=255, null=True, blank=True)
    fav_icon = models.CharField(max_length=255, null=True, blank=True)
    website_logo = models.CharField(max_length=255, null=True, blank=True)
    phone = models.TextField(max_length=20)
    email = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    
    class Meta:
        db_table = 'e_com_systemsettings'


class FAQ(models.Model):
    question = models.TextField(blank=True,null=True)
    answer = models.TextField(blank=True,null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)  

    def __str__(self):
        return self.question

    class Meta:
        db_table = 'e_com_faq'

    
    
class product_category(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    # Single image per category (optional)
    image = models.ImageField(
        upload_to="category_images/",
        null=True,
        blank=True,
        help_text="Single image representing this category"
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    status = models.BooleanField(default=True, help_text='0 = InActive | 1 = Active')
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)  

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'e_com_product_category'


class Size(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    status = models.BooleanField(default=True, help_text='0 = InActive | 1 = Active')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'e_com_size'


class Color(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    hex_code = models.CharField(max_length=7, null=True, blank=True, help_text='Color hex code (e.g., #FF0000)')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    status = models.BooleanField(default=True, help_text='0 = InActive | 1 = Active')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'e_com_color'


class product(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    category = models.ForeignKey(product_category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(null=True, blank=True)
    MRP = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.BooleanField(default=True, help_text='0 = InActive | 1 = Active')
    url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)  
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'e_com_product'


class product_variant(models.Model):
    product = models.ForeignKey(product, on_delete=models.CASCADE, related_name='variants')
    size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True, related_name='variants')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True, related_name='variants')
    stock_quantity = models.IntegerField(default=0, null=True, blank=True)
    sku = models.CharField(max_length=100, null=True, blank=True, unique=True, help_text='Stock Keeping Unit')
    status = models.BooleanField(default=True, help_text='0 = InActive | 1 = Active')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        size_name = self.size.name if self.size else 'No Size'
        color_name = self.color.name if self.color else 'No Color'
        return f"{self.product.name} - {size_name} - {color_name}"

    class Meta:
        db_table = 'e_com_product_variant'
        unique_together = ('product', 'size', 'color')


class product_image(models.Model):
    product = models.ForeignKey(product, on_delete=models.CASCADE, related_name='images')
    variant = models.ForeignKey(product_variant, on_delete=models.CASCADE, null=True, blank=True, related_name='images', 
                                 help_text='If set, image is specific to this variant. If null, image is common for all variants.')
    image = models.ImageField(upload_to="product_images/", null=True, blank=True)
    is_primary = models.BooleanField(default=False, help_text='Primary image for the product/variant')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        if self.variant:
            return f"{self.product.name} - {self.variant}"
        return f"{self.product.name} - Common Image"

    class Meta:
        db_table = 'e_com_product_image'

class customer_review(models.Model):
    product = models.ForeignKey(product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)  
    def __str__(self):
        return self.product.name

    class Meta:
        db_table = 'e_com_customer_review'
        unique_together = ('product', 'customer')

class contact_us(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)  
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'e_com_contact_us'

class wishlist(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(product, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)  
    def __str__(self):
        return self.customer.username

    class Meta:
        db_table = 'e_com_wishlist'
        unique_together = ('customer', 'product')

class cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(product, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)  
    def __str__(self):
        return self.customer.username

    class Meta:
        db_table = 'e_com_cart'
        unique_together = ('customer', 'product')
