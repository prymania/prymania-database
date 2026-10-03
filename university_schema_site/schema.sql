-- ============================================================
--  schema.sql — ฐานข้อมูลกรณีศึกษา (ชุดเดียวกับ prymania_DBLabScript.sql ที่ใช้ในชั้นเรียน)
--  รันไฟล์นี้ใน DBeaver / MySQL Workbench ครั้งเดียวก่อนเปิดเว็บ
-- ============================================================
CREATE DATABASE IF NOT EXISTS university;
USE university;

DROP TABLE IF EXISTS enroll;
DROP TABLE IF EXISTS section;
DROP TABLE IF EXISTS subject;
DROP TABLE IF EXISTS lecturer;
DROP TABLE IF EXISTS student;

/*  drop table ******************************;

drop table if exists enroll;
drop table if exists section;
drop table if exists subject;
drop table if exists lecturer;
drop table if exists student;


คำสั่งเพื่อดูโครงสร้าง table เช่น table student;
describe student;

คำสั่งเพื่อเช็คว่าใน account เรามี table ใดบ้าง;
show tables;

*/


-- ******************** student ********************
create table student(
	stdid		varchar(10),
	name		varchar(50),
	major		varchar(20),
	gpa			numeric(3,2),
	birthday	date,
constraint std_pk	primary key	(stdid),
constraint std_gpa	check		(gpa between 0.0 and 4.0));

-- ******************** subject ********************
create table subject(
	subid		varchar(10),
	name		varchar(30)	not null,
	credit		int,
	major		varchar(20),
	pre			varchar(10),
constraint sub_pk		primary key	(subid),
constraint sub_fk_pre	foreign key	(pre)	references subject(subid));

-- ******************** lecturer *******************
create table lecturer(
	lecid		varchar(10),
	name		varchar(30),
	salary		int,
	major		varchar(30),
constraint lec_pk	primary key	(lecid));

-- ******************** section ********************
create table section(
	secid		int	AUTO_INCREMENT,
	subid		varchar(10),
	lecid		varchar(10),
	term		varchar(6),
constraint sec_pk		primary key	(secid),
constraint sec_fk_sub	foreign key	(subid)	references subject(subid)	on delete cascade,
constraint sec_fk_lec	foreign key	(lecid)	references lecturer(lecid)	on delete cascade,
constraint sec_uk		unique		(subid, lecid, term));

-- ******************** enroll *********************
create table enroll(
	secid		int,
	stdid		varchar(10),
	grade		char,
constraint enroll_pk		primary key	(secid, stdid),
constraint enroll_fk_sec	foreign key	(secid)	references section(secid)	on delete cascade,
constraint enroll_fk_std	foreign key	(stdid)	references student(stdid)	on delete cascade,
constraint enroll_grade		check		(grade in ('A', 'B', 'C', 'D', 'F')));


/*********************************************************/;
/************** insert data statement ********************/;
/*********************************************************/;


-- ******************** student ********************
insert into student values
	('60001',	'Rukawa',	'CS',		3.75,	'2010-05-13'),
	('60002',	'Sakuragi',	'CS',		null,	'2010-01-15'),
	('60003',	'Mitsui',	'CS',		2.00,	'2013-06-25'),
	('60004',	'Sendoh',	'CS',		3.98,	'2012-12-08'),
	('60005',	null,		'Math',		2.78,	'2011-09-02'),
	('60006',	'Nobita',	'Math',		1.55,	null),
	('60007',	'L',		'Art',		3.98,	'2011-01-31'),
	('60008',	'Kira',		'Art',		3.05,	'2015-02-25'),
	('60009',	'Killua',	'English',	3.98,	'2015-03-31'),
	('60010',	'Gon',		'English',	1.55,	'2016-02-20'),
	('60011',	'Kurapika',	'English',	3.98,	'2016-02-20'),
	('60012',	'Hisoka',	'CS',		2.00,	'2015-06-06'),
	('60013',	'Gon',		'CS',		2.78,	'2017-07-07'),
	('60014',	'Light',	'Physics',	2.55,	'2016-10-10'),
	('60015',	'Near',		'Physics',	4.00,	'2014-08-24'),
	('60016',	'Mello',	'Physics',	1.55,	'2015-12-13'),
	('70022',	null,		'English',	null,	null),
	('70033',	'Zoro',		null,		3.98,	'2012-02-29'),
	('70034',	'Luffy',	null,		1.55,	'2010-02-11'),
	('70035',	'Nami',		null,		2.85,	null),
	('70036',	'Sanji',	'CS',		2.78,	null),
	('70037',	'Chopper',	null,		null,	'2011-12-24');

