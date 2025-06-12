-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 12, 2025 at 04:29 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.1.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_inventraa`
--

-- --------------------------------------------------------

--
-- Table structure for table `tb_admin`
--

CREATE TABLE `tb_admin` (
  `id_admin` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(30) NOT NULL,
  `status` enum('admin') NOT NULL DEFAULT 'admin',
  `foto_profil` varchar(255) DEFAULT '/static/img/logoinventra.png'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_admin`
--

INSERT INTO `tb_admin` (`id_admin`, `username`, `password`, `status`, `foto_profil`) VALUES
(1, 'Ketua', 'ketua12345', 'admin', '/static/img/logoinventra.png');

-- --------------------------------------------------------

--
-- Table structure for table `tb_brgkeluar`
--

CREATE TABLE `tb_brgkeluar` (
  `id_brgkeluar` int(11) NOT NULL,
  `id_barang` int(11) NOT NULL,
  `kode_barang` varchar(20) NOT NULL,
  `nama_barang` varchar(100) NOT NULL,
  `tgl_keluar` date NOT NULL,
  `jumlah_barang` int(11) NOT NULL,
  `tujuan` varchar(100) NOT NULL,
  `status` enum('dalam perjalanan','segera tiba','terdistribusi') NOT NULL DEFAULT 'dalam perjalanan',
  `id_reseller` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_brgkeluar`
--

INSERT INTO `tb_brgkeluar` (`id_brgkeluar`, `id_barang`, `kode_barang`, `nama_barang`, `tgl_keluar`, `jumlah_barang`, `tujuan`, `status`, `id_reseller`) VALUES
(1, 1, 'kps01', 'kipas miyako gantung', '2025-05-24', 12, 'sini', 'dalam perjalanan', 3);

-- --------------------------------------------------------

--
-- Table structure for table `tb_brgmasuk`
--

CREATE TABLE `tb_brgmasuk` (
  `id_barang` int(11) NOT NULL,
  `kode_barang` varchar(20) NOT NULL,
  `nama_barang` varchar(100) NOT NULL,
  `tgl_masuk` date NOT NULL,
  `jumlah_barang` int(11) NOT NULL,
  `id_supplier` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_brgmasuk`
--

INSERT INTO `tb_brgmasuk` (`id_barang`, `kode_barang`, `nama_barang`, `tgl_masuk`, `jumlah_barang`, `id_supplier`) VALUES
(1, 'kps01', 'kipas miyako gantung', '2025-04-30', 3, 1),
(2, 'kps02', 'kipas angin x2', '2025-04-27', 35, 2),
(18, 'kopikop', 'akjn ajaas', '2025-05-25', 65, 18),
(21, 'gauuutyfd', 'njmhj', '2025-02-01', 12, 21),
(25, 'kps23345', 'kipas scx', '2025-05-25', 11, 25),
(26, 'kp122112', 'tess dulu lah', '2025-06-04', 34, 26);

-- --------------------------------------------------------

--
-- Table structure for table `tb_manajer`
--

CREATE TABLE `tb_manajer` (
  `id_manajer` int(11) NOT NULL,
  `nama_manajer` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tb_reseller`
--

CREATE TABLE `tb_reseller` (
  `id_reseller` int(11) NOT NULL,
  `nama_toko` varchar(50) NOT NULL,
  `nama_pemilik` varchar(50) NOT NULL,
  `alamat` text NOT NULL,
  `no_telp` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_reseller`
--

INSERT INTO `tb_reseller` (`id_reseller`, `nama_toko`, `nama_pemilik`, `alamat`, `no_telp`) VALUES
(1, 'toko electro jaya', 'poni', 'beringin', '089872651621'),
(2, 'toko electro jaya', 'jonoo', 'jalan sini', '089909877654'),
(3, 'sksnk', 'jokooo', 'beringin', '087667776543');

-- --------------------------------------------------------

--
-- Table structure for table `tb_supplier`
--

CREATE TABLE `tb_supplier` (
  `id_supplier` int(11) NOT NULL,
  `nama_supplier` varchar(50) NOT NULL,
  `alamat` text NOT NULL,
  `no_telp` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_supplier`
--

INSERT INTO `tb_supplier` (`id_supplier`, `nama_supplier`, `alamat`, `no_telp`) VALUES
(1, 'jono', 'tanjung', '089777662312'),
(2, 'joni', 'pakam', '082132122290'),
(3, 'kojo', 'sintis', '081213141516'),
(4, 'asji', 'sini', '089972344651'),
(5, 'qwerfd', 'skdni', '088211122451'),
(6, 'sjbd', 'sdkh', '087665444569'),
(7, 'sdssd', 'sdc', '082122211890'),
(8, 'sds', 'sds', '12133313133'),
(9, 'sdoudso', 'alsd', '08917826851'),
(10, 'dffv', 'fvdf', '08999766565'),
(11, 'ada', 'dfdf', '0877652112'),
(12, 'aposa', 'asask', '087712768881'),
(13, 'spdkp', 'sccc', '089767890091'),
(14, 'opoo', 'sdskd', '082289748373'),
(15, 'knd', 'assd', '08771213839'),
(16, 'odjo', 'sdsd', '085234466521'),
(17, 'osjoi', 'bdsb', '087665542221'),
(18, 'sodikin aja lahh', 'pakam aja sini', '082234512131'),
(19, 'gj', 'skn', '0811223524'),
(20, 'dbg', 'fb', '0875654534234'),
(21, 'fgf', 'fvf', '088667675665'),
(22, 'gffg', 'fgh', '123112233333'),
(23, 'kajii', 'skns', '089787665121'),
(24, 'qopo', 'skncsk', '081321111290'),
(25, 'alkam', 'aspkap', '089889001221'),
(26, 'sapiki', 'askloj', '081213141519');

-- --------------------------------------------------------

--
-- Table structure for table `tb_user`
--

CREATE TABLE `tb_user` (
  `id_user` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(30) NOT NULL,
  `status` enum('user') NOT NULL DEFAULT 'user',
  `dibuat_oleh` int(11) NOT NULL,
  `foto_profil` varchar(255) DEFAULT '/static/img/logoinventra.png'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_user`
--

INSERT INTO `tb_user` (`id_user`, `username`, `password`, `status`, `dibuat_oleh`, `foto_profil`) VALUES
(3, 'Refin', 'refin12345', 'user', 1, '/static/img/profile_38071420d8844f568c5483a364db5135_ic_apple.png.jpg'),
(4, 'Ridho', 'ridho12345', 'user', 1, '/static/img/logoinventra.png');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tb_admin`
--
ALTER TABLE `tb_admin`
  ADD PRIMARY KEY (`id_admin`);

--
-- Indexes for table `tb_brgkeluar`
--
ALTER TABLE `tb_brgkeluar`
  ADD PRIMARY KEY (`id_brgkeluar`),
  ADD KEY `id_barang` (`id_barang`),
  ADD KEY `kode_barang` (`kode_barang`),
  ADD KEY `fk_reseller` (`id_reseller`);

--
-- Indexes for table `tb_brgmasuk`
--
ALTER TABLE `tb_brgmasuk`
  ADD PRIMARY KEY (`id_barang`),
  ADD UNIQUE KEY `kode_barang` (`kode_barang`),
  ADD KEY `id_supplier` (`id_supplier`);

--
-- Indexes for table `tb_manajer`
--
ALTER TABLE `tb_manajer`
  ADD PRIMARY KEY (`id_manajer`);

--
-- Indexes for table `tb_reseller`
--
ALTER TABLE `tb_reseller`
  ADD PRIMARY KEY (`id_reseller`);

--
-- Indexes for table `tb_supplier`
--
ALTER TABLE `tb_supplier`
  ADD PRIMARY KEY (`id_supplier`);

--
-- Indexes for table `tb_user`
--
ALTER TABLE `tb_user`
  ADD PRIMARY KEY (`id_user`),
  ADD KEY `dibuat_oleh` (`dibuat_oleh`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tb_admin`
--
ALTER TABLE `tb_admin`
  MODIFY `id_admin` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `tb_brgkeluar`
--
ALTER TABLE `tb_brgkeluar`
  MODIFY `id_brgkeluar` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `tb_brgmasuk`
--
ALTER TABLE `tb_brgmasuk`
  MODIFY `id_barang` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `tb_manajer`
--
ALTER TABLE `tb_manajer`
  MODIFY `id_manajer` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tb_reseller`
--
ALTER TABLE `tb_reseller`
  MODIFY `id_reseller` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `tb_supplier`
--
ALTER TABLE `tb_supplier`
  MODIFY `id_supplier` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `tb_user`
--
ALTER TABLE `tb_user`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tb_brgkeluar`
--
ALTER TABLE `tb_brgkeluar`
  ADD CONSTRAINT `fk_reseller` FOREIGN KEY (`id_reseller`) REFERENCES `tb_reseller` (`id_reseller`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `tb_brgkeluar_ibfk_1` FOREIGN KEY (`id_barang`) REFERENCES `tb_brgmasuk` (`id_barang`) ON UPDATE CASCADE,
  ADD CONSTRAINT `tb_brgkeluar_ibfk_2` FOREIGN KEY (`kode_barang`) REFERENCES `tb_brgmasuk` (`kode_barang`) ON UPDATE CASCADE;

--
-- Constraints for table `tb_brgmasuk`
--
ALTER TABLE `tb_brgmasuk`
  ADD CONSTRAINT `tb_brgmasuk_ibfk_1` FOREIGN KEY (`id_supplier`) REFERENCES `tb_supplier` (`id_supplier`) ON UPDATE CASCADE;

--
-- Constraints for table `tb_user`
--
ALTER TABLE `tb_user`
  ADD CONSTRAINT `tb_user_ibfk_1` FOREIGN KEY (`dibuat_oleh`) REFERENCES `tb_admin` (`id_admin`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
