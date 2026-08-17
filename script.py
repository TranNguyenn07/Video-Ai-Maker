import os

topic = os.environ["PROMPT"]

story = [
f"Một buổi sáng, Miu và Bống bắt đầu cuộc phiêu lưu: {topic}.",
"Hai bạn bước vào khu rừng đầy ánh nắng.",
"Bỗng một bạn nhỏ cần giúp đỡ.",
"Miu nghĩ ra kế hoạch đầu tiên.",
"Bống động viên mọi người.",
"Cả hai cùng hợp tác vượt thử thách.",
"Những người bạn mới xuất hiện.",
"Một chướng ngại vật cản đường.",
"Miu dùng lòng dũng cảm vượt qua.",
"Bống dùng sự thông minh giúp đỡ.",
"Cả nhóm tiến gần mục tiêu.",
"Hy vọng lại xuất hiện.",
"Thử thách cuối cùng bắt đầu.",
"Miu và Bống không bỏ cuộc.",
"Mọi người cùng chung sức.",
"Phép màu của lòng tốt xuất hiện.",
"Cảnh vật trở nên rực rỡ.",
"Các con vật vui mừng.",
"Miu mỉm cười hạnh phúc.",
"Bống cảm ơn tất cả.",
"Cầu vồng xuất hiện trên bầu trời.",
"Cả nhóm chơi đùa vui vẻ.",
"Một bài học ý nghĩa được kể.",
"Hẹn gặp lại ở tập tiếp theo."
]

open("story.txt","w",encoding="utf-8").write("\n".join(story))
