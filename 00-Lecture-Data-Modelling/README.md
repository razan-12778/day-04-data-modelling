
## Normal Forms Schema

[dbdiagram.io](https://dbdiagram.io/) representation of Normal form schemas for comparison.

### 1NF schema

```text
Table StudentClassesNot1NF {
  student_id int [primary key]
  student_name varchar
  student_email varchar
  course1 varchar
  course2 varchar
  course3 varchar
  instructor1 varchar
  instructor2 varchar
  instructor3 varchar
  instructor1_email varchar
  instructor2_email varchar
  instructor3_email varchar
  instructor1_dept varchar
  instructor2_dept varchar
  instructor3_dept varchar
}

Table StudentClasses1NF {
  student_id int [primary key]
  student_name varchar
  student_email varchar
  course_id varchar [primary key]
  course_name varchar
  instructor_name varchar
  instructor_email varchar
  instructor_dept varchar
}
```

### 2NF

```text
Table students {
  student_id uuid [pk, not null]
  student_name varchar [not null]
  student_email varchar [not null]
}

Table courses {
  course_id varchar [pk, not null]
  course_name varchar [not null]
  instructor_name varchar [not null]
  instructor_email varchar [not null]
  instructor_dept varchar [not null]
}

Table enrollments {
  student_id uuid [pk, not null]
  course_id varchar [not null]
  enrollment_date datetime [not null]
}

Ref: students.student_id < enrollments.student_id
Ref: enrollments.course_id > courses.course_id
```

### 3NF

```text
Table students {
  student_id uuid [pk, not null]
  student_name varchar [not null]
  student_email varchar [not null]
}

Table courses {
  course_id varchar [pk, not null]
  course_name varchar [not null]
  instructor_id varchar [not null]
}

Table instructors {
  instructor_id varchar [pk, not null]
  instructor_name varchar [not null]
  instructor_email varchar [not null]
  instructor_dept varchar [not null]
}

Table enrollments {
  student_id uuid [pk, not null]
  course_id varchar [not null]
  enrollment_date datetime [not null]
}

Ref: students.student_id < enrollments.student_id
Ref: enrollments.course_id > courses.course_id
Ref: instructors.instructor_id < courses.instructor_id
```
