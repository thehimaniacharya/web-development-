CREATE DATABASE  IF NOT EXISTS `hotel_booking` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `hotel_booking`;
-- MySQL dump 10.13  Distrib 8.0.44, for macos15 (arm64)
--
-- Host: localhost    Database: hotel_booking
-- ------------------------------------------------------
-- Server version	9.5.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'da30abfc-bd47-11f0-b3d2-6ff3787e0fd0:1-377';

--
-- Table structure for table `bookings`
--

DROP TABLE IF EXISTS `bookings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookings` (
  `booking_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `hotel_id` int NOT NULL,
  `room_id` int DEFAULT NULL,
  `room_type` varchar(50) NOT NULL,
  `check_in` date NOT NULL,
  `check_out` date NOT NULL,
  `guests` int NOT NULL,
  `num_nights` int NOT NULL,
  `guest_name` varchar(255) NOT NULL,
  `guest_email` varchar(255) NOT NULL,
  `guest_phone` varchar(20) DEFAULT NULL,
  `special_requests` text,
  `base_price` decimal(10,2) DEFAULT '0.00',
  `peak_surcharge` decimal(10,2) DEFAULT '0.00',
  `room_type_surcharge` decimal(10,2) DEFAULT '0.00',
  `guest_surcharge` decimal(10,2) DEFAULT '0.00',
  `subtotal` decimal(10,2) DEFAULT '0.00',
  `advance_discount_percent` decimal(5,2) DEFAULT '0.00',
  `advance_discount_amount` decimal(10,2) DEFAULT '0.00',
  `total_price` decimal(10,2) NOT NULL,
  `status` varchar(50) DEFAULT 'confirmed',
  `booking_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `cancellation_date` datetime DEFAULT NULL,
  PRIMARY KEY (`booking_id`),
  KEY `user_id` (`user_id`),
  KEY `hotel_id` (`hotel_id`),
  KEY `room_id` (`room_id`),
  CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`hotel_id`) REFERENCES `hotels` (`hotel_id`) ON DELETE CASCADE,
  CONSTRAINT `bookings_ibfk_3` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`room_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookings`
--

