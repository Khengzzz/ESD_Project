SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

CREATE DATABASE IF NOT EXISTS `notifications` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `notifications`;

DROP TABLE IF EXISTS `notifications`;
CREATE TABLE IF NOT EXISTS `notifications` (
  `notification_id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `notification_content` TEXT NOT NULL,
  `delivery_status` ENUM('Pending', 'Notified') NOT NULL DEFAULT 'Pending',
  `creation_timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `notifications` (`user_id`, `notification_content`, `delivery_status`) VALUES
(1, 'Your booking for Event _ has been confirmed. Your seat is at 10A', 'Pending'),
(2, 'Your refund of $50.50 has been made', 'Notified'),
(5, 'We apologise but Event _ had been cancelled and we have made a redund of $18 back', 'Pending'),
(7, 'You have subsribed to notifications! We will update you once there are seats available', 'Notified');
(8, 'There is a seat available for Event _. Grab it now!', 'Notified');

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
