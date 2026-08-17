import os

topic = os.environ["PROMPT"].strip()

hero = "Miu"
friend = "Bống"

story = [
f"{hero} và {friend} bắt đầu cuộc phiêu lưu: {topic}.",
"Hai bạn bước vào một khu rừng đầy màu sắc.",
"Một bạn nhỏ đang gặp khó khăn.",
f"{hero} bình tĩnh quan sát mọi chuyện.",
f"{friend} nghĩ ra một ý tưởng hay.",
"Cả hai quyết định giúp đỡ.",
"Họ cùng tìm manh mối đầu tiên.",
"Một thử thách bất ngờ xuất hiện.",
"Hai bạn vượt qua bằng sự đoàn kết.",
"Các con vật trong rừng cổ vũ.",
"Hành trình trở nên gay cấn hơn.",
"Một tia hy vọng xuất hiện.",
"Họ tiến gần mục tiêu cuối cùng.",
"Một trở ngại lớn chặn đường.",
f"{hero} dũng cảm bảo vệ mọi người.",
f"{friend} thông minh giải quyết vấn đề.",
"Cả nhóm cùng chung sức.",
"Mọi khó khăn dần biến mất.",
"Khu rừng trở nên rực rỡ.",
"Những bông hoa nở khắp nơi.",
"Các bạn nhỏ vui vẻ cười đùa.",
"Mọi người cảm ơn Miu và Bống.",
"Một bài học về lòng tốt được kể.",
"Hẹn gặp lại trong chuyến phiêu lưu tiếp theo!"
]

with open("story.txt","w",encoding="utf-8") as f:
    f.write("\n".join(story))
