SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

CREATE DATABASE IF NOT EXISTS `event_management` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `event_management`;

DROP TABLE IF EXISTS `event`;
CREATE TABLE IF NOT EXISTS `event` (
  `event_id` INT AUTO_INCREMENT PRIMARY KEY,
  `event_name` VARCHAR(255) NOT NULL,
  `event_description` TEXT NOT NULL,
  `event_date_time` DATETIME NOT NULL,
  `location` VARCHAR(255) NOT NULL,
  `event_status` ENUM('active', 'cancelled') NOT NULL DEFAULT 'active',
  `ticket_price` DECIMAL(10, 2) NOT NULL,
  `capacity` INT NOT NULL,
  `hall_number` INT NOT NULL,  -- Adding hall_number column
  `creation_timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `event` (`event_name`, `event_description`, `event_date_time`, `location`, `event_status`, `ticket_price`, `capacity`, `hall_number`) VALUES
('Music Concert', 'An evening of live music performances', '2024-03-15 19:00:00', 'Concert Hall', 'active', 50.00, 500, 1),
('Food Festival', 'A culinary extravaganza featuring various cuisines', '2024-04-20 11:00:00', 'Concert Hall', 'active', 20.00, 1000, 2),
('Tech Conference', 'A conference on the latest trends in technology', '2024-05-10 09:00:00', 'Concert Hall', 'active', 100.00, 300, 3),
('Charity Gala', 'A fundraising event for a local charity organization', '2024-06-05 18:30:00', 'Concert Hall', 'active', 75.00, 200, 4),
('Fitness Expo', 'A health and fitness exhibition with workout sessions', '2024-07-15 10:00:00', 'Concert Hall', 'active', 30.00, 500, 5),
('Art Exhibition', 'An exhibition showcasing contemporary artworks', '2024-08-20 12:00:00', 'Concert Hall', 'active', 10.00, 200, 1),
('Comedy Show', 'A night of laughter with stand-up comedians', '2024-09-10 20:00:00', 'Concert Hall', 'active', 35.00, 150, 2),
('Movie Marathon', 'A marathon screening of classic and popular films', '2024-10-25 14:00:00', 'Concert Hall', 'active', 15.00, 300, 3),
('Fashion Show', 'A runway showcase of the latest fashion trends', '2024-11-15 19:30:00', 'Concert Hall', 'active', 50.00, 250, 4),
('Business Summit', 'A summit for industry leaders to discuss business strategies', '2024-12-05 08:30:00', 'Concert Hall', 'active', 150.00, 400, 5);

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
