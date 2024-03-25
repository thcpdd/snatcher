create table failed_data
(
    id            int auto_increment
        primary key,
    created_at    timestamp    default CURRENT_TIMESTAMP not null,
    username      varchar(255) default ''                not null,
    course_name   varchar(255) default ''                not null,
    failed_reason varchar(255) default ''                not null,
    log_key       varchar(255) default ''                not null,
    port          int          default 0                 not null
);

create table physical_education_course
(
    id          int auto_increment
        primary key,
    course_name varchar(255) default '' not null comment '课程名称',
    course_id   varchar(255) default '' not null comment '课程id',
    grade       int          default 0  not null comment '年级',
    study_year  int          default 0  not null comment '学年',
    term        varchar(10)  default '' not null comment '学期'
);

create table public_choice_course
(
    id          int auto_increment
        primary key,
    course_name varchar(255) default '' not null comment '课程名称',
    course_id   varchar(255) default '' not null comment '课程id',
    course_no   varchar(255) default '' not null comment '课程号',
    study_year  int          default 0  not null comment '学年',
    term        varchar(10)  default '' not null comment '学期'
);

create table selected_course_data
(
    id          int auto_increment comment '主键'
        primary key,
    username    varchar(255) default ''                null comment '学号',
    email       varchar(255) default ''                null comment '邮箱',
    course_name varchar(255)                           null comment '课程名称',
    created_at  timestamp    default CURRENT_TIMESTAMP null comment '创建时间',
    updated_at  timestamp    default CURRENT_TIMESTAMP null comment '更新时间',
    is_deleted  tinyint(1)   default 0                 null comment '是否有效',
    log_key     varchar(255)                           null comment '日志key'
);

create table verify_codes
(
    id          int auto_increment
        primary key,
    username    varchar(20) default ''                null,
    verify_code varchar(40) default ''                null,
    is_used     tinyint(1)  default 0                 null,
    create_at   timestamp   default CURRENT_TIMESTAMP null,
    constraint verify_code
        unique (verify_code)
);