LOCK TABLES `bookings` WRITE;
/*!40000 ALTER TABLE `bookings` DISABLE KEYS */;
INSERT INTO `bookings` VALUES (1,2,1,NULL,'single','2026-01-22','2026-01-23',1,1,'acharya02','acharya02@example.com',NULL,NULL,100.00,0.00,0.00,0.00,100.00,0.00,0.00,100.00,'confirmed','2026-01-21 17:19:14',NULL),(2,2,1,NULL,'single','2026-01-22','2026-01-23',1,1,'acharya02','acharya02@example.com',NULL,NULL,100.00,0.00,0.00,0.00,100.00,0.00,0.00,100.00,'confirmed','2026-01-21 17:29:23',NULL),(3,2,7,NULL,'single','2026-01-22','2026-01-23',1,1,'acharya02','acharya02@example.com',NULL,NULL,70.00,0.00,0.00,0.00,70.00,0.00,0.00,70.00,'confirmed','2026-01-21 17:39:33',NULL),(4,2,6,NULL,'single','2026-01-22','2026-01-23',1,1,'acharya02','acharya02@example.com',NULL,NULL,70.00,0.00,0.00,0.00,70.00,0.00,0.00,70.00,'confirmed','2026-01-21 17:46:38',NULL),(5,2,11,NULL,'single','2026-01-22','2026-01-23',1,1,'acharya02','acharya02@example.com',NULL,NULL,100.00,0.00,0.00,0.00,100.00,0.00,0.00,100.00,'confirmed','2026-01-21 17:55:32',NULL),(6,2,1,NULL,'single','2026-01-24','2026-01-28',1,4,'acharya02','acharya02@example.com',NULL,NULL,100.00,0.00,0.00,0.00,400.00,0.00,0.00,400.00,'cancelled','2026-01-23 07:34:39','2026-01-23 14:00:59'),(7,2,1,NULL,'family','2026-01-24','2026-01-25',4,1,'acharya02','acharya02@example.com',NULL,NULL,100.00,0.00,50.00,0.00,150.00,0.00,0.00,150.00,'confirmed','2026-01-23 07:51:17',NULL),(8,2,11,NULL,'family','2026-01-24','2026-01-30',4,6,'acharya02','acharya02@example.com',NULL,NULL,100.00,0.00,50.00,0.00,900.00,0.00,0.00,900.00,'confirmed','2026-01-23 08:00:12',NULL),(9,2,1,NULL,'double','2026-01-24','2026-01-27',2,3,'acharya02','acharya02@example.com',NULL,NULL,100.00,0.00,20.00,10.00,390.00,0.00,0.00,390.00,'confirmed','2026-01-23 08:15:28',NULL),(10,2,1,NULL,'family','2026-01-24','2026-01-31',4,7,'acharya02','acharya02@example.com',NULL,NULL,100.00,0.00,50.00,0.00,1050.00,0.00,0.00,1050.00,'cancelled','2026-01-23 14:02:11','2026-01-23 19:48:06'),(11,2,1,NULL,'double','2026-01-25','2026-01-30',2,5,'acharya02','acharya02@example.com',NULL,NULL,100.00,0.00,20.00,10.00,650.00,0.00,0.00,650.00,'confirmed','2026-01-24 10:15:55',NULL),(12,2,2,NULL,'single','2026-01-25','2026-01-26',1,1,'acharya02','acharya02@example.com',NULL,NULL,90.00,0.00,0.00,0.00,90.00,0.00,0.00,90.00,'confirmed','2026-01-24 15:46:46',NULL),(13,2,2,NULL,'single','2026-01-25','2026-01-26',1,1,'acharya02','acharya02@example.com',NULL,NULL,90.00,0.00,0.00,0.00,90.00,0.00,0.00,90.00,'confirmed','2026-01-24 15:48:36',NULL),(14,2,2,NULL,'single','2026-01-25','2026-01-26',1,1,'acharya02','acharya02@example.com',NULL,NULL,90.00,0.00,0.00,0.00,90.00,0.00,0.00,90.00,'confirmed','2026-01-24 15:49:23',NULL);
/*!40000 ALTER TABLE `bookings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contact_messages`
--

DROP TABLE IF EXISTS `contact_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contact_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `subject` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `submitted_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` enum('new','read','replied') COLLATE utf8mb4_unicode_ci DEFAULT 'new',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contact_messages`
--

LOCK TABLES `contact_messages` WRITE;
/*!40000 ALTER TABLE `contact_messages` DISABLE KEYS */;
INSERT INTO `contact_messages` VALUES (1,'himani acharya','himaniacharya835@gmail.com','room booking','I want to book a room for my family ','2026-01-13 16:31:21','127.0.0.1','new'),(2,'himani acharya','himaniacharya835@gmail.com','room booking','I want to book a room for my family ','2026-01-13 16:31:23','127.0.0.1','new'),(3,'himani acharya','himaniacharya835@gmail.com','room booking','I want to book a room for my family ','2026-01-13 16:31:25','127.0.0.1','new');
/*!40000 ALTER TABLE `contact_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hotels`
--

DROP TABLE IF EXISTS `hotels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hotels` (
  `hotel_id` int NOT NULL AUTO_INCREMENT,
  `city` varchar(50) NOT NULL,
  `title` varchar(100) NOT NULL,
  `description` text,
  `price` decimal(10,2) NOT NULL,
  `image` varchar(100) NOT NULL,
  `address` varchar(255) DEFAULT 'Hotel Address, City, Country',
  PRIMARY KEY (`hotel_id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hotels`
--

LOCK TABLES `hotels` WRITE;
/*!40000 ALTER TABLE `hotels` DISABLE KEYS */;
INSERT INTO `hotels` VALUES (1,'London','Luxury Stay in London','Experience luxury in the heart of London',200.00,'london.jpg','Hotel Address, City, Country'),(2,'Manchester','Urban Elegance','Modern luxury in Manchester',180.00,'manchester.jpg','Hotel Address, City, Country'),(3,'Edinburgh','World Hotel Edinburgh','Classic luxury with castle views',160.00,'edinburgh.jpg','Hotel Address, City, Country'),(4,'Glasgow','Elegant Glasgow','Stylish comfort in Glasgow',150.00,'glasgow.jpg','Hotel Address, City, Country'),(5,'Birmingham','Central Birmingham','Luxury near city centre',150.00,'birmingham.jpg','Hotel Address, City, Country'),(6,'Bristol','Bristol Retreat','Modern comfort in Bristol',140.00,'bristol.jpg','Hotel Address, City, Country'),(7,'Cardiff','Cardiff Comfort','Relaxing stay in Cardiff',130.00,'cardiff.jpg','Hotel Address, City, Country'),(8,'Aberdeen','Aberdeen Grand','Luxury by the coast',140.00,'aberdeen.jpg','Hotel Address, City, Country'),(9,'Belfast','Belfast Luxury','Comfort in Northern Ireland',130.00,'belfast.jpg','Hotel Address, City, Country'),(10,'New Castle','Newcastle Stay','Affordable city comfort',120.00,'newcastle.jpg','Hotel Address, City, Country'),(11,'Norwich','Norwich Escape','Peaceful stay in Norwich',130.00,'norwich.jpg','Hotel Address, City, Country'),(12,'Nottingham','Nottingham Central','Modern city hotel',130.00,'nottingham.jpg','Hotel Address, City, Country'),(13,'Oxford','Oxford Heritage','Classic luxury in Oxford',180.00,'oxford.jpg','Hotel Address, City, Country'),(14,'Plymouth','Plymouth View','Sea-side luxury',180.00,'plymouth.jpg','Hotel Address, City, Country'),(15,'Swansea','Swansea Bay','Relax by the sea',130.00,'swansea.jpg','Hotel Address, City, Country'),(16,'Bournemouth','Bournemouth Resort','Beachside luxury',130.00,'bournemouth.jpg','Hotel Address, City, Country'),(17,'Kent','Kent Countryside','Calm & comfort',140.00,'kent.jpg','Hotel Address, City, Country'),(18,'London','plaza express','Balcony with proper view of hotel  with mini bar ',160.00,'default.jpg','london street 6'),(21,'London','yeti yak','balcony',130.00,'default.jpg','london');
/*!40000 ALTER TABLE `hotels` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room_amenities`
--

DROP TABLE IF EXISTS `room_amenities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room_amenities` (
  `amenity_id` int NOT NULL AUTO_INCREMENT,
  `room_type_id` int DEFAULT NULL,
  `amenity_name` varchar(100) DEFAULT NULL,
  `icon_class` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`amenity_id`),
  KEY `room_type_id` (`room_type_id`),
  CONSTRAINT `room_amenities_ibfk_1` FOREIGN KEY (`room_type_id`) REFERENCES `room_types` (`room_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_amenities`
--

LOCK TABLES `room_amenities` WRITE;
/*!40000 ALTER TABLE `room_amenities` DISABLE KEYS */;
/*!40000 ALTER TABLE `room_amenities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room_types`
--

DROP TABLE IF EXISTS `room_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room_types` (
  `room_type_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `capacity` int DEFAULT NULL,
  PRIMARY KEY (`room_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_types`
--

LOCK TABLES `room_types` WRITE;
/*!40000 ALTER TABLE `room_types` DISABLE KEYS */;
/*!40000 ALTER TABLE `room_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rooms`
--

DROP TABLE IF EXISTS `rooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rooms` (
  `room_id` int NOT NULL AUTO_INCREMENT,
  `hotel_id` int DEFAULT NULL,
  `room_number` varchar(10) DEFAULT NULL,
  `room_type` varchar(50) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `price_multiplier` decimal(3,2) DEFAULT '1.00',
  `features` text,
  `status` varchar(50) DEFAULT NULL,
  `capacity` int DEFAULT '1',
  `max_guests` int DEFAULT '1',
  PRIMARY KEY (`room_id`),
  UNIQUE KEY `room_number` (`room_number`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rooms`
--

LOCK TABLES `rooms` WRITE;
/*!40000 ALTER TABLE `rooms` DISABLE KEYS */;
INSERT INTO `rooms` VALUES (1,1,'101','Single',200.00,1.00,NULL,'available',1,1),(2,1,'102','Double',240.00,1.00,NULL,'available',2,1),(3,1,'103','Family',280.00,1.00,NULL,'available',4,1),(4,2,'201','Single',150.00,1.00,'Single bed, TV, WiFi, Desk','available',1,1),(5,2,'202','Double',190.00,1.20,'Double bed, TV, WiFi, Mini-fridge','available',2,2),(6,2,'203','Family',250.00,1.50,'Two double beds, TV, WiFi, Mini-fridge, Sofa','available',4,4),(7,2,'204','Single',145.00,1.00,'Single bed, TV, WiFi, Quiet area','available',1,1),(8,2,'205','Double',200.00,1.20,'Double bed, TV, WiFi, Mini-fridge, City view','available',2,2),(9,3,'301','Single',155.00,1.00,'Single bed, TV, WiFi, Castle view','available',1,1),(10,3,'302','Double',195.00,1.20,'Double bed, TV, WiFi, Mini-fridge, Castle view','available',2,2),(11,3,'303','Family',260.00,1.50,'Two double beds, TV, WiFi, Mini-fridge, Castle view','available',4,4),(12,3,'304','Single',300.00,1.80,'King bed, Living area, Premium castle view','available',2,2),(13,3,'305','Double',205.00,1.20,'Double bed, TV, WiFi, Mini-fridge, Executive','available',2,2),(14,4,'401','Single',140.00,1.00,'Single bed, TV, WiFi, City view','available',1,1),(15,4,'402','Double',180.00,1.20,'Double bed, TV, WiFi, Mini-fridge','available',2,2),(16,4,'403','Family',240.00,1.50,'Two double beds, TV, WiFi, Mini-fridge','available',4,4),(17,4,'404','Single',135.00,1.00,'Single bed, TV, WiFi, Standard','available',1,1),(18,5,'501','Single',145.00,1.00,'Single bed, TV, WiFi, Central location','available',1,1),(19,5,'502','Double',185.00,1.20,'Double bed, TV, WiFi, Mini-fridge, City centre','available',2,2),(20,5,'503','Family',245.00,1.50,'Two double beds, TV, WiFi, Mini-fridge','available',4,4),(21,5,'504','Single',140.00,1.00,'Single bed, TV, WiFi, Quiet room','booked',1,1),(22,5,'505','Double',190.00,1.20,'Double bed, TV, WiFi, Mini-fridge, Business','available',2,2),(23,6,'601','Single',135.00,1.00,'Single bed, TV, WiFi, Modern design','available',1,1),(24,6,'602','Double',175.00,1.20,'Double bed, TV, WiFi, Mini-fridge, Modern','available',2,2),(25,6,'603','Family',230.00,1.50,'Two double beds, TV, WiFi, Mini-fridge','available',4,4),(26,7,'701','Single',130.00,1.00,'Single bed, TV, WiFi, Comfortable','available',1,1),(27,7,'702','Double',170.00,1.20,'Double bed, TV, WiFi, Mini-fridge','available',2,2),(28,7,'703','Family',220.00,1.50,'Two double beds, TV, WiFi, Mini-fridge','available',4,4),(29,7,'704','Single',125.00,1.00,'Single bed, TV, WiFi, Standard','available',1,1),(30,8,'801','Single',140.00,1.00,'Single bed, TV, WiFi, Coastal view','available',1,1),(31,8,'802','Double',180.00,1.20,'Double bed, TV, WiFi, Mini-fridge, Coastal','available',2,2),(32,8,'803','Family',235.00,1.50,'Two double beds, TV, WiFi, Mini-fridge, Sea view','maintenance',4,4),(33,9,'901','Single',130.00,1.00,'Single bed, TV, WiFi, City centre','available',1,1),(34,9,'902','Double',170.00,1.20,'Double bed, TV, WiFi, Mini-fridge','available',2,2),(35,9,'903','Family',225.00,1.50,'Two double beds, TV, WiFi, Mini-fridge','available',4,4),(36,9,'904','Double',175.00,1.20,'Double bed, TV, WiFi, Mini-fridge, Premium','available',2,2),(37,10,'1001','Single',120.00,1.00,'Single bed, TV, WiFi, Affordable','available',1,1),(38,10,'1002','Double',160.00,1.20,'Double bed, TV, WiFi, Mini-fridge, Affordable','available',2,2),(39,10,'1003','Family',210.00,1.50,'Two double beds, TV, WiFi, Mini-fridge','available',4,4),(40,11,'1101','Single',130.00,1.00,'Single bed, TV, WiFi, Quiet location','available',1,1),(41,11,'1102','Double',170.00,1.20,'Double bed, TV, WiFi, Mini-fridge','available',2,2),(42,11,'1103','Family',225.00,1.50,'Two double beds, TV, WiFi, Mini-fridge','available',4,4),(43,11,'1104','Single',125.00,1.00,'Single bed, TV, WiFi, Garden view','available',1,1),(44,12,'1201','Single',130.00,1.00,'Single bed, TV, WiFi, Central','available',1,1),(45,12,'1202','Double',170.00,1.20,'Double bed, TV, WiFi, Mini-fridge','available',2,2),(46,12,'1203','Family',225.00,1.50,'Two double beds, TV, WiFi, Mini-fridge','available',4,4),(47,12,'1204','Single',125.00,1.00,'Single bed, TV, WiFi, Executive','available',1,1),(48,12,'1205','Suite',250.00,1.80,'King bed, Living area, Premium amenities','available',2,2),(49,13,'1301','Single',180.00,1.00,'Single bed, TV, WiFi, Historic area','available',1,1),(50,13,'1302','Double',220.00,1.20,'Double bed, TV, WiFi, Mini-fridge, Historic','available',2,2),(51,13,'1303','Family',290.00,1.50,'Two double beds, TV, WiFi, Mini-fridge','available',4,4),(52,13,'1304','Single',175.00,1.00,'Single bed, TV, WiFi, University view','available',1,1),(53,13,'1305','Suite',320.00,1.80,'King bed, Living area, Historic view','available',2,2),(54,14,'1401','Single',180.00,1.00,'Single bed, TV, WiFi, Sea view','available',1,1),(55,14,'1402','Double',220.00,1.20,'Double bed, TV, WiFi, Mini-fridge, Sea view','available',2,2),(56,14,'1403','Family',290.00,1.50,'Two double beds, TV, WiFi, Mini-fridge, Ocean view','available',4,4),(57,14,'1404','Double',225.00,1.20,'Double bed, TV, WiFi, Mini-fridge, Harbor view','available',2,2),(58,15,'1501','Single',130.00,1.00,'Single bed, TV, WiFi, Bay view','available',1,1),(59,15,'1502','Double',170.00,1.20,'Double bed, TV, WiFi, Mini-fridge, Bay view','available',2,2),(60,15,'1503','Family',225.00,1.50,'Two double beds, TV, WiFi, Mini-fridge, Sea front','available',4,4),(61,16,'1601','Single',130.00,1.00,'Single bed, TV, WiFi, Beach access','available',1,1),(62,16,'1602','Double',170.00,1.20,'Double bed, TV, WiFi, Mini-fridge, Beach','available',2,2),(63,16,'1603','Family',225.00,1.50,'Two double beds, TV, WiFi, Mini-fridge, Pool access','available',4,4),(64,16,'1604','Single',125.00,1.00,'Single bed, TV, WiFi, Garden view','available',1,1),(65,17,'1701','Single',140.00,1.00,'Single bed, TV, WiFi, Countryside','available',1,1),(66,17,'1702','Double',180.00,1.20,'Double bed, TV, WiFi, Mini-fridge, Countryside','available',2,2),(67,17,'1703','Family',240.00,1.50,'Two double beds, TV, WiFi, Mini-fridge, Garden view','available',4,4),(68,17,'1704','Single',135.00,1.00,'Single bed, TV, WiFi, Rural view','available',1,1),(69,17,'1705','Suite',260.00,1.80,'King bed, Living area, Countryside view','available',2,2),(70,18,'10183','Family',180.00,1.50,'Two double beds, TV, WiFi, Mini-fridge, Sofa, En-suite bathroom','available',4,4),(74,20,'200001','Single',136.00,1.00,'Single bed, TV, WiFi, En-suite bathroom','available',1,1),(75,20,'200002','Double',170.00,1.20,'Double bed, TV, WiFi, Mini-fridge, En-suite bathroom','available',2,2),(76,20,'200003','Family',204.00,1.50,'Two double beds, TV, WiFi, Mini-fridge, Sofa, En-suite bathroom','available',4,4),(77,21,'210001','Single',104.00,1.00,'Single bed, TV, WiFi, En-suite bathroom','available',4,4),(78,21,'210002','Double',130.00,1.20,'Double bed, TV, WiFi, Mini-fridge, En-suite bathroom','available',3,3),(79,21,'210003','Family',156.00,1.50,'Two double beds, TV, WiFi, Mini-fridge, Sofa, En-suite bathroom','available',4,4);
/*!40000 ALTER TABLE `rooms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `seasonal_pricing`
--

DROP TABLE IF EXISTS `seasonal_pricing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `seasonal_pricing` (
  `city_name` varchar(100) NOT NULL,
  `standard_price_peak` decimal(10,2) DEFAULT '100.00',
  `standard_price_offpeak` decimal(10,2) DEFAULT '70.00',
  `total_rooms` int DEFAULT '50',
  PRIMARY KEY (`city_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `seasonal_pricing`
--

LOCK TABLES `seasonal_pricing` WRITE;
/*!40000 ALTER TABLE `seasonal_pricing` DISABLE KEYS */;
/*!40000 ALTER TABLE `seasonal_pricing` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_login` timestamp NULL DEFAULT NULL,
  `role` varchar(10) DEFAULT 'user',
  `status` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'himani01','thehimaniacharya@gmail.com','scrypt:32768:8:1$CX6Bb9xh8vWDzKT7$7ae3e9a3df5b65aea07740b032cb5749c48a12959b229d674a00d892c3bc989b56af42ea0f7af3c4d278c12ac9e02ec4973ad3caebebb4f3129401144e757ce0','2026-01-16 14:35:00',NULL,'admin',1),(2,'acharya02','acharyahimani835@gmail.com','scrypt:32768:8:1$flSuliniQFPOdc7q$848e0ced705c9de8149188ec900affb9f6b1dc5aba4b04ef8008a3ac52e8c7bef8c252e473578ee28c22750eaf83c28440e7e03413353eb7f5c592113ead0e0a','2026-01-16 15:39:16',NULL,'user',1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-24 23:42:22
