from pydantic import BaseModel, Field


class ElectiveCourse(BaseModel):
    semester: str = Field(..., description="学期", examples=["2023.1"])
    class_name: str = Field(
        ..., description="教学班名称", examples=["高等数学(20232-23)[小2班]"]
    )
    class_type: str = Field(..., description="课程类型", examples=["必修课"])
    class_assessment_method: str = Field(..., description="考核方式", examples=["考试"])
    class_info: str = Field(
        ..., description="上课信息", examples=["第1-4周 星期一 第7,8节[31-313]"]
    )
    class_number: str = Field(..., description="课程编号", examples=["19"])
    credit: float = Field(..., description="学分", examples=[3.0])
    teacher: str = Field(..., description="教师", examples=["张三"])


class ScheduledCourse(BaseModel):
    class_span: str = Field(..., description="上课时间", alias="classSpan")
    course: str = Field(..., description="课程名称", alias="course")
    course_name: str = Field(..., description="详细课程名称", alias="className")
    week_span: str = Field(..., description="周数", alias="weekSpan")
    course_type: str = Field(..., description="是否为必修课", alias="courseRequire")
    teacher: str = Field(..., description="教师姓名", alias="teacherName")
    week_day: int = Field(..., description="星期几", alias="weekDay")
    class_room: str = Field(..., description="教室", alias="classRoom")
    pk_type: str = Field(..., description="课程类型", alias="pkType")


class GPA(BaseModel):
    student_name: str = Field(..., description="学生名称")
    gpa: str = Field(..., description="绩点")
    status: str = Field(..., description="状态")


class Score(BaseModel):
    semester: str = Field(..., description="课程学期", examples=["2023.1"])
    course_name: str = Field(..., description="课程名", examples=["高等数学"])
    course_nature: str = Field(..., description="课程性质", examples=["必修"])
    credit: float = Field(..., description="学分", examples=[3.0])
    grade: str = Field(..., description="成绩", examples=["合格", "94"])
