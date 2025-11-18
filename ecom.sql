-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 18, 2025 at 01:33 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ecom`
--

-- --------------------------------------------------------

--
-- Table structure for table `authtoken_token`
--

CREATE TABLE `authtoken_token` (
  `key` varchar(40) NOT NULL,
  `created` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add content type', 4, 'add_contenttype'),
(14, 'Can change content type', 4, 'change_contenttype'),
(15, 'Can delete content type', 4, 'delete_contenttype'),
(16, 'Can view content type', 4, 'view_contenttype'),
(17, 'Can add session', 5, 'add_session'),
(18, 'Can change session', 5, 'change_session'),
(19, 'Can delete session', 5, 'delete_session'),
(20, 'Can view session', 5, 'view_session'),
(21, 'Can add Token', 6, 'add_token'),
(22, 'Can change Token', 6, 'change_token'),
(23, 'Can delete Token', 6, 'delete_token'),
(24, 'Can view Token', 6, 'view_token'),
(25, 'Can add Token', 7, 'add_tokenproxy'),
(26, 'Can change Token', 7, 'change_tokenproxy'),
(27, 'Can delete Token', 7, 'delete_tokenproxy'),
(28, 'Can view Token', 7, 'view_tokenproxy'),
(29, 'Can add color', 8, 'add_color'),
(30, 'Can change color', 8, 'change_color'),
(31, 'Can delete color', 8, 'delete_color'),
(32, 'Can view color', 8, 'view_color'),
(33, 'Can add contact_us', 9, 'add_contact_us'),
(34, 'Can change contact_us', 9, 'change_contact_us'),
(35, 'Can delete contact_us', 9, 'delete_contact_us'),
(36, 'Can view contact_us', 9, 'view_contact_us'),
(37, 'Can add country', 10, 'add_country'),
(38, 'Can change country', 10, 'change_country'),
(39, 'Can delete country', 10, 'delete_country'),
(40, 'Can view country', 10, 'view_country'),
(41, 'Can add faq', 11, 'add_faq'),
(42, 'Can change faq', 11, 'change_faq'),
(43, 'Can delete faq', 11, 'delete_faq'),
(44, 'Can view faq', 11, 'view_faq'),
(45, 'Can add otp save', 12, 'add_otpsave'),
(46, 'Can change otp save', 12, 'change_otpsave'),
(47, 'Can delete otp save', 12, 'delete_otpsave'),
(48, 'Can view otp save', 12, 'view_otpsave'),
(49, 'Can add product_category', 13, 'add_product_category'),
(50, 'Can change product_category', 13, 'change_product_category'),
(51, 'Can delete product_category', 13, 'delete_product_category'),
(52, 'Can view product_category', 13, 'view_product_category'),
(53, 'Can add role', 14, 'add_role'),
(54, 'Can change role', 14, 'change_role'),
(55, 'Can delete role', 14, 'delete_role'),
(56, 'Can view role', 14, 'view_role'),
(57, 'Can add size', 15, 'add_size'),
(58, 'Can change size', 15, 'change_size'),
(59, 'Can delete size', 15, 'delete_size'),
(60, 'Can view size', 15, 'view_size'),
(61, 'Can add system settings', 16, 'add_systemsettings'),
(62, 'Can change system settings', 16, 'change_systemsettings'),
(63, 'Can delete system settings', 16, 'delete_systemsettings'),
(64, 'Can view system settings', 16, 'view_systemsettings'),
(65, 'Can add user gender', 17, 'add_usergender'),
(66, 'Can change user gender', 17, 'change_usergender'),
(67, 'Can delete user gender', 17, 'delete_usergender'),
(68, 'Can view user gender', 17, 'view_usergender'),
(69, 'Can add product', 18, 'add_product'),
(70, 'Can change product', 18, 'change_product'),
(71, 'Can delete product', 18, 'delete_product'),
(72, 'Can view product', 18, 'view_product'),
(73, 'Can add product_variant', 19, 'add_product_variant'),
(74, 'Can change product_variant', 19, 'change_product_variant'),
(75, 'Can delete product_variant', 19, 'delete_product_variant'),
(76, 'Can view product_variant', 19, 'view_product_variant'),
(77, 'Can add product_image', 20, 'add_product_image'),
(78, 'Can change product_image', 20, 'change_product_image'),
(79, 'Can delete product_image', 20, 'delete_product_image'),
(80, 'Can view product_image', 20, 'view_product_image'),
(81, 'Can add state', 21, 'add_state'),
(82, 'Can change state', 21, 'change_state'),
(83, 'Can delete state', 21, 'delete_state'),
(84, 'Can view state', 21, 'view_state'),
(85, 'Can add city', 22, 'add_city'),
(86, 'Can change city', 22, 'change_city'),
(87, 'Can delete city', 22, 'delete_city'),
(88, 'Can view city', 22, 'view_city'),
(89, 'Can add user', 23, 'add_user'),
(90, 'Can change user', 23, 'change_user'),
(91, 'Can delete user', 23, 'delete_user'),
(92, 'Can view user', 23, 'view_user'),
(93, 'Can add customer_review', 24, 'add_customer_review'),
(94, 'Can change customer_review', 24, 'change_customer_review'),
(95, 'Can delete customer_review', 24, 'delete_customer_review'),
(96, 'Can view customer_review', 24, 'view_customer_review'),
(97, 'Can add cart', 25, 'add_cart'),
(98, 'Can change cart', 25, 'change_cart'),
(99, 'Can delete cart', 25, 'delete_cart'),
(100, 'Can view cart', 25, 'view_cart'),
(101, 'Can add wishlist', 26, 'add_wishlist'),
(102, 'Can change wishlist', 26, 'change_wishlist'),
(103, 'Can delete wishlist', 26, 'delete_wishlist'),
(104, 'Can view wishlist', 26, 'view_wishlist'),
(105, 'Can add Blacklisted Token', 27, 'add_blacklistedtoken'),
(106, 'Can change Blacklisted Token', 27, 'change_blacklistedtoken'),
(107, 'Can delete Blacklisted Token', 27, 'delete_blacklistedtoken'),
(108, 'Can view Blacklisted Token', 27, 'view_blacklistedtoken'),
(109, 'Can add Outstanding Token', 28, 'add_outstandingtoken'),
(110, 'Can change Outstanding Token', 28, 'change_outstandingtoken'),
(111, 'Can delete Outstanding Token', 28, 'delete_outstandingtoken'),
(112, 'Can view Outstanding Token', 28, 'view_outstandingtoken');

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(6, 'authtoken', 'token'),
(7, 'authtoken', 'tokenproxy'),
(4, 'contenttypes', 'contenttype'),
(25, 'reward_admin', 'cart'),
(22, 'reward_admin', 'city'),
(8, 'reward_admin', 'color'),
(9, 'reward_admin', 'contact_us'),
(10, 'reward_admin', 'country'),
(24, 'reward_admin', 'customer_review'),
(11, 'reward_admin', 'faq'),
(12, 'reward_admin', 'otpsave'),
(18, 'reward_admin', 'product'),
(13, 'reward_admin', 'product_category'),
(20, 'reward_admin', 'product_image'),
(19, 'reward_admin', 'product_variant'),
(14, 'reward_admin', 'role'),
(15, 'reward_admin', 'size'),
(21, 'reward_admin', 'state'),
(16, 'reward_admin', 'systemsettings'),
(23, 'reward_admin', 'user'),
(17, 'reward_admin', 'usergender'),
(26, 'reward_admin', 'wishlist'),
(5, 'sessions', 'session'),
(27, 'token_blacklist', 'blacklistedtoken'),
(28, 'token_blacklist', 'outstandingtoken');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2025-11-18 12:13:48.791831'),
(2, 'contenttypes', '0002_remove_content_type_name', '2025-11-18 12:13:48.863809'),
(3, 'auth', '0001_initial', '2025-11-18 12:13:49.131897'),
(4, 'auth', '0002_alter_permission_name_max_length', '2025-11-18 12:13:49.202233'),
(5, 'auth', '0003_alter_user_email_max_length', '2025-11-18 12:13:49.212681'),
(6, 'auth', '0004_alter_user_username_opts', '2025-11-18 12:13:49.217745'),
(7, 'auth', '0005_alter_user_last_login_null', '2025-11-18 12:13:49.225217'),
(8, 'auth', '0006_require_contenttypes_0002', '2025-11-18 12:13:49.228386'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2025-11-18 12:13:49.235707'),
(10, 'auth', '0008_alter_user_username_max_length', '2025-11-18 12:13:49.243889'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2025-11-18 12:13:49.248896'),
(12, 'auth', '0010_alter_group_name_max_length', '2025-11-18 12:13:49.262645'),
(13, 'auth', '0011_update_proxy_permissions', '2025-11-18 12:13:49.265450'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2025-11-18 12:13:49.280925'),
(15, 'reward_admin', '0001_initial', '2025-11-18 12:13:51.150795'),
(16, 'admin', '0001_initial', '2025-11-18 12:13:51.371483'),
(17, 'admin', '0002_logentry_remove_auto_add', '2025-11-18 12:13:51.387284'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2025-11-18 12:13:51.415542'),
(19, 'authtoken', '0001_initial', '2025-11-18 12:13:51.523456'),
(20, 'authtoken', '0002_auto_20160226_1747', '2025-11-18 12:13:51.603535'),
(21, 'authtoken', '0003_tokenproxy', '2025-11-18 12:13:51.605919'),
(22, 'authtoken', '0004_alter_tokenproxy_options', '2025-11-18 12:13:51.614491'),
(23, 'sessions', '0001_initial', '2025-11-18 12:13:51.649101'),
(24, 'token_blacklist', '0001_initial', '2025-11-18 12:13:51.842030'),
(25, 'token_blacklist', '0002_outstandingtoken_jti_hex', '2025-11-18 12:13:51.920671'),
(26, 'token_blacklist', '0003_auto_20171017_2007', '2025-11-18 12:13:51.945526'),
(27, 'token_blacklist', '0004_auto_20171017_2013', '2025-11-18 12:13:52.016609'),
(28, 'token_blacklist', '0005_remove_outstandingtoken_jti', '2025-11-18 12:13:52.044723'),
(29, 'token_blacklist', '0006_auto_20171017_2113', '2025-11-18 12:13:52.070043'),
(30, 'token_blacklist', '0007_auto_20171017_2214', '2025-11-18 12:13:54.211155'),
(31, 'token_blacklist', '0008_migrate_to_bigautofield', '2025-11-18 12:13:54.664928'),
(32, 'token_blacklist', '0010_fix_migrate_to_bigautofield', '2025-11-18 12:13:54.697372'),
(33, 'token_blacklist', '0011_linearizes_history', '2025-11-18 12:13:54.700733'),
(34, 'token_blacklist', '0012_alter_outstandingtoken_user', '2025-11-18 12:13:54.727314'),
(35, 'token_blacklist', '0013_alter_blacklistedtoken_options_and_more', '2025-11-18 12:13:54.758592');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('jyifibronkxeupl7gnothpomiquuuhao', '.eJxVjDsOwjAQBe_iGln-xR9Kes5g7cYbYkA2ihMJhLg7BKWA9s28ebIIyzzGpdEUc2J7Jtnud0PoL1RWkM5QTpX3tcxTRr4qfKONH2ui62Fz_wIjtPHz9nrw1inUgKRCsAmtN-Q9SXA9DBaDQSulNtSJDo2zGgMY2TnjhVfmG23UWq4l0v2WpwfbSyWCFeL1Bu2TP5Y:1vLKgX:N3NU_Hlc6dJLMt0XwRq9Ji1wD_t8LfORmUiAM9eDrFA', '2025-12-02 12:19:49.416623');

-- --------------------------------------------------------

--
-- Table structure for table `e_com_cart`
--

CREATE TABLE `e_com_cart` (
  `id` bigint(20) NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `customer_id` bigint(20) NOT NULL,
  `product_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `e_com_cart`
