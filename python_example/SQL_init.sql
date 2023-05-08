CREATE DATABASE course_Registration;

USE course_Registration;

CREATE TABLE `Student` (
  `student_id` varchar(9) NOT NULL,
  `student_name` varchar(11) NOT NULL,
    PRIMARY KEY (student_id)
);

INSERT INTO `Student` (`student_id`, `student_name`) VALUES
('d1180377', 'Student1'),
('d1180378', 'Student2'),
('d1180379', 'Student3'),;


CREATE TABLE `Course` (
  `course_id` varchar(9) NOT NULL,
  `course_name` varchar(9) NOT NULL,
  `department` varchar(9) NOT NULL,
  `compulsory` varchar(9) NOT NULL,
  `grade` int NOT NULL,
  `Course_Credits` int NOT NULL,
  `Slot` varchar(9) NOT NULL,
  `linit_people` int NOT NULL,
    PRIMARY KEY (course_id)
);
INSERT INTO `course` (`course_id`,`course_name`,`department`, `compulsory`,`grade`,`Course_Credits`, `Slot`, `linit_people`) VALUES('1001','DM','資工','必修',1, 3,  '8-9', 25),
('1002','LM','資工','必修',2 ,6,  '9-10', 25),('1003','CH','電機','必修',1,3,  '3-4', 25),('1004','EN','電機','必修',1, 3,  '1-2', 25),('1005','DL','資工','選修',3, 3,  '5-6', 25);




CREATE TABLE `enrollments` (
  student_id varchar(9) ,
  course_id varchar(9) ,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id)
);

INSERT INTO `enrollments` (student_id,course_id) VALUES
('d1180377', '1002'),('d1180377', '1003'),('d1180377', '1004')
,('d1180378', '1001'),('d1180378', '1003');

DELIMITER //
CREATE PROCEDURE register_course(IN p_student_id VARCHAR(9), IN p_course_id VARCHAR(9))
BEGIN
  DECLARE current_slot VARCHAR(9);
  DECLARE new_course_slot VARCHAR(9);
  DECLARE current_course_count INT;
  DECLARE new_course_limit INT;
  DECLARE new_course_name VARCHAR(11);
  DECLARE total_credits INT;
  DECLARE new_course_credits INT;

  -- Check if the new course conflicts with existing courses
  SELECT Slot INTO new_course_slot FROM Course WHERE course_id = p_course_id;
  SELECT COUNT(*) INTO current_course_count FROM enrollments e
  JOIN Course c ON e.course_id = c.course_id
  WHERE e.student_id = p_student_id AND c.Slot = new_course_slot;

  -- Check if the new course has the same name as existing courses
  SELECT course_name INTO new_course_name FROM Course WHERE course_id = p_course_id;
  SELECT COUNT(*) INTO current_course_count FROM enrollments e
  JOIN Course c ON e.course_id = c.course_id
  WHERE e.student_id = p_student_id AND c.course_name = new_course_name;

  IF current_course_count = 0 THEN
    -- Check if the new course has available seats
    SELECT linit_people INTO new_course_limit FROM Course WHERE course_id = p_course_id;
    SELECT COUNT(*) INTO current_course_count FROM enrollments WHERE course_id = p_course_id;
    
    IF current_course_count < new_course_limit THEN
      -- Check if the total credits after adding the new course do not exceed 30
      SELECT Course_Credits INTO new_course_credits FROM Course WHERE course_id = p_course_id;
      SELECT SUM(Course_Credits) INTO total_credits FROM enrollments e
      JOIN Course c ON e.course_id = c.course_id
      WHERE e.student_id = p_student_id;

      IF (total_credits + new_course_credits) <= 30 THEN
        -- Register the student for the new course
        INSERT INTO enrollments (student_id, course_id) VALUES (p_student_id, p_course_id);
      ELSE
        SIGNAL SQLSTATE '45000'
          SET MESSAGE_TEXT = 'Error: The total credits after adding the new course exceed the maximum limit of 30 credits.';
      END IF;
    ELSE
      SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: The course is full.';
    END IF;
  ELSE
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Error: The course conflicts with an existing course or has the same name as an existing course.';
  END IF;
END //
DELIMITER ;