DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `token` varchar(255) DEFAULT NULL,
  `leader_card_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`)
);
INSERT INTO `user` (`name`, `token`, `leader_card_id`) VALUES
("init1", "abc", 1),
("init2", "def", 2);

DROP TABLE IF EXISTS `room`;
CREATE TABLE `room` (
  `room_id` bigint NOT NULL AUTO_INCREMENT,
  `live_id` bigint DEFAULT NULL,
  `joined_user_count` int DEFAULT NULL,
  `max_user_count` int DEFAULT NULL,
  PRIMARY KEY (`room_id`)
  -- UNIQUE KEY `token` (`token`)
);
INSERT INTO `room` (`live_id`, `joined_user_count`, `max_user_count`) VALUES
(1, 2, 4);

DROP TABLE IF EXISTS `room_member`;
CREATE TABLE `room_member` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `room_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`)
  -- UNIQUE KEY `token` (`token`)
);
INSERT INTO `room_member` (`room_id`, `user_id`) VALUES
(1, 1),
(1, 2);

