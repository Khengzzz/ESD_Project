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
  `screening_id` INT NOT NULL,
  `seat_id` JSON NOT NULL,
  `quantity` INT NOT NULL,
  `booking_status` ENUM('Pending', 'Confirmed', 'Refunded') NOT NULL DEFAULT 'Pending',
  `payment_transaction_id` VARCHAR(255),
  `refund_transaction_id` VARCHAR(255),
  `creation_timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `booking` (`user_id`, `screening_id`, `seat_id`, `quantity`, `booking_status`, `payment_transaction_id`, `refund_transaction_id`)
VALUES
(1, 1, '{"seats": [1,2]}', 2, 'Confirmed', 'ABC123', NULL),
(2, 3, '{"seats": [3,4,5]}', 3, 'Pending', NULL, NULL),
(3, 3, '{"seats": [1,2]}', 4, 'Pending', NULL, NULL),
(1, 2, '{"seats": [10,11,12]}', 3, 'Refunded', 'DEF456', 'REF789'),
(4, 6, '{"seats": [13,14,15]}', 3, 'Confirmed', 'GHI789', NULL),
(2, 4, '{"seats": [16,17]}', 2, 'Confirmed', 'JKL012', NULL),
(3, 15, '{"seats": [40,41]}', 2, 'Confirmed', 'MNO345', NULL),
(5, 16, '{"seats": [42,43]}', 2, 'Pending', NULL, NULL),
(1, 17, '{"seats": [44,45,46,47]}', 4, 'Confirmed', 'ABC123', NULL),
(2, 18, '{"seats": [48]}', 1, 'Pending', NULL, NULL),
(3, 19, '{"seats": [49,50]}', 2, 'Pending', NULL, NULL);


COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
