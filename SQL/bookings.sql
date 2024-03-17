SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

CREATE DATABASE IF NOT EXISTS `booking_management` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `booking_management`;

DROP TABLE IF EXISTS `booking`;
CREATE TABLE IF NOT EXISTS `booking` (
  `booking_id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `screening_id` INT NOT NULL,
  `seat_id` JSON NOT NULL,
  `quantity` INT NOT NULL,
  `booking_status` ENUM('Pending', 'Confirmed', 'Refunded') NOT NULL DEFAULT 'Pending',
  `payment_transaction_id` VARCHAR(255),
  `refund_transaction_id` VARCHAR(255),
  `creation_timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `booking` (`user_id`, `email`, `screening_id`, `seat_id`, `quantity`, `booking_status`, `payment_transaction_id`, `refund_transaction_id`)
VALUES
(1, 'user1@example.com', 1, '{"seats": [1,2]}', 2, 'Confirmed', 'PY156', NULL),
(2, 'user2@example.com', 2, '{"seats": [3,4,5]}', 3, 'Refunded', 'PY839', 'REF712'),
(3, 'user3@example.com', 3, '{"seats": [1,2]}', 2, 'Pending', NULL, NULL),
(1, 'user1@example.com', 1, '{"seats": [1,2,3]}', 3, 'Pending', NULL, NULL),
(4, 'user4@example.com', 2, '{"seats": [1,2,3]}', 3, 'Pending', NULL, NULL),
(2, 'user2@example.com', 3, '{"seats": [4,5]}', 2, 'Pending', NULL, NULL),
(3, 'user3@example.com', 1, '{"seats": [1,5]}', 2, 'Pending', NULL, NULL),
(5, 'user5@example.com', 2, '{"seats": [3,4]}', 2, 'Confirmed', 'PY934', NULL),
(1, 'user1@example.com', 3, '{"seats": [2]}', 1, 'Refunded', 'PY837', 'REF5690'),
(2, 'user2@example.com', 1, '{"seats": [4]}', 1, 'Pending', NULL, NULL),
(3, 'user3@example.com', 2, '{"seats": [5]}', 1, 'Pending', NULL, NULL);


COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