-- ******************** subject ********************
insert into subject values
	('CS001',	'Programming',		3,	'CS',		null),
	('CS002',	'Java',				3,	'CS',		'CS001'),
	('CS003',	'Web Design',		2,	'CS',		'CS001'),
	('CS004',	'Database',			3,	'CS',		'CS001'),
	('CS005',	'Graphics',			3,	'CS',		'CS002'),
	('CS006',	'Mobile Apps',		2,	'CS',		'CS002'),
	('CS007',	'Robotics',			4,	'CS',		'CS002'),
	('CS008',	'AI',				3,	'CS',		'CS002'),
	('CS009',	'Project',			6,	'CS',		'CS004'),
	('CS010',	'Security',			3,	'CS',		'CS004'),
	('MA001',	'Mathematics',		3,	'Math',		null),
	('MA002',	'Discrete Math',	4,	'Math',		'MA001'),
	('MA003',	'Statistics',		3,	'Math',		'MA002'),
	('TH001',	'Thai',				1,	'Thai',		null),
	('TH002',	'Thai Writing',		1,	'Thai',		'TH001'),
	('EN001',	'English',			2,	'English',	null),
	('EN002',	'Reading',			3,	'English',	'EN001'),
	('EN003',	'Conversation',		3,	'English',	'EN001'),
	('EN004',	'Writing',			3,	'English',	'EN002'),
	('PH001',	'Physics',			3,	'Physics',	null);

-- ******************** lecturer *******************
insert into lecturer values
	('t01',	'Peter Parker',	40000,	'CS'),
	('t02',	'Steve Roger',	50000,	'CS'),
	('t03',	'Yoda',			80000,	'Math'),
	('t04',	'Post Malone',	47000,	'Thai'),
	('t05',	'IronMan',		65000,	'Thai'),
	('t06',	'Goku',			20000,	'English'),
	('t07',	'Vegeta',		25000,	'English'),
	('t08',	'Cell',			70000,	'English'),
	('t09',	'Frieza',		60000,	'English'),
	('t10',	'Piccolo',		15000,	'Art'),
	('t11',	'Batman',		null,	'DC'),
	('t12',	'Wolverine',	null,	'DC'),
	('t13',	'Thor',			60000,	'DC'),
	('t14',	'Yoda',			80000,	'CS'),
	('t15',	'Gohan',		20000,	'Math'),
	('t16',	'Levi',			null,	'Physics');

-- ******************** section ********************
insert into section(subid, lecid, term) values
	('CS001',	't01',	'2023-1'),		-- secid 1
	('CS004',	't01',	'2023-1'),		-- secid 2
	('CS005',	't01',	'2023-1'),		-- secid 3
	('CS003',	't02',	'2023-1'),		-- secid 4
	('CS006',	't02',	'2023-1'),		-- secid 5
	('CS002',	't01',	'2023-2'),		-- secid 6
	('CS003',	't01',	'2023-2'),		-- secid 7
	('CS004',	't03',	'2023-3'),		-- secid 8
	('CS007',	't05',	'2023-3'),		-- secid 9
	('CS008',	't01',	'2023-3'),		-- secid 10

	('CS001',	't01',	'2024-1'),		-- secid 11
	('CS004',	't01',	'2024-1'),		-- secid 12
	('CS005',	't02',	'2024-1'),		-- secid 13

	('CS008',	't02',	'2024-2'),		-- secid 14
	('CS001',	't01',	'2024-2'),		-- secid 15
	('CS002',	't01',	'2024-2'),		-- secid 16
	('CS005',	't01',	'2024-2'),		-- secid 17
	('MA001',	't03',	'2024-2'),		-- secid 18
	('MA002',	't05',	'2024-2'),		-- secid 19

	('CS004',	't01',	'2024-3'),		-- secid 20
	('CS004',	't03',	'2024-3'),		-- secid 21
	('CS004',	't05',	'2024-3'),		-- secid 22
	('MA002',	't05',	'2024-3'),		-- secid 23

	('CS001',	't02',	'2024-1'),		-- secid 24
	('CS006',	't03',	'2024-1'),		-- secid 25
	('CS007',	't02',	'2024-1'),		-- secid 26
	('MA001',	't05',	'2024-1'),		-- secid 27
	('CS009',	't02',	'2024-2'),		-- secid 28
	('CS002',	't02',	'2024-2'),		-- secid 29
	('CS002',	't04',	'2024-2'),		-- secid 30

	('CS009',	't02',	'2024-3'),		-- secid 31
	('CS002',	't13',	'2024-3'),		-- secid 32
	('CS002',	't05',	'2024-3'),		-- secid 33

	('EN001',	't06',	'2025-1'),		-- secid 34
	('CS001',	't01',	'2025-1'),		-- secid 35
	('CS003',	't03',	'2025-1'),		-- secid 36
	('MA001',	't06',	'2025-1'),		-- secid 37
	('EN001',	't07',	'2025-1'),		-- secid 38

	('CS001',	't02',	'2025-2'),		-- secid 39
	('CS008',	't03',	'2025-2'),		-- secid 40
	('CS009',	't04',	'2025-2'),		-- secid 41
	('EN003',	't08',	'2025-2'),		-- secid 42

	('TH001',	't04',	'2025-3'),		-- secid 43
	('TH002',	't04',	'2025-3'),		-- secid 44 (ไม่มีคนลง)
	('CS010',	't02',	'2025-3'),		-- secid 45
	('CS002',	't14',	'2025-3'),		-- secid 46
	('MA003',	't03',	'2025-3'),		-- secid 47
	('EN003',	't09',	'2025-3'),		-- secid 48
	('CS001',	't10',	'2025-3'),		-- secid 49
	('MA001',	't15',	'2025-3'),		-- secid 50

	('CS004',	't01',	'2026-1'),		-- secid 51
	('CS009',	't03',	'2026-1');		-- secid 52 (ไม่มีคนลง)