--

INSERT INTO `e_com_cart` (`id`, `created_at`, `updated_at`, `customer_id`, `product_id`) VALUES
(1, '2025-11-18 12:28:10.722315', '2025-11-18 12:28:10.722315', 2, 6);

-- --------------------------------------------------------

--
-- Table structure for table `e_com_city`
--

CREATE TABLE `e_com_city` (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `status` tinyint(1) NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `state_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `e_com_color`
--

CREATE TABLE `e_com_color` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `hex_code` varchar(7) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `status` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `e_com_color`
--

INSERT INTO `e_com_color` (`id`, `name`, `hex_code`, `created_at`, `updated_at`, `status`) VALUES
(1, 'RED', '#ff0000', '2025-11-18 06:31:07.195640', '2025-11-18 06:31:07.195640', 1);

-- --------------------------------------------------------

--
-- Table structure for table `e_com_contact_us`
--

CREATE TABLE `e_com_contact_us` (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `subject` varchar(255) DEFAULT NULL,
  `message` longtext DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `e_com_contact_us`
--

INSERT INTO `e_com_contact_us` (`id`, `name`, `email`, `subject`, `message`, `created_at`, `updated_at`) VALUES
(1, '5y', '5y', '5y', '5y', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `e_com_country`
--

CREATE TABLE `e_com_country` (
  `id` bigint(20) NOT NULL,
  `code` varchar(2) NOT NULL,
  `name` varchar(100) NOT NULL,
  `flag` varchar(100) DEFAULT NULL,
  `zone_id` int(11) NOT NULL,
  `country_code` int(11) DEFAULT NULL,
  `status` tinyint(1) NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `e_com_country`
--

INSERT INTO `e_com_country` (`id`, `code`, `name`, `flag`, `zone_id`, `country_code`, `status`, `created_at`, `updated_at`) VALUES
(1, 'IN', 'India', '', 91, 91, 1, '2025-11-17 05:05:13.759574', '2025-11-17 05:05:13.759574');

-- --------------------------------------------------------

--
-- Table structure for table `e_com_customer_review`
--

CREATE TABLE `e_com_customer_review` (
  `id` bigint(20) NOT NULL,
  `rating` int(11) DEFAULT NULL,
  `review` longtext DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `customer_id` bigint(20) NOT NULL,
  `product_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `e_com_faq`
--

CREATE TABLE `e_com_faq` (
  `id` bigint(20) NOT NULL,
  `question` longtext DEFAULT NULL,
  `answer` longtext DEFAULT NULL,
  `date_created` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `e_com_faq`
--

INSERT INTO `e_com_faq` (`id`, `question`, `answer`, `date_created`, `created_at`, `updated_at`) VALUES
(2, 'What are your shipping options?', 'We offer standard shipping (5-7 business days) and express shipping (2-3 business days). Prime members get free standard shipping on all orders.', '2025-11-18 17:53:04.000000', '2025-11-18 17:53:04.000000', '2025-11-18 17:53:04.000000'),
(3, 'What is your return policy?', 'We offer a 30-day return policy for all unused items in their original packaging. Simply contact our customer service team to initiate a return.', '2025-11-18 17:53:04.000000', '2025-11-18 17:53:04.000000', '2025-11-18 17:53:04.000000'),
(4, 'Are all products genuine and original?', 'Yes, all our products are 100% genuine and sourced directly from authorized manufacturers and distributors. We guarantee authenticity on every item.', '2025-11-18 17:53:04.000000', '2025-11-18 17:53:04.000000', '2025-11-18 17:53:04.000000'),
(5, 'Do you offer international shipping?', 'Currently, we only ship within India. We are working on expanding our shipping services to international locations in the near future.', '2025-11-18 17:53:04.000000', '2025-11-18 17:53:04.000000', '2025-11-18 17:53:04.000000'),
(6, 'How can I track my order?', 'Once your order is shipped, you will receive a tracking number via email and SMS. You can use this number to track your order on our website or the courier\'s website.', '2025-11-18 17:53:04.000000', '2025-11-18 17:53:04.000000', '2025-11-18 17:53:04.000000'),
(7, 'Do you offer bulk or wholesale pricing?', 'Yes, we offer special pricing for bulk orders. Please contact our sales team at sales@kitchivo.com for more information about wholesale opportunities.', '2025-11-18 17:53:04.000000', '2025-11-18 17:53:04.000000', '2025-11-18 17:53:04.000000');

-- --------------------------------------------------------

--
-- Table structure for table `e_com_gender`
--

CREATE TABLE `e_com_gender` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `e_com_gender`
--

INSERT INTO `e_com_gender` (`id`, `name`, `created_at`, `updated_at`) VALUES
(1, 'Male', NULL, NULL),
(2, 'Female', NULL, NULL),
(3, 'Others', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `e_com_otpsave`
--

CREATE TABLE `e_com_otpsave` (
  `id` int(11) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `OTP` int(11) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `e_com_product`
--

CREATE TABLE `e_com_product` (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `description` longtext DEFAULT NULL,
  `MRP` decimal(10,2) DEFAULT NULL,
  `sale_price` decimal(10,2) DEFAULT NULL,
  `price_in_dolor` decimal(10,2) DEFAULT NULL,
  `sale_price_in_dollar` decimal(10,2) DEFAULT NULL,
  `status` tinyint(1) NOT NULL,
  `url` varchar(200) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `category_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `e_com_product`
--

INSERT INTO `e_com_product` (`id`, `name`, `description`, `MRP`, `sale_price`, `price_in_dolor`, `sale_price_in_dollar`, `status`, `url`, `created_at`, `updated_at`, `category_id`) VALUES
(6, 'Memory Foam Pillow', 'Memory Foam Pillows Neck Pillow for Sleeping, Ergonomic Contour Cervical Pillow Neck Support Bed Pillow for Side Back Stomach Sleeper, Orthopedic Pillow for Neck Pain Relief', 1999.00, 389.00, 40.00, 35.53, 1, 'https://amzn.in/d/id09A27', '2025-11-18 09:57:21.969926', '2025-11-18 12:20:10.550431', 2);

-- --------------------------------------------------------

--
-- Table structure for table `e_com_product_category`
--

CREATE TABLE `e_com_product_category` (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `image` varchar(100) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `status` tinyint(1) NOT NULL,
  `updated_at` datetime(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `e_com_product_category`
--

INSERT INTO `e_com_product_category` (`id`, `name`, `image`, `created_at`, `status`, `updated_at`) VALUES
(1, 'Kitchen', 'category_images\\category_1_CyzdGD9HaM.jpg', '2025-11-17 10:16:47.838186', 1, '2025-11-18 09:50:59.954389'),
(2, 'Home Decor', 'category_images\\category_2_3q45AYDxqZ.jpg', '2025-11-18 09:51:15.872187', 1, '2025-11-18 09:51:15.872187'),
(3, 'Cleaning', 'category_images\\category_3_Toi0NVHZBy.jpg', '2025-11-18 09:51:39.423667', 1, '2025-11-18 09:51:39.433314'),
(4, 'Storage', 'category_images\\category_4_P0cTyTbZuw.jpg', '2025-11-18 09:51:51.026739', 1, '2025-11-18 09:51:51.039205'),
(5, 'Cookware', 'category_images\\category_5_E8OCYbbymv.jpg', '2025-11-18 09:52:05.963405', 1, '2025-11-18 09:52:05.971043'),
(6, 'Dining', 'category_images\\category_6_q7U3LYGBDP.jpg', '2025-11-18 09:52:31.655379', 1, '2025-11-18 09:52:31.655379'),
(7, 'Appliances', 'category_images\\category_7_eClRnQBK75.jpg', '2025-11-18 09:53:29.591636', 1, '2025-11-18 09:53:29.591636'),
(8, 'Bathroom', 'category_images\\category_8_qFl3dg2HL6.jpg', '2025-11-18 09:53:40.629143', 1, '2025-11-18 09:53:40.631148');

-- --------------------------------------------------------

--
-- Table structure for table `e_com_product_image`
--

CREATE TABLE `e_com_product_image` (
  `id` bigint(20) NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `is_primary` tinyint(1) NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `product_id` bigint(20) NOT NULL,
  `variant_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `e_com_product_image`
--

INSERT INTO `e_com_product_image` (`id`, `image`, `is_primary`, `created_at`, `updated_at`, `product_id`, `variant_id`) VALUES
(12, 'product_images\\product_6_0ZjZMlBC8f.jpg', 0, '2025-11-18 09:57:21.974862', '2025-11-18 09:57:21.974862', 6, NULL),
(13, 'product_images\\product_6_lujaslJYzj.jpg', 0, '2025-11-18 09:57:21.976796', '2025-11-18 09:57:21.976796', 6, NULL),
(14, 'product_images\\product_6_SdIIBBGAM9.jpg', 0, '2025-11-18 09:57:21.984361', '2025-11-18 09:57:21.984361', 6, NULL),
(15, 'product_images\\product_6_4HAqWfDYsR.jpg', 0, '2025-11-18 09:57:21.987199', '2025-11-18 09:57:21.987199', 6, NULL),
(16, 'product_images\\product_6_toatQp11HJ.jpg', 0, '2025-11-18 09:57:21.989396', '2025-11-18 09:57:21.989396', 6, NULL),
(17, 'product_images\\product_6_TcOuOEjKjS.jpg', 0, '2025-11-18 09:57:21.989396', '2025-11-18 09:57:21.989396', 6, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `e_com_product_variant`
--

CREATE TABLE `e_com_product_variant` (
  `id` bigint(20) NOT NULL,
  `stock_quantity` int(11) DEFAULT NULL,
  `sku` varchar(100) DEFAULT NULL,
  `status` tinyint(1) NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `color_id` bigint(20) DEFAULT NULL,
  `product_id` bigint(20) NOT NULL,
  `size_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `e_com_role`
--

CREATE TABLE `e_com_role` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `e_com_role`
--

INSERT INTO `e_com_role` (`id`, `name`, `created_at`, `updated_at`) VALUES
(1, 'Super Admin', NULL, NULL),
(2, 'Customer', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `e_com_size`
--

CREATE TABLE `e_com_size` (
  `id` bigint(20) NOT NULL,
  `name` varchar(50) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `status` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `e_com_size`
--

INSERT INTO `e_com_size` (`id`, `name`, `created_at`, `updated_at`, `status`) VALUES
(1, 'S', '2025-11-18 11:58:11.000000', '2025-11-18 11:58:11.000000', 1),
(2, 'M', '2025-11-18 11:58:11.000000', '2025-11-18 11:58:11.000000', 1),
(3, 'L', '2025-11-18 11:58:39.000000', '2025-11-18 11:58:39.000000', 1),
(4, 'XL', '2025-11-18 11:58:39.000000', '2025-11-18 06:30:34.849011', 1);

-- --------------------------------------------------------

--
-- Table structure for table `e_com_state`
--

CREATE TABLE `e_com_state` (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `status` tinyint(1) NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `country_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `e_com_state`
--

INSERT INTO `e_com_state` (`id`, `name`, `status`, `created_at`, `updated_at`, `country_id`) VALUES
(1, 'Gujrat', 1, '2025-11-17 09:09:49.678980', '2025-11-17 09:09:49.678980', 1);

-- --------------------------------------------------------

--
-- Table structure for table `e_com_systemsettings`
--

CREATE TABLE `e_com_systemsettings` (
  `id` bigint(20) NOT NULL,
  `website_name` varchar(255) DEFAULT NULL,
  `fav_icon` varchar(255) DEFAULT NULL,
  `website_logo` varchar(255) DEFAULT NULL,
  `phone` longtext NOT NULL,
  `email` longtext DEFAULT NULL,
  `address` longtext DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `e_com_systemsettings`
--

INSERT INTO `e_com_systemsettings` (`id`, `website_name`, `fav_icon`, `website_logo`, `phone`, `email`, `address`, `created_at`, `updated_at`) VALUES
(1, 'E Com', 'system_settings/fav_icon_w2Qx5jwv.png', 'system_settings/website_logo_wDiqvlUd.png', '+91 8745147896', 'ecom@gmail.com', 'Vadodara', '2025-11-17 08:32:16.984143', '2025-11-18 07:29:04.166472');

-- --------------------------------------------------------

--
-- Table structure for table `e_com_user`
--

CREATE TABLE `e_com_user` (
  `id` bigint(20) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `username` varchar(150) NOT NULL,
  `profile_picture` varchar(100) DEFAULT NULL,
  `card_header` varchar(100) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `address` longtext DEFAULT NULL,
  `pincode` varchar(10) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `phone` varchar(20) NOT NULL,
  `name` varchar(150) DEFAULT NULL,
  `otp` int(11) DEFAULT NULL,
  `otp_created_at` datetime(6) DEFAULT NULL,
  `device_type` int(11) DEFAULT NULL,
  `device_token` varchar(255) DEFAULT NULL,
  `register_type` varchar(10) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `remember_token` varchar(255) DEFAULT NULL,
  `email_verified_at` datetime(6) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `country_id` bigint(20) DEFAULT NULL,
  `role_id` bigint(20) DEFAULT NULL,
  `state_id` bigint(20) DEFAULT NULL,
  `gender_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `e_com_user`
--

INSERT INTO `e_com_user` (`id`, `last_login`, `is_superuser`, `first_name`, `last_name`, `username`, `profile_picture`, `card_header`, `date_of_birth`, `address`, `pincode`, `email`, `phone`, `name`, `otp`, `otp_created_at`, `device_type`, `device_token`, `register_type`, `password`, `remember_token`, `email_verified_at`, `is_active`, `is_staff`, `created_at`, `updated_at`, `country_id`, `role_id`, `state_id`, `gender_id`) VALUES
(1, '2025-11-18 12:19:49.413438', 1, 'Kitchivo', 'Kitchivo', 'Super Admin', '', '', '2002-12-13', 'Vadodara', '390001', 'Kitchivo@support.com', '9874563210', 'Kitchivo', 842139, '2025-11-17 09:19:59.157138', 0, NULL, NULL, 'pbkdf2_sha256$720000$ZRf3JMrVr3OZxBUu1O2ioO$We6vp6iPFJyw9ezRkxr/k97vB06+t4OsyCApMXSz558=', NULL, NULL, 1, 1, '2025-11-17 04:57:00.395131', '2025-11-18 09:33:53.627146', 1, 1, 1, 1),
(2, '2025-11-18 12:29:42.732660', 0, 'Devansh', 'Shah', 'ds', 'profile_pics/2_5g8DAVzB.webp', '', '1998-12-25', '18 Mansarovar Complex, Vadodara', '390024', 'ds@yopmail.com', '9712573541', 'Devansh Shah', NULL, NULL, 0, NULL, 'Mobile App', 'pbkdf2_sha256$720000$jBXVKdAJxWdHSQklSYarPA$DLdAtKlVImns4e9eOOCmuWO3EgtO+FZphJ/Pdu/CqR4=', NULL, NULL, 1, 0, '2025-11-18 06:48:22.825567', '2025-11-18 12:29:42.733807', 1, 2, 1, 1);

-- --------------------------------------------------------

--
-- Table structure for table `e_com_user_cities`
--

CREATE TABLE `e_com_user_cities` (
  `id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `city_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `e_com_user_groups`
--

CREATE TABLE `e_com_user_groups` (
  `id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `e_com_user_user_permissions`
--

CREATE TABLE `e_com_user_user_permissions` (
  `id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `e_com_wishlist`
--

CREATE TABLE `e_com_wishlist` (
  `id` bigint(20) NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `customer_id` bigint(20) NOT NULL,
  `product_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `e_com_wishlist`
--

INSERT INTO `e_com_wishlist` (`id`, `created_at`, `updated_at`, `customer_id`, `product_id`) VALUES
(1, '2025-11-18 12:28:26.228900', '2025-11-18 12:28:26.228900', 2, 6);

-- --------------------------------------------------------

--
-- Table structure for table `token_blacklist_blacklistedtoken`
--

CREATE TABLE `token_blacklist_blacklistedtoken` (
  `id` bigint(20) NOT NULL,
  `blacklisted_at` datetime(6) NOT NULL,
  `token_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `token_blacklist_outstandingtoken`
--

CREATE TABLE `token_blacklist_outstandingtoken` (
  `id` bigint(20) NOT NULL,
  `token` longtext NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) NOT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  `jti` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `token_blacklist_outstandingtoken`
--

INSERT INTO `token_blacklist_outstandingtoken` (`id`, `token`, `created_at`, `expires_at`, `user_id`, `jti`) VALUES
(1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5NTAwNDc3OCwiaWF0IjoxNzYzNDY4Nzc4LCJqdGkiOiI2N2U5OTEzZDMzY2Y0OGI2ODE2YmI1ZTJhOTQzYWE3MCIsInVzZXJfaWQiOiIyIn0.sZdxrafTl0-bM9ZsEolPPOpMop3c5UzkS0oBDk4STwQ', '2025-11-18 12:26:18.229952', '2026-11-18 12:26:18.000000', 2, '67e9913d33cf48b6816bb5e2a943aa70'),
(2, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5NTAwNDg2NywiaWF0IjoxNzYzNDY4ODY3LCJqdGkiOiI0MTY0YzQxNDZhNjU0YWE3YTdhYjg0YjQxMzUwYzY3ZiIsInVzZXJfaWQiOiIyIn0.sjQnf18wTiP2011XGoky3D6SeUnOEJr2yWPgPN6b3uM', '2025-11-18 12:27:47.080793', '2026-11-18 12:27:47.000000', 2, '4164c4146a654aa7a7ab84b41350c67f'),
(3, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5NTAwNDkwOSwiaWF0IjoxNzYzNDY4OTA5LCJqdGkiOiIxMjBmYjcyNTdlMTI0ZGNmYTNkN2M3MjFmNDVmY2M2YSIsInVzZXJfaWQiOiIyIn0.awG6EWIL6w25RTHqy3DwzmCd_7Rc5cya9Vp_ALY_ZZ0', '2025-11-18 12:28:29.882050', '2026-11-18 12:28:29.000000', 2, '120fb7257e124dcfa3d7c721f45fcc6a'),
(4, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5NTAwNDk4MiwiaWF0IjoxNzYzNDY4OTgyLCJqdGkiOiIwYWEzMzY3ZTIxNDI0MTU1ODMwODc2MTJlZmY4ZDE3MiIsInVzZXJfaWQiOiIyIn0.DkB3jvJgXaRWupx9JdFcsfEU5cNi6MkigOBB1xBr-0M', '2025-11-18 12:29:42.736865', '2026-11-18 12:29:42.000000', 2, '0aa3367e2142415583087612eff8d172');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `authtoken_token`
--
ALTER TABLE `authtoken_token`
  ADD PRIMARY KEY (`key`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Indexes for table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indexes for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_e_com_user_id` (`user_id`);

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indexes for table `e_com_cart`
--
ALTER TABLE `e_com_cart`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `e_com_cart_customer_id_product_id_c6ef04b2_uniq` (`customer_id`,`product_id`),
  ADD KEY `e_com_cart_product_id_b52177f0_fk_e_com_product_id` (`product_id`);

--
-- Indexes for table `e_com_city`
--
ALTER TABLE `e_com_city`
  ADD PRIMARY KEY (`id`),
  ADD KEY `e_com_city_state_id_72051dd3_fk_e_com_state_id` (`state_id`);

--
-- Indexes for table `e_com_color`
--
ALTER TABLE `e_com_color`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `e_com_contact_us`
--
ALTER TABLE `e_com_contact_us`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `e_com_country`
--
ALTER TABLE `e_com_country`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `e_com_customer_review`
--
ALTER TABLE `e_com_customer_review`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `e_com_customer_review_product_id_customer_id_a7a9fe0d_uniq` (`product_id`,`customer_id`),
  ADD KEY `e_com_customer_review_customer_id_b4237677_fk_e_com_user_id` (`customer_id`);

--
-- Indexes for table `e_com_faq`
--
ALTER TABLE `e_com_faq`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `e_com_gender`
--
ALTER TABLE `e_com_gender`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `e_com_otpsave`
--
ALTER TABLE `e_com_otpsave`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `e_com_product`
--
ALTER TABLE `e_com_product`
  ADD PRIMARY KEY (`id`),
  ADD KEY `e_com_product_category_id_06864900_fk_e_com_product_category_id` (`category_id`);

--
-- Indexes for table `e_com_product_category`
--
ALTER TABLE `e_com_product_category`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `e_com_product_image`
--
ALTER TABLE `e_com_product_image`
  ADD PRIMARY KEY (`id`),
  ADD KEY `e_com_product_image_product_id_0350b31a_fk_e_com_product_id` (`product_id`),
  ADD KEY `e_com_product_image_variant_id_d771b293_fk_e_com_pro` (`variant_id`);

--
-- Indexes for table `e_com_product_variant`
--
ALTER TABLE `e_com_product_variant`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `sku` (`sku`),
  ADD UNIQUE KEY `e_com_product_variant_product_id_size_id_color_id_59ea3735_uniq` (`product_id`,`size_id`,`color_id`),
  ADD KEY `e_com_product_variant_color_id_372b8e88_fk_e_com_color_id` (`color_id`),
  ADD KEY `e_com_product_variant_size_id_bae2758a_fk_e_com_size_id` (`size_id`);

--
-- Indexes for table `e_com_role`
--
ALTER TABLE `e_com_role`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `e_com_size`
--
ALTER TABLE `e_com_size`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `e_com_state`
--
ALTER TABLE `e_com_state`
  ADD PRIMARY KEY (`id`),
  ADD KEY `e_com_state_country_id_3bfb3297_fk_e_com_country_id` (`country_id`);

--
-- Indexes for table `e_com_systemsettings`
--
ALTER TABLE `e_com_systemsettings`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `e_com_user`
--
ALTER TABLE `e_com_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `e_com_user_country_id_08d5a05a_fk_e_com_country_id` (`country_id`),
  ADD KEY `e_com_user_role_id_318e22b5_fk_e_com_role_id` (`role_id`),
  ADD KEY `e_com_user_state_id_b0684a78_fk_e_com_state_id` (`state_id`),
  ADD KEY `e_com_user_gender_id_36ab2d27_fk_e_com_gender_id` (`gender_id`);

--
-- Indexes for table `e_com_user_cities`
--
ALTER TABLE `e_com_user_cities`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `e_com_user_cities_user_id_city_id_afddc9d7_uniq` (`user_id`,`city_id`),
  ADD KEY `e_com_user_cities_city_id_2452c10b_fk_e_com_city_id` (`city_id`);

--
-- Indexes for table `e_com_user_groups`
--
ALTER TABLE `e_com_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `e_com_user_groups_user_id_group_id_79cbf832_uniq` (`user_id`,`group_id`),
  ADD KEY `e_com_user_groups_group_id_2cdb74d0_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `e_com_user_user_permissions`
--
ALTER TABLE `e_com_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `e_com_user_user_permissions_user_id_permission_id_5653854e_uniq` (`user_id`,`permission_id`),
  ADD KEY `e_com_user_user_perm_permission_id_e384e346_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `e_com_wishlist`
--
ALTER TABLE `e_com_wishlist`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `e_com_wishlist_customer_id_product_id_fcdd392c_uniq` (`customer_id`,`product_id`),
  ADD KEY `e_com_wishlist_product_id_57f1b0d2_fk_e_com_product_id` (`product_id`);

--
-- Indexes for table `token_blacklist_blacklistedtoken`
--
ALTER TABLE `token_blacklist_blacklistedtoken`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `token_id` (`token_id`);

--
-- Indexes for table `token_blacklist_outstandingtoken`
--
ALTER TABLE `token_blacklist_outstandingtoken`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq` (`jti`),
  ADD KEY `token_blacklist_outs_user_id_83bc629a_fk_e_com_use` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=113;

--
-- AUTO_INCREMENT for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;

--
-- AUTO_INCREMENT for table `e_com_cart`
--
ALTER TABLE `e_com_cart`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `e_com_city`
--
ALTER TABLE `e_com_city`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `e_com_color`
--
ALTER TABLE `e_com_color`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `e_com_contact_us`
--
ALTER TABLE `e_com_contact_us`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `e_com_country`
--
ALTER TABLE `e_com_country`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `e_com_customer_review`
--
ALTER TABLE `e_com_customer_review`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `e_com_faq`
--
ALTER TABLE `e_com_faq`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `e_com_gender`
--
ALTER TABLE `e_com_gender`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `e_com_otpsave`
--
ALTER TABLE `e_com_otpsave`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `e_com_product`
--
ALTER TABLE `e_com_product`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `e_com_product_category`
--
ALTER TABLE `e_com_product_category`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `e_com_product_image`
--
ALTER TABLE `e_com_product_image`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `e_com_product_variant`
--
ALTER TABLE `e_com_product_variant`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `e_com_role`
--
ALTER TABLE `e_com_role`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `e_com_size`
--
ALTER TABLE `e_com_size`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `e_com_state`
--
ALTER TABLE `e_com_state`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `e_com_systemsettings`
--
ALTER TABLE `e_com_systemsettings`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `e_com_user`
--
ALTER TABLE `e_com_user`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `e_com_user_cities`
--
ALTER TABLE `e_com_user_cities`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `e_com_user_groups`
--
ALTER TABLE `e_com_user_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `e_com_user_user_permissions`
--
ALTER TABLE `e_com_user_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `e_com_wishlist`
--
ALTER TABLE `e_com_wishlist`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `token_blacklist_blacklistedtoken`
--
ALTER TABLE `token_blacklist_blacklistedtoken`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `token_blacklist_outstandingtoken`
--
ALTER TABLE `token_blacklist_outstandingtoken`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `authtoken_token`
--
ALTER TABLE `authtoken_token`
  ADD CONSTRAINT `authtoken_token_user_id_35299eff_fk_e_com_user_id` FOREIGN KEY (`user_id`) REFERENCES `e_com_user` (`id`);

--
-- Constraints for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Constraints for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_e_com_user_id` FOREIGN KEY (`user_id`) REFERENCES `e_com_user` (`id`);

--
-- Constraints for table `e_com_cart`
--
ALTER TABLE `e_com_cart`
  ADD CONSTRAINT `e_com_cart_customer_id_91926251_fk_e_com_user_id` FOREIGN KEY (`customer_id`) REFERENCES `e_com_user` (`id`),
  ADD CONSTRAINT `e_com_cart_product_id_b52177f0_fk_e_com_product_id` FOREIGN KEY (`product_id`) REFERENCES `e_com_product` (`id`);

--
-- Constraints for table `e_com_city`
--
ALTER TABLE `e_com_city`
  ADD CONSTRAINT `e_com_city_state_id_72051dd3_fk_e_com_state_id` FOREIGN KEY (`state_id`) REFERENCES `e_com_state` (`id`);

--
-- Constraints for table `e_com_customer_review`
--
ALTER TABLE `e_com_customer_review`
  ADD CONSTRAINT `e_com_customer_review_customer_id_b4237677_fk_e_com_user_id` FOREIGN KEY (`customer_id`) REFERENCES `e_com_user` (`id`),
  ADD CONSTRAINT `e_com_customer_review_product_id_fa9682fc_fk_e_com_product_id` FOREIGN KEY (`product_id`) REFERENCES `e_com_product` (`id`);

--
-- Constraints for table `e_com_product`
--
ALTER TABLE `e_com_product`
  ADD CONSTRAINT `e_com_product_category_id_06864900_fk_e_com_product_category_id` FOREIGN KEY (`category_id`) REFERENCES `e_com_product_category` (`id`);

--
-- Constraints for table `e_com_product_image`
--
ALTER TABLE `e_com_product_image`
  ADD CONSTRAINT `e_com_product_image_product_id_0350b31a_fk_e_com_product_id` FOREIGN KEY (`product_id`) REFERENCES `e_com_product` (`id`),
  ADD CONSTRAINT `e_com_product_image_variant_id_d771b293_fk_e_com_pro` FOREIGN KEY (`variant_id`) REFERENCES `e_com_product_variant` (`id`);

--
-- Constraints for table `e_com_product_variant`
--
ALTER TABLE `e_com_product_variant`
  ADD CONSTRAINT `e_com_product_variant_color_id_372b8e88_fk_e_com_color_id` FOREIGN KEY (`color_id`) REFERENCES `e_com_color` (`id`),
  ADD CONSTRAINT `e_com_product_variant_product_id_4fa49291_fk_e_com_product_id` FOREIGN KEY (`product_id`) REFERENCES `e_com_product` (`id`),
  ADD CONSTRAINT `e_com_product_variant_size_id_bae2758a_fk_e_com_size_id` FOREIGN KEY (`size_id`) REFERENCES `e_com_size` (`id`);

--
-- Constraints for table `e_com_state`
--
ALTER TABLE `e_com_state`
  ADD CONSTRAINT `e_com_state_country_id_3bfb3297_fk_e_com_country_id` FOREIGN KEY (`country_id`) REFERENCES `e_com_country` (`id`);

--
-- Constraints for table `e_com_user`
--
ALTER TABLE `e_com_user`
  ADD CONSTRAINT `e_com_user_country_id_08d5a05a_fk_e_com_country_id` FOREIGN KEY (`country_id`) REFERENCES `e_com_country` (`id`),
  ADD CONSTRAINT `e_com_user_gender_id_36ab2d27_fk_e_com_gender_id` FOREIGN KEY (`gender_id`) REFERENCES `e_com_gender` (`id`),
  ADD CONSTRAINT `e_com_user_role_id_318e22b5_fk_e_com_role_id` FOREIGN KEY (`role_id`) REFERENCES `e_com_role` (`id`),
  ADD CONSTRAINT `e_com_user_state_id_b0684a78_fk_e_com_state_id` FOREIGN KEY (`state_id`) REFERENCES `e_com_state` (`id`);

--
-- Constraints for table `e_com_user_cities`
--
ALTER TABLE `e_com_user_cities`
  ADD CONSTRAINT `e_com_user_cities_city_id_2452c10b_fk_e_com_city_id` FOREIGN KEY (`city_id`) REFERENCES `e_com_city` (`id`),
  ADD CONSTRAINT `e_com_user_cities_user_id_ac5d7264_fk_e_com_user_id` FOREIGN KEY (`user_id`) REFERENCES `e_com_user` (`id`);

--
-- Constraints for table `e_com_user_groups`
--
ALTER TABLE `e_com_user_groups`
  ADD CONSTRAINT `e_com_user_groups_group_id_2cdb74d0_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `e_com_user_groups_user_id_1b44c4f4_fk_e_com_user_id` FOREIGN KEY (`user_id`) REFERENCES `e_com_user` (`id`);

--
-- Constraints for table `e_com_user_user_permissions`
--
ALTER TABLE `e_com_user_user_permissions`
  ADD CONSTRAINT `e_com_user_user_perm_permission_id_e384e346_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `e_com_user_user_permissions_user_id_f6212fec_fk_e_com_user_id` FOREIGN KEY (`user_id`) REFERENCES `e_com_user` (`id`);

--
-- Constraints for table `e_com_wishlist`
--
ALTER TABLE `e_com_wishlist`
  ADD CONSTRAINT `e_com_wishlist_customer_id_a0a7db25_fk_e_com_user_id` FOREIGN KEY (`customer_id`) REFERENCES `e_com_user` (`id`),
  ADD CONSTRAINT `e_com_wishlist_product_id_57f1b0d2_fk_e_com_product_id` FOREIGN KEY (`product_id`) REFERENCES `e_com_product` (`id`);

--
-- Constraints for table `token_blacklist_blacklistedtoken`
--
ALTER TABLE `token_blacklist_blacklistedtoken`
  ADD CONSTRAINT `token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk` FOREIGN KEY (`token_id`) REFERENCES `token_blacklist_outstandingtoken` (`id`);

--
-- Constraints for table `token_blacklist_outstandingtoken`
--
ALTER TABLE `token_blacklist_outstandingtoken`
  ADD CONSTRAINT `token_blacklist_outs_user_id_83bc629a_fk_e_com_use` FOREIGN KEY (`user_id`) REFERENCES `e_com_user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
