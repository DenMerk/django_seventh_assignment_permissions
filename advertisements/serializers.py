from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # Обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # Само поле при этом объявляется как `read_only=True`
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""
        # TODO: добавьте требуемую валидацию
        status_for_closing = data.get('status')  # отрабатывается ситуация закрытия объявления при превышении лимита
        if status_for_closing == 'CLOSED':
            return data
        advs = Advertisement.objects.filter(creator=self.context["request"].user)
        advs_count = 0  # Счетчик открытых объявлений
        limit_advs = 10  # Лимит открытых объявлений для пользователя

        for adv in advs:
            if adv.status == 'OPEN':
                advs_count += 1
        print(advs_count)
        if advs_count > limit_advs:
            raise serializers.ValidationError('Exceeded the number of active advertisements')
        return data