-- ******************** enroll *********************
insert into enroll values
	(1,		'60001',	'A'),
	(1,		'60002',	'B'),
	(1,		'60005',	'C'),
	(1,		'60006',	'F'),
	(1,		'60010',	'F'),

	(2,		'60001',	'C'),
	(2,		'60002',	'A'),
	(2,		'60005',	'D'),
	(2,		'60010',	'F'),

	(4,		'60004',	'F'),

	(5,		'60005',	'C'),
	(5,		'60006',	'A'),
	(5,		'60003',	'F'),
	(5,		'60004',	'B'),

	(6,		'60001',	'B'),
	(6,		'60002',	'F'),
	(6,		'60003',	'B'),
	(6,		'60007',	'A'),

	(7,		'60005',	'B'),
	(7,		'60007',	'A'),

	(8,		'60001',	'A'),
	(8,		'60007',	'B'),

	(9,		'60003',	'D'),
	(9,		'60004',	'C'),

	(10,	'60001',	'A'),
	(10,	'60003',	'F'),
	(10,	'60009',	'B'),

	(11,	'60012',	'A'),

	(12,	'60002',	'A'),
	(12,	'60004',	'A'),
	(12,	'60005',	'B'),
	(12,	'60006',	'F'),

	(13,	'60004',	'A'),
	(13,	'60006',	'F'),

	(14,	'60010',	'B'),
	(14,	'60012',	'B'),

	(15,	'60001',	'A'),
	(15,	'60004',	'A'),
	(15,	'60003',	'B'),
	(15,	'60010',	'F'),

	(16,	'60013',	'A'),
	(16,	'60010',	'D'),

	(17,	'60013',	'B'),
	(17,	'60007',	'C'),

	(18,	'60005',	'A'),
	(18,	'60006',	'D'),
	(18,	'60013',	'C'),

	(19,	'60001',	'B'),
	(19,	'60002',	'B'),
	(19,	'60003',	'A'),
	(19,	'60007',	'A'),
	(19,	'60005',	'A'),

	(20,	'60013',	'F'),
	(20,	'60009',	'C'),

	(21,	'60006',	'F'),

	(22,	'60008',	'F'),
	(22,	'70034',	'F'),
	(23,	'60008',	'F'),
	(23,	'70034',	'F'),

	(28,	'60004',	'A'),

	(30,	'70022',	'A'),

	(31,	'60001',	'A'),
	(31,	'60007',	'B'),

	(34,	'70033',	null),
	(34,	'60009',	'A'),
	(34,	'60011',	'A'),
	(34,	'60010',	'C'),

	(35,	'70033',	null),
	(35,	'60010',	'A'),

	(36,	'70033',	null),
	(36,	'70022',	null),
	(36,	'60011',	'B'),

	(37,	'70022',	null),

	(38,	'60013',	'B'),
	(38,	'70034',	'F'),

	(39,	'70034',	'D'),
	(39,	'70022',	'C'),

	(40,	'60004',	'A'),
	(40,	'60009',	'A'),

	(41,	'60007',	'A'),

	(42,	'60009',	'B'),
	(42,	'60011',	'C'),
	(42,	'60010',	'F'),

	(43,	'60010',	'A'),
	(43,	'60013',	'A'),
	(43,	'70022',	'B'),

	(45,	'60001',	'B'),
	(45,	'60004',	'A'),
	(45,	'60009',	null),

	(46,	'70034',	'C'),
	(46,	'60002',	'B'),

	(47,	'60005',	'A'),
	(47,	'60006',	null),

	(48,	'60011',	'A'),
	(48,	'70022',	'F'),

	(49,	'70036',	'B'),
	(49,	'70037',	'C'),

	(50,	'70036',	'D'),

	(51,	'60008',	null),
	(51,	'70034',	null);
