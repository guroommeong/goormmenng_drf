from django.db import models
import random
import string


class Shelter(models.Model):
    id = models.AutoField(primary_key=True)  # 보호소 ID
    photo = models.ImageField(upload_to='shelter_photos/', blank=True, null=True)  # 보호소 이미지
    description = models.TextField()  # 보호소 설명
    contact = models.CharField(max_length=100)  # 보호소 연락처
    name = models.CharField(max_length=100)  # 보호소 이름

    class Meta:
        db_table = 'shelter'


class Dog(models.Model):
    photo = models.ImageField(upload_to='dog_photos/', blank=True, null=True)  # 유기견 사진
    dog_id = models.AutoField(primary_key=True)  # 유기견 ID
    name = models.CharField(max_length=100)  # 유기견 이름
    age = models.IntegerField()  # 유기견 나이
    gender = models.CharField(max_length=10, choices=[('수컷', '수컷'), ('암컷', '암컷'), ('중성', '중성')])  # 유기견 성별
    tags = models.CharField(max_length=255)  # 유기견 태그들 (쉼표로 구분된 문자열)
    remaining_days = models.IntegerField()  # 보호소에서 머무를 수 있는 남은 기간
    description = models.TextField()  # 유기견 설명
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE)  # 보호소 외래키
    registration_number = models.CharField(max_length=50, blank=True, null=True)  # 유기견 등록번호
    owner = models.CharField(max_length=100, blank=True, null=True)  # 유기견 소유주 이름

    class Meta:
        db_table = 'dog'

    @property
    def tags_list(self):
        """태그 필드를 리스트 형식으로 반환합니다."""
        return self.tags.split(",") if self.tags else []

    @tags_list.setter
    def tags_list(self, value):
        """리스트 형식의 태그를 쉼표로 구분된 문자열로 저장합니다."""
        if isinstance(value, list):
            self.tags = ",".join(value)
        else:
            raise ValueError("tags_list must be a list of strings.")


class Reservation(models.Model):
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)  # 예약된 유기견
    start_date = models.DateField()  # 예약 시작일
    end_date = models.DateField()  # 예약 종료일
    created_at = models.DateTimeField(auto_now_add=True)  # 예약 생성일
    guest_name = models.CharField(max_length=100, default="guest")  # 사용자 이름 (기본값: guest)
    reservation_number = models.CharField(max_length=8, unique=True)  # 예약 번호 (영문 숫자 8자리)

    class Meta:
        db_table = 'reservation'

    def save(self, *args, **kwargs):
        if not self.reservation_number:
            self.reservation_number = self.generate_reservation_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_reservation_number():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

