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
  `event_id` INT NOT NULL,
  `seat_id` JSON NOT NULL,
  `booking_status` ENUM('Pending', 'Confirmed', 'Refunded') NOT NULL DEFAULT 'Pending',
  `payment_transaction_id` VARCHAR(255),
  `payment_status` ENUM('Succeeded', 'Pending', 'Failed'),
  `refund_transaction_id` VARCHAR(255),
  `creation_timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `booking` (`user_id`, `event_id`, `seat_id`, `booking_status`, `payment_transaction_id`, `payment_status`, `refund_transaction_id`)
VALUES
(1, 1, '{"row": 10, "seat": "A"}', 'Confirmed', 'ABC123', 'succeeded', NULL),
(2, 3, '{"row": 5, "seat": "C"}', 'Pending', NULL, NULL, NULL),
(3, 7, '{"row": 2, "seat": "D"}', 'Pending', NULL, NULL, NULL),
(1, 2, '{"row": 15, "seat": "B"}', 'Refunded', 'DEF456', 'failed', 'REF789'),
(4, 6, '{"row": 8, "seat": "F"}', 'Confirmed', 'GHI789', 'succeeded', NULL),
(2, 4, '{"row": 3, "seat": "A"}', 'Confirmed', 'JKL012', 'succeeded', NULL),
(3, 5, '{"row": 12, "seat": "E"}', 'Confirmed', 'MNO345', 'succeeded', NULL),
(5, 8, '{"row": 20, "seat": "G"}', 'Pending', NULL, NULL, NULL);

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
