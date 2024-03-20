SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

CREATE DATABASE IF NOT EXISTS `subscriber` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `subscriber`;

DROP TABLE IF EXISTS `subscriber`;
CREATE TABLE IF NOT EXISTS `subscriber` (
  `screening_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `user_email` VARCHAR(255) NOT NULL,
  `creation_timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`screening_id`, `user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `subscriber` (`screening_id`, `user_id`, `user_email`) VALUES
(1, 1, 'kheng_hin@yahoo.com'),
(1, 2, 'ritikab.2022@scis.smu.edu.sg'),
(3, 3, 'ritika.bajpai17@gmail.com'),
(3, 1, 'kheng_hin@yahoo.com'),
(3, 4, 'khsiew.2022@scis.smu.edu.sg');



COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;