import os

topic = os.environ["PROMPT"].lower()

# Nhận diện bối cảnh
if "biển" in topic or "cá" in topic:
    place = "đại dương xanh"
elif "vũ trụ" in topic:
    place = "không gian đầy sao"
elif "khủng long" in topic:
    place = "thung lũng khủng long"
elif "trường" in topic:
    place = "ngôi trường cầu vồng"
else:
    place = "khu rừng phép thuật"

story = [
f"Miu và Bống bắt đầu chuyến phiêu lưu tại {place}.",
f"Hôm nay nhiệm vụ là: {topic}.",
"Khung cảnh thật đẹp và đầy màu sắc.",
"Hai bạn nghe thấy tiếng gọi giúp đỡ.",
"Miu bình tĩnh quan sát xung quanh.",
"Bống nghĩ ra một kế hoạch thông minh.",
"Cả hai cùng tiến về phía trước.",
"Một thử thách bất ngờ xuất hiện.",
"Hai bạn hợp tác vượt qua.",
"Mọi người bắt đầu mỉm cười.",
"Con đường dần sáng hơn.",
"Một người bạn mới xuất hiện.",
"Cả nhóm cùng tìm lời giải.",
"Khó khăn lớn nhất đang chờ phía trước.",
"Miu dũng cảm bảo vệ mọi người.",
"Bống giúp mọi người bằng trí thông minh.",
"Niềm hy vọng dần xuất hiện.",
"Ánh sáng rực rỡ bao phủ khắp nơi.",
"Các con vật vui vẻ reo hò.",
"Khung cảnh trở nên thật kỳ diệu.",
"Mọi người cảm ơn Miu và Bống.",
"Bài học về lòng tốt được lan tỏa.",
"Ai cũng hạnh phúc và đoàn kết.",
"Hẹn gặp lại trong tập tiếp theo!"
]

with open("story.txt","w",encoding="utf-8") as f:
    f.write("\n".join(story))
