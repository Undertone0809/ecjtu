---
title: ecjtu-api
language_tabs:
  - shell: Shell
  - http: HTTP
  - javascript: JavaScript
  - ruby: Ruby
  - python: Python
  - php: PHP
  - java: Java
  - go: Go
toc_footers: []
includes: []
search: true
code_clipboard: true
highlight_theme: darkula
headingLevel: 2
generator: "@tarslib/widdershins v4.0.23"

---

# ecjtu-api

Base URLs:

# Authentication

# 登录

<a id="opIdlogin_login_post"></a>

## POST 登录

POST /login

登录并获取token,以下所有接口都需要token才可以使用

> Body 请求参数

```json
{
  "stud_id": "string",
  "password": "string"
}
```

### 请求参数

|名称|位置|类型|必选|中文名|说明|
|---|---|---|---|---|---|
|body|body|[UserLoginSchema](#schemauserloginschema)| 否 | UserLoginSchema|none|

> 返回示例

> 200 Response

```json
"string"
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|string|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

# GPA

<a id="opIdgpa_gpa_get"></a>

## GET 获取GPA

GET /gpa

获取当学期GPA

### 请求参数

|名称|位置|类型|必选|中文名|说明|
|---|---|---|---|---|---|
|token|header|string| 否 | Token|none|

> 返回示例

> 200 Response

```json
"string"
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|string|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

# 课表

<a id="opIdschedule_schedule_get"></a>

## GET 获取当天课表

GET /schedule

获取当天课表

### 请求参数

|名称|位置|类型|必选|中文名|说明|
|---|---|---|---|---|---|
|token|header|string| 否 | Token|none|

> 返回示例

> 200 Response

```json
"string"
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|string|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<a id="opIdschedule_date_schedule__date__get"></a>

## GET 获取指定日期课表

GET /schedule/{date}

获取指定日期课表,指定日期格式为yyyy-mm-dd

### 请求参数

|名称|位置|类型|必选|中文名|说明|
|---|---|---|---|---|---|
|date|path|string| 是 | Date|none|
|token|header|string| 否 | Token|none|

> 返回示例

> 200 Response

```json
"string"
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|string|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<a id="opIdschedule_week_schedule_week_get"></a>

## GET 获取本周课表

GET /schedule/week

获取本周课表

### 请求参数

|名称|位置|类型|必选|中文名|说明|
|---|---|---|---|---|---|
|token|header|string| 否 | Token|none|

> 返回示例

> 200 Response

```json
"string"
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|string|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

# 成绩

<a id="opIdscore_score_get"></a>

## GET 获取当前成绩

GET /score

获取当学期成绩

### 请求参数

|名称|位置|类型|必选|中文名|说明|
|---|---|---|---|---|---|
|token|header|string| 否 | Token|none|

> 返回示例

> 200 Response

```json
"string"
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|string|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<a id="opIdscore_semester_score__semester__get"></a>

## GET 获取指定学期成绩

GET /score/{semester}

获取指定学期成绩,semester格式为yyyy.1或yyyy.2

### 请求参数

|名称|位置|类型|必选|中文名|说明|
|---|---|---|---|---|---|
|semester|path|string| 是 | Semester|none|
|token|header|string| 否 | Token|none|

> 返回示例

> 200 Response

```json
"string"
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|string|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

# 选课情况

<a id="opIdelective_courses_elective_courses_get"></a>

## GET 获取当前选课情况

GET /elective_courses

获取当前学期选课情况

### 请求参数

|名称|位置|类型|必选|中文名|说明|
|---|---|---|---|---|---|
|token|header|string| 否 | Token|none|

> 返回示例

> 200 Response

```json
"string"
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|string|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<a id="opIdelective_courses_semester_elective_courses__semester__get"></a>

## GET 获取指定学期选课情况

GET /elective_courses/{semester}

获取指定学期选课情况,semester格式为yyyy.1或yyyy.2

### 请求参数

|名称|位置|类型|必选|中文名|说明|
|---|---|---|---|---|---|
|semester|path|string| 是 | Semester|none|
|token|header|string| 否 | Token|none|

> 返回示例

> 200 Response

```json
"string"
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|string|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|