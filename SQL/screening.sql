DROP DATABASE IF EXISTS `screening`;
CREATE DATABASE IF NOT EXISTS `screening` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `screening`;

DROP TABLE IF EXISTS `screening`;
CREATE TABLE IF NOT EXISTS `screening` (
    `screening_id` INT AUTO_INCREMENT PRIMARY KEY,
    `movie_name` VARCHAR(255) NOT NULL,
    `movie_description` TEXT NOT NULL,
    `movie_date_time` DATETIME NOT NULL,
    `location` VARCHAR(255) NOT NULL,
    `movie_status` ENUM('active', 'cancelled') NOT NULL DEFAULT 'active',
    `ticket_price` DECIMAL(10, 2) NOT NULL,
    `capacity` INT NOT NULL,
    `hall_number` INT NOT NULL,
    `creation_timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `seat`;
CREATE TABLE IF NOT EXISTS `seat` (
    `screening_id` INT NOT NULL,
    `seat_id` INT NOT NULL,
    `seat_status` ENUM('available', 'booked', 'reserved', 'unavailable') NOT NULL DEFAULT 'available',
    PRIMARY KEY (`screening_id`, `seat_id`),
    FOREIGN KEY (`screening_id`) REFERENCES `screening` (`screening_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `screening` (`movie_name`, `movie_description`, `movie_date_time`, `movie_status`, `ticket_price`, `capacity`, `hall_number`) VALUES
('Action Movie Premiere', 'Be the first to witness the adrenaline-pumping action!', '2024-03-20 18:00:00', 'Showing', 12.00, 100, 1),
('Romantic Comedy Night', 'Fall in love with laughter and romance under the stars', '2024-04-10 20:00:00', 'Showing', 10.00, 80, 2),
('Family Movie Matinee', 'Fun for the whole family with classic animated films', '2024-05-05 14:00:00', 'Showing', 8.00, 150, 3);

INSERT INTO `seat` (`screening_id`, `seat_id`, `seat_status`) VALUES
(1, 1, 'available'),
(1, 2, 'available'),
(1, 3, 'available'),
(1, 4, 'available'),
(1, 5, 'available'),
(2, 1, 'available'),
(2, 2, 'available'),
(2, 3, 'available'),
(2, 4, 'available'),
(2, 5, 'available'),
(3, 1, 'available'),
(3, 2, 'available'),
(3, 3, 'available'),
(3, 4, 'available'),
(3, 5, 'available');