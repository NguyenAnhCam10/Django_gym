from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.template.response import TemplateResponse
from django.utils import timezone
import json
from datetime import datetime, timedelta
from django.db.models import Count, Sum, Q
from .models import User, MemberProfile, Schedule, Review, Progress, Payment, Package, MemberPackage, Notification, Chat, ChatParticipant, Message
from django.urls import path
#AdminUser và MemberProfile
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_staff', 'is_superuser', 'is_active', 'date_joined', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('date_joined',)}),  # Loại bỏ created_at và last_login
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone', 'role'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

    # Đặt role mặc định là member khi tạo user mới
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Khi thêm user mới
            form.base_fields['role'].initial = 'member'  # Mặc định role là member
        return form

class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'height', 'weight', 'bmi', 'updated_at')
    search_fields = ('user__username', 'user__email')
    exclude = ('bmi', 'updated_at')  # Loại bỏ bmi và updated_at khỏi form



    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['queryset'] = User.objects.filter(role='member')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



#AdminSchedule

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'pt', 'start_time', 'end_time', 'status', 'note')
    list_filter = ('status', 'pt')
    search_fields = ('user__username', 'pt__username', 'note')
    date_hierarchy = 'start_time'
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'pt':
            return qs.filter(pt=request.user)  # PT chỉ thấy lịch của mình
        return qs

    def get_readonly_fields(self, request, obj=None):
        if request.user.role == 'pt':
            return ['user', 'member_package', 'created_at', 'updated_at']  # PT không sửa các trường này
        return []

    def has_add_permission(self, request):
        return True  # PT có thể tạo lịch mới

    def has_change_permission(self, request, obj=None):
        return True  # PT có thể sửa lịch

    def has_delete_permission(self, request, obj=None):
        if request.user.role == 'pt':
            return False  # PT không được xóa lịch
        return True


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'pt', 'gym_rating', 'pt_rating', 'created_at')
    list_filter = ('gym_rating', 'pt_rating')
    search_fields = ('user__username', 'pt__username', 'comment')
    date_hierarchy = 'created_at'

#

class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'pt', 'weight', 'body_fat', 'muscle_mass', 'recorded_at')
    list_filter = ('pt',)
    search_fields = ('user__username', 'pt__username', 'note')
    date_hierarchy = 'recorded_at'

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('member_package', 'amount', 'method', 'payment_date', 'status')
    list_filter = ('method', 'status')
    search_fields = ('member_package__user__username', 'member_package__package__name')
    date_hierarchy = 'payment_date'


class PackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'pt_sessions', 'package_type', 'is_active']  # Xóa 'duration'
    list_filter = ['package_type', 'is_active']
    search_fields = ['name']


class MemberPackageAdmin(admin.ModelAdmin):
    list_display = ['user', 'package', 'start_date', 'end_date', 'status']
    list_filter = ['status']
    search_fields = ['user__username', 'package__name']



class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'type', 'sent_at', 'is_read')
    list_filter = ('type', 'is_read')
    search_fields = ('title', 'message', 'user__username')
    date_hierarchy = 'sent_at'



class ChatAdmin(admin.ModelAdmin):
    list_display = ('chat_name', 'is_group', 'last_message', 'last_updated')
    list_filter = ('is_group',)
    search_fields = ('chat_name',)


class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = ('chat', 'user', 'joined_at')
    list_filter = ('chat',)
    search_fields = ('user__username',)


class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'content', 'timestamp')
    list_filter = ('chat', 'sender')
    search_fields = ('content', 'sender__username')


class MyAdminSite(admin.AdminSite):
    site_header = 'Quản lý phòng Gym'
    site_title = 'Trang quản trị'
    index_title = 'Bảng điều khiển'

    def get_urls(self):
        return [
            path('gym-stats/', self.gym_stats, name='gym_stats'),
        ] + super().get_urls()

    def gym_stats(self, request):
        """Trang thống kê theo yêu cầu"""

        # 1. Thống kê số lượng hội viên
        total_members = User.objects.filter(role='member').count()
        active_members = User.objects.filter(role='member', is_active=True).count()
        new_members_this_month = User.objects.filter(
            role='member',
            date_joined__month=timezone.now().month,
            date_joined__year=timezone.now().year
        ).count()

        # 2. Thống kê doanh thu
        now = timezone.now()
        current_month = now.replace(day=1)
        current_year = now.replace(month=1, day=1)

        monthly_revenue = sum(
            mp.package.price for mp in
            MemberPackage.objects.filter(start_date__gte=current_month).select_related('package')
        )

        yearly_revenue = sum(
            mp.package.price for mp in
            MemberPackage.objects.filter(start_date__gte=current_year).select_related('package')
        )

        total_revenue = sum(
            mp.package.price for mp in MemberPackage.objects.all().select_related('package')
        )

        # 3. Mức độ sử dụng phòng tập theo khung giờ
        # Lấy dữ liệu 30 ngày gần nhất
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        # Khung giờ hoạt động (6h - 22h)
        hourly_usage = {}
        for hour in range(6, 23):  # 6h đến 22h
            hourly_usage[hour] = 0

        # Đếm số lượt sử dụng theo giờ
        schedules = Schedule.objects.filter(
            start_time__date__gte=start_date,
            start_time__date__lte=end_date,
            status__in=['approved', 'completed']
        )

        for schedule in schedules:
            hour = schedule.start_time.hour
            if 6 <= hour <= 22:
                hourly_usage[hour] += 1

        # Chuẩn bị dữ liệu cho biểu đồ
        hourly_labels = []
        hourly_data = []
        for hour in range(6, 23):
            hourly_labels.append(f"{hour:02d}:00-{hour + 1:02d}:00")
            hourly_data.append(hourly_usage[hour])

        context = {
            # Số lượng hội viên
            'total_members': total_members,
            'active_members': active_members,
            'new_members_this_month': new_members_this_month,

            # Doanh thu
            'monthly_revenue': monthly_revenue,
            'yearly_revenue': yearly_revenue,
            'total_revenue': total_revenue,

            # Dữ liệu cho biểu đồ sử dụng theo giờ
            'hourly_labels': json.dumps(hourly_labels),
            'hourly_data': json.dumps(hourly_data),
        }

        return TemplateResponse(request, 'admin/gym-stats.html', context)

admin_site = MyAdminSite (name='phòng Gym')

admin_site.register(User, UserAdmin)
admin_site.register(MemberProfile, MemberProfileAdmin)
admin_site.register(Schedule, ScheduleAdmin)
admin_site.register(Review, ReviewAdmin)
admin_site.register(Progress, ProgressAdmin)
admin_site.register(Package, PackageAdmin)
admin_site.register(MemberPackage,MemberPackageAdmin)
admin_site.register(Notification, NotificationAdmin)
admin_site.register(Chat, ChatAdmin)
admin_site.register(ChatParticipant, ChatParticipantAdmin)
admin_site.register(Message, MessageAdmin)

