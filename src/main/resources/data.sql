CREATE database Insurance;

use Insurance;

CREATE table User (
 userId int not null,
 loginId char(10),
 password char(100),
 nickName char(100),
 realName char(25),
 phone int,
 birthYear int,
 gender char(10),
 primary key(userId)
);

INSERT INTO User values(1,"testuser","1234","테스트유저0","유저0",01012345678,20000101,"남자");
INSERT INTO User values(2,"testuser1","1234","테스트유저1","유저1",01011112222,19991231,"남자");
INSERT INTO User values(3,"testuser2","2222","테스트유저2","유저2",01022223333,1980505,"여자");

SELECT *
FROM User;


INSERT INTO age_rate (id, age_start, age_end, rate) VALUES (1, 0, 19, 1.0);
INSERT INTO age_rate (id, age_start, age_end, rate) VALUES (2, 20, 29, 1.2);
INSERT INTO age_rate (id, age_start, age_end, rate) VALUES (3, 30, 39, 1.4);
INSERT INTO age_rate (id, age_start, age_end, rate) VALUES (4, 40, 49, 1.9);
INSERT INTO age_rate (id, age_start, age_end, rate) VALUES (5, 50, 100, 2.6);

