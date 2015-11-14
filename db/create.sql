CREATE DATABASE `lsfstats` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE lsfstats;

CREATE TABLE `jobs` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `jobid` bigint(20) unsigned NOT NULL,
  `timestamp` int(10) unsigned DEFAULT NULL,
  `user` varchar(255) DEFAULT NULL,
  `submit_time` int(10) unsigned DEFAULT NULL,
  `start_time` int(10) unsigned DEFAULT NULL,
  `end_time` int(10) unsigned DEFAULT NULL,
  `run_time` int(10) DEFAULT NULL,
  `exit_status` int(10) DEFAULT NULL,
  `cputime` int(25) unsigned DEFAULT NULL,
  `status` int(10) DEFAULT NULL,
  `resreq` varchar(255) DEFAULT NULL,
  `project_name` varchar(255) DEFAULT NULL,
  `queue` varchar(255) DEFAULT NULL,
  `mem` int(25) DEFAULT NULL,
  `mem_reservation` int(25) DEFAULT NULL,
  `mem_avg` int(25) DEFAULT NULL,
  `mem_max` int(25) DEFAULT NULL,
  `cores` int(25) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `timestamp` (`timestamp`),
  KEY `jobid` (`jobid`),
  KEY `user` (`user`),
  KEY `status` (`status`),
  KEY `timestamp_user` (`user`,`timestamp`) USING BTREE,
  KEY `timestamp_user_status` (`timestamp`,`user`,`status`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

CREATE TABLE `jobs_small` (
  `id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `jobid` bigint(20) unsigned NOT NULL,
  `timestamp` int(10) unsigned DEFAULT NULL,
  `user` varchar(255) DEFAULT NULL,
  `submit_time` int(10) unsigned DEFAULT NULL,
  `start_time` int(10) unsigned DEFAULT NULL,
  `end_time` int(10) unsigned DEFAULT NULL,
  `run_time` int(10) DEFAULT NULL,
  `exit_status` int(10) DEFAULT NULL,
  `cputime` int(25) unsigned DEFAULT NULL,
  `status` int(10) DEFAULT NULL,
  `resreq` varchar(255) DEFAULT NULL,
  `project_name` varchar(255) DEFAULT NULL,
  `queue` varchar(255) DEFAULT NULL,
  `mem` int(25) DEFAULT NULL,
  `mem_reservation` int(25) DEFAULT NULL,
  `mem_avg` int(25) DEFAULT NULL,
  `mem_max` int(25) DEFAULT NULL,
  `cores` int(25) DEFAULT NULL,
  KEY `timestamp_user` (`timestamp`,`user`),
  KEY `timestamp` (`timestamp`),
  KEY `user` (`user`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `namedictionary` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `shortname` varchar(200) DEFAULT NULL,
  `longname` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`id`),
  UNIQUE KEY `shortname_UNIQUE` (`shortname`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

CREATE TABLE `summary` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `timestamp` int(10) unsigned NOT NULL,
  `mem` int(25) unsigned NOT NULL,
  `mem_reservation` int(25) NOT NULL DEFAULT '0',
  `mem_max` int(25) unsigned NOT NULL,
  `mem_avg` int(25) unsigned NOT NULL,
  `cores` int(25) unsigned NOT NULL,
  `pending_jobs` int(25) unsigned NOT NULL,
  `running_jobs` int(25) unsigned NOT NULL,
  `total_jobs` int(25) unsigned NOT NULL,
  `pending_time_avg` int(25) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

