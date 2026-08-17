import os,re

TOPICS={
1:"Cáo con cứu chim non",
2:"Thỏ lạc trong rừng",
3:"Gấu nhỏ học chia sẻ"
}

cmd=os.environ["PROMPT"]
m=re.search(r"(\d+)",cmd)
day=int(m.group(1)) if m else 1
topic=TOPICS.get(day,cmd)

story=[
f"Vào một buổi sáng đẹp trời, Miu và Bống bắt đầu chuyến phiêu lưu {topic}.",
"Hai bạn nghe thấy tiếng kêu cứu.",
"Một chú chim non bị lạc khỏi tổ.",
"Miu nghĩ ra cách giúp đỡ.",
"Bống tìm thấy chiếc tổ trên cây.",
"Hai bạn cùng đưa chim trở về.",
"Chim mẹ xúc động cảm ơn.",
"Bài học: Lòng tốt luôn tạo nên điều kỳ diệu."
]

open("story.txt","w",encoding="utf-8").write("\n".join(story))
