from rest_framework import serializers
from .models import User, MemberProfile, Package, MemberPackage, Schedule, Progress, Review, Payment, Notification, Chat, ChatParticipant, Message

class UserSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)



        return data

    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.set_password(u.password)
        u.save()

        return u

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password' ,'first_name', 'last_name', 'phone', 'role', 'created_at', 'last_login')
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

class MemberProfileSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)



        return data
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = MemberProfile
        fields = ('id', 'user', 'height', 'weight', 'bmi', 'updated_at')


class PackageSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Package
        fields = ['id', 'name', 'price', 'description', 'pt_sessions', 'package_type', 'created_by', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']
class MemberPackageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    package = PackageSerializer(read_only=True)
    package_id = serializers.PrimaryKeyRelatedField(
        queryset=Package.objects.filter(is_active=True), source='package', write_only=True
    )

    class Meta:
        model = MemberPackage
        fields = ['id', 'user', 'package', 'package_id', 'start_date', 'end_date', 'remaining_sessions', 'status', 'created_at', 'updated_at']
        read_only_fields = ['user', 'end_date', 'remaining_sessions', 'status', 'created_at', 'updated_at']

class ScheduleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    pt = UserSerializer(read_only=True)
    member_package = MemberPackageSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='member'),
        source='user',
        write_only=True
    )
    pt_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='pt'),
        source='pt',
        required=False,
        write_only=True,
        allow_null=True
    )
    member_package_id = serializers.PrimaryKeyRelatedField(
        queryset=MemberPackage.objects.all(),
        source='member_package',
        write_only=True,
        allow_null=True
    )

    class Meta:
        model = Schedule
        fields = ['id', 'user', 'user_id', 'pt', 'pt_id', 'member_package', 'member_package_id', 'start_time', 'end_time', 'status', 'note', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ProgressSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    pt = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    pt_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='pt', write_only=True, allow_null=True
    )

    class Meta:
        model = Progress
        fields = ['id', 'user', 'user_id', 'pt', 'pt_id', 'weight', 'body_fat', 'muscle_mass', 'note', 'recorded_at']
        read_only_fields = ['pt', 'recorded_at']

class ReviewSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)
    # pt = UserSerializer(read_only=True)
    # user_id = serializers.PrimaryKeyRelatedField(
    #     queryset=User.objects.filter(role='member'),
    #     source='user',
    #     write_only=True
    # )
    # pt_id = serializers.PrimaryKeyRelatedField(
    #     queryset=User.objects.filter(role='pt'),
    #     source='pt',
    #     write_only=True,
    #     allow_null=True
    # )
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data
        return data

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_id', 'pt', 'pt_id', 'gym_rating', 'pt_rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']
        extra_kwargs = {
            'lesson': {
                'write_only': True
            }
        }

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['payment_date']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('sent_at', 'is_sent', 'user')

class ChatParticipantSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ChatParticipant
        fields = ['id', 'chat', 'user', 'joined_at']

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'content', 'timestamp', 'firebase_message_id']

class ChatSerializer(serializers.ModelSerializer):
    participants = ChatParticipantSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'chat_name', 'is_group', 'last_message', 'last_updated', 'firebase_chat_id', 'participants', 'messages']

