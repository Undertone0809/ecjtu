"""
暂时用来做开发测试,后续加入tests文件夹.
"""

from User import User

long = User("2022211003000112", "20030115b")

# 登录成功则执行以下函数
# 读取今天的课程表
print(long.get_classes())
# 读取2024-04-12的课程表
print(long.get_classes("2024-04-12"))
# 读取本周课程表并保存到文件
print(long.get_class_table_tofile())
# 读取个人绩点记录
print(long.get_grade_count())
# 读取个人2023.1学期的成绩记录
print(long.get_grade_from_semester("2023.1"))
# 读取个人2023.1学期的成绩记录并保存到文件
print(long.get_grade_from_semester_tofile("2023.1"))
