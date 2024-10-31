# def calculate_match_score(dog_data, user_tags):
#     # 유기견 데이터와 사용자의 태그를 비교해 매칭 점수를 계산하는 함수입니다.
#     score = 0
#     for tag in user_tags:
#         if tag in dog_data:
#             score += 1
#
#     if len(user_tags) == 0:
#         return 0  # 사용자 태그가 없으면 매칭 점수는 0점
#
#     return (score / len(user_tags)) * 5  # 5점 만점 환산
